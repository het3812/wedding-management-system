"""
Vendor Blueprint - Vendor registration, login, dashboard, service management
Separate from admin - vendors have their own login page and dashboard
"""
import secrets
from pathlib import Path
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session
from werkzeug.utils import secure_filename

from db import execute_query, execute_update
from config import VENDOR_UPLOAD_FOLDER, ALLOWED_EXTENSIONS

vendor_bp = Blueprint('vendor', __name__, url_prefix='/vendor')


def vendor_required(f):
    """Decorator: require vendor role"""
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.', 'warning')
            return redirect(url_for('vendor.login'))
        user = execute_query("SELECT role FROM users WHERE id = %s", (session['user_id'],), fetch_one=True)
        if not user or user['role'] != 'vendor':
            flash('Vendor access only.', 'danger')
            return redirect(url_for('vendor.login'))
        vendor = execute_query("SELECT * FROM vendors WHERE user_id = %s", (session['user_id'],), fetch_one=True)
        if not vendor:
            flash('Vendor profile not found.', 'danger')
            return redirect(url_for('vendor.login'))
        g.current_vendor = vendor
        g.current_user_id = session['user_id']
        return f(*args, **kwargs)
    return wrapped


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@vendor_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Vendor login - separate from admin login"""
    if request.method == 'GET':
        if 'user_id' in session:
            user = execute_query("SELECT role FROM users WHERE id = %s", (session['user_id'],), fetch_one=True)
            if user and user['role'] == 'vendor':
                return redirect(url_for('vendor.dashboard'))
        return render_template('vendor_login.html')

    from werkzeug.security import check_password_hash

    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    if not email or not password:
        flash('Email and password required.', 'danger')
        return render_template('vendor_login.html')

    user = execute_query(
        "SELECT id, name, email, password, role FROM users WHERE email = %s",
        (email,),
        fetch_one=True
    )

    if not user or user['role'] != 'vendor':
        flash('Invalid credentials or not a vendor account.', 'danger')
        return render_template('vendor_login.html')

    if not check_password_hash(user['password'], password):
        flash('Invalid credentials.', 'danger')
        return render_template('vendor_login.html')

    session.clear()
    session['user_id'] = user['id']
    session['user_role'] = 'vendor'
    flash(f'Welcome, {user["name"]}!', 'success')
    return redirect(url_for('vendor.dashboard'))


@vendor_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Vendor registration: name, service type, contact"""
    if request.method == 'GET':
        return render_template('vendor_register.html')

    from werkzeug.security import generate_password_hash

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    business_name = request.form.get('business_name', '').strip()
    service_type = request.form.get('service_type', '').strip()
    contact_email = request.form.get('contact_email', '').strip().lower()
    contact_phone = request.form.get('contact_phone', '').strip()

    if not all([name, email, password, business_name, service_type, contact_email]):
        flash('All fields except phone are required.', 'danger')
        return render_template('vendor_register.html')

    if len(password) < 6:
        flash('Password must be at least 6 characters.', 'danger')
        return render_template('vendor_register.html')

    existing = execute_query("SELECT id FROM users WHERE email = %s", (email,), fetch_one=True)
    if existing:
        flash('Email already registered.', 'danger')
        return render_template('vendor_register.html')

    hashed = generate_password_hash(password)
    user_id = execute_update(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'vendor')",
        (name, email, hashed)
    )

    execute_update(
        """INSERT INTO vendors (user_id, business_name, service_type, contact_email, contact_phone, is_approved)
           VALUES (%s, %s, %s, %s, %s, FALSE)""",
        (user_id, business_name, service_type, contact_email, contact_phone or None)
    )

    flash('Registration successful! Please login. Admin will approve your account.', 'success')
    return redirect(url_for('vendor.login'))


@vendor_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))


@vendor_bp.route('/')
@vendor_required
def dashboard():
    """Vendor dashboard: list services, profile info, bookings, stats"""
    services = execute_query(
        "SELECT * FROM vendor_services WHERE vendor_id = %s ORDER BY created_at DESC",
        (g.current_vendor['id'],)
    )
    
    # Get bookings
    bookings = execute_query("""
        SELECT vb.*, u.name as customer_name, u.email as customer_email
        FROM vendor_bookings vb
        JOIN users u ON vb.user_id = u.id
        WHERE vb.vendor_id = %s
        ORDER BY vb.created_at DESC
        LIMIT 10
    """, (g.current_vendor['id'],))
    
    # Get stats
    stats = execute_query("""
        SELECT 
            COUNT(*) as total_bookings,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_bookings,
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending_bookings
        FROM vendor_bookings
        WHERE vendor_id = %s
    """, (g.current_vendor['id'],), fetch_one=True)
    
    # Get unread chats count
    unread_chats = execute_query("""
        SELECT COUNT(*) as count
        FROM vendor_chats
        WHERE vendor_id = %s AND unread_vendor > 0
    """, (g.current_vendor['id'],), fetch_one=True)
    
    return render_template('vendor_dashboard.html', 
                         vendor=g.current_vendor, 
                         services=services,
                         bookings=bookings,
                         stats=stats,
                         unread_chats=unread_chats['count'])


@vendor_bp.route('/services/add', methods=['GET', 'POST'])
@vendor_required
def add_service():
    """Add vendor service: title, description, price, image"""
    if request.method == 'GET':
        return render_template('vendor_service_form.html', service=None)

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    price = request.form.get('price', '').strip()
    price_val = float(price) if price and price.replace('.', '').replace('-', '').isdigit() else None

    if not title:
        flash('Service title is required.', 'danger')
        return render_template('vendor_service_form.html', service=None)

    image_path = None
    if 'image' in request.files and request.files['image'].filename:
        file = request.files['image']
        if allowed_file(file.filename):
            VENDOR_UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            vendor_dir = VENDOR_UPLOAD_FOLDER / str(g.current_vendor['id'])
            vendor_dir.mkdir(parents=True, exist_ok=True)
            fn = secure_filename(file.filename)
            unique = f"{secrets.token_hex(4)}_{fn}"
            filepath = vendor_dir / unique
            file.save(str(filepath))
            image_path = f"uploads/vendors/{g.current_vendor['id']}/{unique}"

    execute_update(
        """INSERT INTO vendor_services (vendor_id, title, description, price, image_path)
           VALUES (%s, %s, %s, %s, %s)""",
        (g.current_vendor['id'], title, description or None, price_val, image_path)
    )
    flash('Service added.', 'success')
    return redirect(url_for('vendor.dashboard'))


@vendor_bp.route('/services/<int:svc_id>/edit', methods=['GET', 'POST'])
@vendor_required
def edit_service(svc_id):
    """Edit own service only"""
    svc = execute_query(
        "SELECT * FROM vendor_services WHERE id = %s AND vendor_id = %s",
        (svc_id, g.current_vendor['id']),
        fetch_one=True
    )
    if not svc:
        flash('Service not found.', 'danger')
        return redirect(url_for('vendor.dashboard'))

    if request.method == 'GET':
        return render_template('vendor_service_form.html', service=svc)

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    price = request.form.get('price', '').strip()
    price_val = float(price) if price and price.replace('.', '').replace('-', '').isdigit() else None

    if not title:
        flash('Service title is required.', 'danger')
        return render_template('vendor_service_form.html', service=svc)

    image_path = svc['image_path']
    if 'image' in request.files and request.files['image'].filename:
        file = request.files['image']
        if allowed_file(file.filename):
            VENDOR_UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            vendor_dir = VENDOR_UPLOAD_FOLDER / str(g.current_vendor['id'])
            vendor_dir.mkdir(parents=True, exist_ok=True)
            fn = secure_filename(file.filename)
            unique = f"{secrets.token_hex(4)}_{fn}"
            filepath = vendor_dir / unique
            file.save(str(filepath))
            image_path = f"uploads/vendors/{g.current_vendor['id']}/{unique}"

    execute_update(
        """UPDATE vendor_services SET title=%s, description=%s, price=%s, image_path=%s WHERE id=%s AND vendor_id=%s""",
        (title, description or None, price_val, image_path, svc_id, g.current_vendor['id'])
    )
    flash('Service updated.', 'success')
    return redirect(url_for('vendor.dashboard'))


@vendor_bp.route('/services/<int:svc_id>/delete')
@vendor_required
def delete_service(svc_id):
    """Delete own service only"""
    svc = execute_query(
        "SELECT image_path FROM vendor_services WHERE id = %s AND vendor_id = %s",
        (svc_id, g.current_vendor['id']),
        fetch_one=True
    )
    if svc:
        if svc['image_path']:
            from flask import current_app
            p = Path(current_app.root_path) / 'static' / svc['image_path']
            if p.exists():
                p.unlink(missing_ok=True)
        execute_update("DELETE FROM vendor_services WHERE id = %s AND vendor_id = %s", (svc_id, g.current_vendor['id']))
        flash('Service deleted.', 'info')
    return redirect(url_for('vendor.dashboard'))



@vendor_bp.route('/profile/edit', methods=['GET', 'POST'])
@vendor_required
def edit_profile():
    """Edit vendor profile: contact, location, social links"""
    if request.method == 'GET':
        return render_template('vendor_profile_form.html', vendor=g.current_vendor)
    
    # Update profile
    business_name = request.form.get('business_name', '').strip()
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()
    contact_email = request.form.get('contact_email', '').strip()
    contact_phone = request.form.get('contact_phone', '').strip()
    website_url = request.form.get('website_url', '').strip()
    instagram_url = request.form.get('instagram_url', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    area = request.form.get('area', '').strip()
    
    if not all([business_name, category, contact_email]):
        flash('Business name, category, and contact email are required.', 'danger')
        return render_template('vendor_profile_form.html', vendor=g.current_vendor)
    
    execute_update("""
        UPDATE vendors 
        SET business_name = %s, category = %s, description = %s,
            contact_email = %s, contact_phone = %s,
            website_url = %s, instagram_url = %s,
            city = %s, state = %s, area = %s
        WHERE id = %s
    """, (business_name, category, description, contact_email, contact_phone,
          website_url, instagram_url, city, state, area, g.current_vendor['id']))
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('vendor.dashboard'))


@vendor_bp.route('/payment-settings', methods=['GET', 'POST'])
@vendor_required
def payment_settings():
    """Manage payment settings and UPI QR code"""
    if request.method == 'GET':
        return render_template('vendor_payment_settings.html', vendor=g.current_vendor)
    
    # Update payment settings
    upi_id = request.form.get('upi_id', '').strip()
    bank_account_name = request.form.get('bank_account_name', '').strip()
    bank_account_number = request.form.get('bank_account_number', '').strip()
    bank_ifsc_code = request.form.get('bank_ifsc_code', '').strip()
    bank_name = request.form.get('bank_name', '').strip()
    accepts_online_payment = request.form.get('accepts_online_payment') == 'on'
    payment_terms = request.form.get('payment_terms', '').strip()
    
    # Handle UPI QR code upload
    upi_qr_code = g.current_vendor.get('upi_qr_code')
    if 'upi_qr_code' in request.files and request.files['upi_qr_code'].filename:
        file = request.files['upi_qr_code']
        if allowed_file(file.filename):
            VENDOR_UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            vendor_dir = VENDOR_UPLOAD_FOLDER / str(g.current_vendor['id']) / 'payment'
            vendor_dir.mkdir(parents=True, exist_ok=True)
            
            fn = secure_filename(file.filename)
            unique = f"upi_qr_{secrets.token_hex(4)}_{fn}"
            filepath = vendor_dir / unique
            file.save(str(filepath))
            upi_qr_code = f"uploads/vendors/{g.current_vendor['id']}/payment/{unique}"
            
            # Delete old QR code if exists
            if g.current_vendor.get('upi_qr_code'):
                from flask import current_app
                old_path = Path(current_app.root_path) / 'static' / g.current_vendor['upi_qr_code']
                if old_path.exists():
                    old_path.unlink(missing_ok=True)
    
    # Update database
    execute_update("""
        UPDATE vendors 
        SET upi_id = %s, upi_qr_code = %s,
            bank_account_name = %s, bank_account_number = %s,
            bank_ifsc_code = %s, bank_name = %s,
            accepts_online_payment = %s, payment_terms = %s
        WHERE id = %s
    """, (upi_id, upi_qr_code, bank_account_name, bank_account_number,
          bank_ifsc_code, bank_name, accepts_online_payment, payment_terms,
          g.current_vendor['id']))
    
    flash('Payment settings updated successfully!', 'success')
    return redirect(url_for('vendor.payment_settings'))


@vendor_bp.route('/payment-settings/delete-qr', methods=['POST'])
@vendor_required
def delete_upi_qr():
    """Delete UPI QR code"""
    if g.current_vendor.get('upi_qr_code'):
        from flask import current_app
        qr_path = Path(current_app.root_path) / 'static' / g.current_vendor['upi_qr_code']
        if qr_path.exists():
            qr_path.unlink(missing_ok=True)
        
        execute_update(
            "UPDATE vendors SET upi_qr_code = NULL WHERE id = %s",
            (g.current_vendor['id'],)
        )
        flash('UPI QR code deleted.', 'info')
    
    return redirect(url_for('vendor.payment_settings'))


@vendor_bp.route('/gallery')
@vendor_required
def gallery():
    """View vendor gallery"""
    images = execute_query(
        "SELECT * FROM vendor_gallery WHERE vendor_id = %s ORDER BY display_order, uploaded_at DESC",
        (g.current_vendor['id'],)
    )
    return render_template('vendor_gallery.html', vendor=g.current_vendor, images=images)


@vendor_bp.route('/gallery/upload', methods=['POST'])
@vendor_required
def upload_gallery_image():
    """Upload image to gallery"""
    if 'image' not in request.files:
        flash('No image selected.', 'warning')
        return redirect(url_for('vendor.gallery'))
    
    file = request.files['image']
    caption = request.form.get('caption', '').strip()
    
    if file and file.filename and allowed_file(file.filename):
        VENDOR_UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        vendor_dir = VENDOR_UPLOAD_FOLDER / str(g.current_vendor['id']) / 'gallery'
        vendor_dir.mkdir(parents=True, exist_ok=True)
        
        fn = secure_filename(file.filename)
        unique = f"{secrets.token_hex(4)}_{fn}"
        filepath = vendor_dir / unique
        file.save(str(filepath))
        image_path = f"uploads/vendors/{g.current_vendor['id']}/gallery/{unique}"
        
        execute_update("""
            INSERT INTO vendor_gallery (vendor_id, image_path, caption)
            VALUES (%s, %s, %s)
        """, (g.current_vendor['id'], image_path, caption))
        
        flash('Image uploaded successfully!', 'success')
    else:
        flash('Invalid file type. Allowed: png, jpg, jpeg, gif, webp', 'danger')
    
    return redirect(url_for('vendor.gallery'))


@vendor_bp.route('/gallery/<int:img_id>/delete')
@vendor_required
def delete_gallery_image(img_id):
    """Delete gallery image"""
    img = execute_query(
        "SELECT image_path FROM vendor_gallery WHERE id = %s AND vendor_id = %s",
        (img_id, g.current_vendor['id']),
        fetch_one=True
    )
    
    if img:
        from flask import current_app
        p = Path(current_app.root_path) / 'static' / img['image_path']
        if p.exists():
            p.unlink(missing_ok=True)
        execute_update(
            "DELETE FROM vendor_gallery WHERE id = %s AND vendor_id = %s",
            (img_id, g.current_vendor['id'])
        )
        flash('Image deleted.', 'info')
    
    return redirect(url_for('vendor.gallery'))


@vendor_bp.route('/bookings')
@vendor_required
def bookings():
    """View all bookings"""
    bookings = execute_query("""
        SELECT vb.*, u.name as customer_name, u.email as customer_email, u.id as customer_user_id,
               vs.title as service_title
        FROM vendor_bookings vb
        JOIN users u ON vb.user_id = u.id
        LEFT JOIN vendor_services vs ON vb.service_id = vs.id
        WHERE vb.vendor_id = %s
        ORDER BY vb.created_at DESC
    """, (g.current_vendor['id'],))
    
    return render_template('vendor_bookings.html', vendor=g.current_vendor, bookings=bookings)


@vendor_bp.route('/bookings/<int:booking_id>/update-status', methods=['POST'])
@vendor_required
def update_booking_status(booking_id):
    """Update booking status"""
    status = request.form.get('status')
    
    if status not in ['Pending', 'Confirmed', 'Completed', 'Cancelled']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('vendor.bookings'))
    
    # Verify booking belongs to this vendor
    booking = execute_query(
        "SELECT id FROM vendor_bookings WHERE id = %s AND vendor_id = %s",
        (booking_id, g.current_vendor['id']),
        fetch_one=True
    )
    
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('vendor.bookings'))
    
    # Update status
    if status == 'Completed':
        execute_update("""
            UPDATE vendor_bookings 
            SET status = %s, completed_at = %s
            WHERE id = %s
        """, (status, datetime.now(), booking_id))
        
        # Update vendor's last order date and orders count
        execute_update("""
            UPDATE vendors 
            SET last_order_date = %s, orders_in_validity = orders_in_validity + 1
            WHERE id = %s
        """, (datetime.now(), g.current_vendor['id']))
    else:
        execute_update(
            "UPDATE vendor_bookings SET status = %s WHERE id = %s",
            (status, booking_id)
        )
    
    flash(f'Booking status updated to {status}.', 'success')
    return redirect(url_for('vendor.bookings'))


@vendor_bp.route('/bookings/<int:booking_id>/verify-payment', methods=['POST'])
@vendor_required
def verify_payment(booking_id):
    """Verify payment for a booking"""
    payment_type = request.form.get('payment_type')  # 'advance' or 'final'
    
    if payment_type not in ['advance', 'final']:
        flash('Invalid payment type.', 'danger')
        return redirect(url_for('vendor.bookings'))
    
    # Verify booking belongs to this vendor
    booking = execute_query(
        "SELECT * FROM vendor_bookings WHERE id = %s AND vendor_id = %s",
        (booking_id, g.current_vendor['id']),
        fetch_one=True
    )
    
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('vendor.bookings'))
    
    # Update payment status
    if payment_type == 'advance':
        execute_update("""
            UPDATE vendor_bookings 
            SET advance_paid = TRUE, advance_paid_date = NOW(),
                payment_status = 'Advance Paid'
            WHERE id = %s
        """, (booking_id,))
        flash('Advance payment verified successfully!', 'success')
    else:  # final
        execute_update("""
            UPDATE vendor_bookings 
            SET final_paid = TRUE, final_paid_date = NOW(),
                payment_status = 'Fully Paid'
            WHERE id = %s
        """, (booking_id,))
        flash('Final payment verified successfully!', 'success')
    
    return redirect(url_for('vendor.bookings'))


@vendor_bp.route('/bookings/<int:booking_id>/reject-payment', methods=['POST'])
@vendor_required
def reject_payment(booking_id):
    """Reject payment for a booking"""
    payment_type = request.form.get('payment_type')  # 'advance' or 'final'
    reason = request.form.get('reason', '').strip()
    
    if payment_type not in ['advance', 'final']:
        flash('Invalid payment type.', 'danger')
        return redirect(url_for('vendor.bookings'))
    
    # Verify booking belongs to this vendor
    booking = execute_query(
        "SELECT * FROM vendor_bookings WHERE id = %s AND vendor_id = %s",
        (booking_id, g.current_vendor['id']),
        fetch_one=True
    )
    
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('vendor.bookings'))
    
    # Update payment status
    if payment_type == 'advance':
        execute_update("""
            UPDATE vendor_bookings 
            SET advance_paid = FALSE, advance_paid_date = NULL,
                payment_notes = %s
            WHERE id = %s
        """, (f"Advance payment rejected: {reason}", booking_id))
    else:  # final
        execute_update("""
            UPDATE vendor_bookings 
            SET final_paid = FALSE, final_paid_date = NULL,
                payment_notes = %s
            WHERE id = %s
        """, (f"Final payment rejected: {reason}", booking_id))
    
    flash(f'{payment_type.capitalize()} payment rejected.', 'info')
    return redirect(url_for('vendor.bookings'))


@vendor_bp.route('/reviews')
@vendor_required
def reviews():
    """View all reviews for this vendor"""
    # Get filter parameters
    rating_filter = request.args.get('rating_filter', '')
    sort_by = request.args.get('sort_by', 'recent')
    
    # Build query
    query = """
        SELECT vr.*, u.name as reviewer_name, u.email as reviewer_email
        FROM vendor_reviews vr
        JOIN users u ON vr.user_id = u.id
        WHERE vr.vendor_id = %s
    """
    params = [g.current_vendor['id']]
    
    # Apply rating filter
    if rating_filter:
        query += " AND vr.rating = %s"
        params.append(int(rating_filter))
    
    # Apply sorting
    if sort_by == 'helpful':
        query += " ORDER BY vr.helpful_count DESC, vr.created_at DESC"
    elif sort_by == 'rating_high':
        query += " ORDER BY vr.rating DESC, vr.created_at DESC"
    elif sort_by == 'rating_low':
        query += " ORDER BY vr.rating ASC, vr.created_at DESC"
    else:  # recent
        query += " ORDER BY vr.created_at DESC"
    
    reviews = execute_query(query, tuple(params))
    
    # Get rating distribution
    rating_distribution = execute_query("""
        SELECT rating, COUNT(*) as count
        FROM vendor_reviews
        WHERE vendor_id = %s
        GROUP BY rating
        ORDER BY rating DESC
    """, (g.current_vendor['id'],))
    
    rating_dist_dict = {r['rating']: r['count'] for r in rating_distribution}
    total_reviews = sum(rating_dist_dict.values())
    
    return render_template('vendor_reviews.html',
                         vendor=g.current_vendor,
                         reviews=reviews,
                         rating_distribution=rating_dist_dict,
                         total_reviews=total_reviews,
                         rating_filter=rating_filter,
                         sort_by=sort_by)


@vendor_bp.route('/reviews/<int:review_id>/respond', methods=['POST'])
@vendor_required
def respond_to_review(review_id):
    """Respond to a customer review"""
    response_text = request.form.get('response_text', '').strip()
    
    if not response_text:
        flash('Response cannot be empty.', 'danger')
        return redirect(url_for('vendor.reviews'))
    
    # Verify review belongs to this vendor
    review = execute_query("""
        SELECT id FROM vendor_reviews 
        WHERE id = %s AND vendor_id = %s
    """, (review_id, g.current_vendor['id']), fetch_one=True)
    
    if not review:
        flash('Review not found.', 'danger')
        return redirect(url_for('vendor.reviews'))
    
    # Add or update response
    execute_update("""
        UPDATE vendor_reviews 
        SET vendor_response = %s, vendor_response_date = NOW()
        WHERE id = %s
    """, (response_text, review_id))
    
    flash('Response added successfully!', 'success')
    return redirect(url_for('vendor.reviews'))


@vendor_bp.route('/reviews/<int:review_id>/delete-response', methods=['POST'])
@vendor_required
def delete_review_response(review_id):
    """Delete vendor response to a review"""
    # Verify review belongs to this vendor
    review = execute_query("""
        SELECT id FROM vendor_reviews 
        WHERE id = %s AND vendor_id = %s
    """, (review_id, g.current_vendor['id']), fetch_one=True)
    
    if not review:
        flash('Review not found.', 'danger')
        return redirect(url_for('vendor.reviews'))
    
    # Delete response
    execute_update("""
        UPDATE vendor_reviews 
        SET vendor_response = NULL, vendor_response_date = NULL
        WHERE id = %s
    """, (review_id,))
    
    flash('Response deleted.', 'info')
    return redirect(url_for('vendor.reviews'))



