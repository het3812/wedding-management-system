"""
Marketplace Blueprint - Public vendor discovery, filtering, booking
Accessible to all users (hosts) to find and book vendors
"""
import secrets
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify
from werkzeug.utils import secure_filename
from db import execute_query, execute_update
from datetime import datetime, timedelta
from config import ALLOWED_EXTENSIONS

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/marketplace')

VENDOR_CATEGORIES = [
    'Photographer', 'Clothes/Boutique', 'Party Plot', 'Car Booking',
    'Makeup Artist', 'Mehendi Artist', 'Pandit', 'Catering', 'Decoration'
]


def login_required(f):
    """Decorator: require any logged-in user"""
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('host.login'))
        g.current_user_id = session['user_id']
        g.current_user = execute_query(
            "SELECT * FROM users WHERE id = %s", 
            (session['user_id'],), 
            fetch_one=True
        )
        return f(*args, **kwargs)
    return wrapped


@marketplace_bp.route('/')
def index():
    """Vendor marketplace with filtering and search"""
    # Get filter parameters
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    min_rating = request.args.get('rating', '')
    sort_by = request.args.get('sort', 'rating')  # rating, price_low, price_high
    search = request.args.get('search', '')
    
    # Build query
    query = """
        SELECT v.*, u.name as vendor_name,
               (SELECT MIN(price) FROM vendor_services WHERE vendor_id = v.id) as min_price,
               (SELECT COUNT(*) FROM vendor_gallery WHERE vendor_id = v.id) as gallery_count
        FROM vendors v
        JOIN users u ON v.user_id = u.id
        WHERE v.is_approved = 1 AND v.is_blocked = 0
    """
    params = []
    
    # Apply filters
    if category:
        query += " AND v.category = %s"
        params.append(category)
    
    if city:
        query += " AND v.city LIKE %s"
        params.append(f"%{city}%")
    
    if min_rating:
        query += " AND v.average_rating >= %s"
        params.append(float(min_rating))
    
    if search:
        query += " AND (v.business_name LIKE %s OR v.description LIKE %s OR v.category LIKE %s)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])
    
    # Apply sorting
    if sort_by == 'price_low':
        query += " ORDER BY min_price ASC"
    elif sort_by == 'price_high':
        query += " ORDER BY min_price DESC"
    else:  # rating (default)
        query += " ORDER BY v.average_rating DESC, v.total_reviews DESC"
    
    vendors = execute_query(query, tuple(params))
    
    # Get available cities for filter
    cities = execute_query(
        "SELECT DISTINCT city FROM vendors WHERE city IS NOT NULL AND city != '' ORDER BY city"
    )
    
    return render_template('marketplace_index.html',
                         vendors=vendors,
                         categories=VENDOR_CATEGORIES,
                         cities=cities,
                         selected_category=category,
                         selected_city=city,
                         selected_rating=min_rating,
                         selected_sort=sort_by,
                         search_query=search)


@marketplace_bp.route('/vendor/<int:vendor_id>')
def vendor_profile(vendor_id):
    """Detailed vendor profile page"""
    vendor = execute_query("""
        SELECT v.*, u.name as vendor_name, u.email as user_email
        FROM vendors v
        JOIN users u ON v.user_id = u.id
        WHERE v.id = %s AND v.is_approved = 1 AND v.is_blocked = 0
    """, (vendor_id,), fetch_one=True)
    
    if not vendor:
        flash('Vendor not found or not available.', 'danger')
        return redirect(url_for('marketplace.index'))
    
    # Get services
    services = execute_query(
        "SELECT * FROM vendor_services WHERE vendor_id = %s ORDER BY created_at DESC",
        (vendor_id,)
    )
    
    # Get gallery
    gallery = execute_query(
        "SELECT * FROM vendor_gallery WHERE vendor_id = %s ORDER BY display_order, uploaded_at DESC",
        (vendor_id,)
    )
    
    # Get filter parameters
    rating_filter = request.args.get('rating_filter', '')
    sort_by = request.args.get('sort_by', 'recent')  # recent, helpful, rating_high, rating_low
    
    # Build reviews query
    reviews_query = """
        SELECT vr.*, u.name as reviewer_name,
               (SELECT COUNT(*) FROM review_helpfulness WHERE review_id = vr.id AND is_helpful = 1) as helpful_count,
               (SELECT COUNT(*) FROM review_helpfulness WHERE review_id = vr.id AND is_helpful = 0) as unhelpful_count
        FROM vendor_reviews vr
        JOIN users u ON vr.user_id = u.id
        WHERE vr.vendor_id = %s
    """
    params = [vendor_id]
    
    # Apply rating filter
    if rating_filter:
        reviews_query += " AND vr.rating = %s"
        params.append(int(rating_filter))
    
    # Apply sorting
    if sort_by == 'helpful':
        reviews_query += " ORDER BY vr.helpful_count DESC, vr.created_at DESC"
    elif sort_by == 'rating_high':
        reviews_query += " ORDER BY vr.rating DESC, vr.created_at DESC"
    elif sort_by == 'rating_low':
        reviews_query += " ORDER BY vr.rating ASC, vr.created_at DESC"
    else:  # recent (default)
        reviews_query += " ORDER BY vr.created_at DESC"
    
    reviews = execute_query(reviews_query, tuple(params))
    
    # Get rating distribution
    rating_distribution = execute_query("""
        SELECT rating, COUNT(*) as count
        FROM vendor_reviews
        WHERE vendor_id = %s
        GROUP BY rating
        ORDER BY rating DESC
    """, (vendor_id,))
    
    # Convert to dict for easy access
    rating_dist_dict = {r['rating']: r['count'] for r in rating_distribution}
    total_reviews = sum(rating_dist_dict.values())
    
    # Check if current user has reviewed
    user_review = None
    user_booking = None
    if 'user_id' in session:
        user_review = execute_query("""
            SELECT * FROM vendor_reviews 
            WHERE vendor_id = %s AND user_id = %s
        """, (vendor_id, session['user_id']), fetch_one=True)
        
        user_booking = execute_query("""
            SELECT id FROM vendor_bookings 
            WHERE vendor_id = %s AND user_id = %s AND status = 'Completed'
            LIMIT 1
        """, (vendor_id, session['user_id']), fetch_one=True)
    
    # Check if current user has existing chat
    chat_id = None
    if 'user_id' in session:
        chat = execute_query(
            "SELECT id FROM vendor_chats WHERE vendor_id = %s AND user_id = %s",
            (vendor_id, session['user_id']),
            fetch_one=True
        )
        if chat:
            chat_id = chat['id']
    
    return render_template('marketplace_vendor_profile.html',
                         vendor=vendor,
                         services=services,
                         gallery=gallery,
                         reviews=reviews,
                         rating_distribution=rating_dist_dict,
                         total_reviews=total_reviews,
                         user_review=user_review,
                         user_booking=user_booking,
                         chat_id=chat_id,
                         rating_filter=rating_filter,
                         sort_by=sort_by)


@marketplace_bp.route('/vendor/<int:vendor_id>/book', methods=['GET', 'POST'])
@login_required
def book_vendor(vendor_id):
    """Book a vendor service"""
    vendor = execute_query(
        "SELECT * FROM vendors WHERE id = %s AND is_approved = 1 AND is_blocked = 0",
        (vendor_id,),
        fetch_one=True
    )
    
    if not vendor:
        flash('Vendor not available.', 'danger')
        return redirect(url_for('marketplace.index'))
    
    if request.method == 'GET':
        services = execute_query(
            "SELECT * FROM vendor_services WHERE vendor_id = %s",
            (vendor_id,)
        )
        return render_template('marketplace_booking_form.html', vendor=vendor, services=services)
    
    # Process booking
    service_id = request.form.get('service_id')
    event_date = request.form.get('event_date')
    notes = request.form.get('notes', '').strip()
    
    if not event_date:
        flash('Event date is required.', 'danger')
        return redirect(request.url)
    
    # Convert empty service_id to None
    if service_id == '' or service_id == 'None':
        service_id = None
    
    # Get service price
    total_amount = None
    if service_id:
        service = execute_query(
            "SELECT price FROM vendor_services WHERE id = %s",
            (service_id,),
            fetch_one=True
        )
        if service:
            total_amount = service['price']
    
    # Create booking
    execute_update("""
        INSERT INTO vendor_bookings 
        (vendor_id, user_id, service_id, booking_date, event_date, total_amount, notes, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
    """, (vendor_id, g.current_user_id, service_id, datetime.now().date(), event_date, total_amount, notes))
    
    # Update vendor's last order date
    execute_update(
        "UPDATE vendors SET last_order_date = %s WHERE id = %s",
        (datetime.now(), vendor_id)
    )
    
    flash('Booking request sent successfully! The vendor will contact you soon.', 'success')
    return redirect(url_for('marketplace.my_bookings'))


@marketplace_bp.route('/my-bookings')
@login_required
def my_bookings():
    """View user's bookings"""
    bookings = execute_query("""
        SELECT vb.*, v.business_name, v.contact_email, v.contact_phone,
               v.upi_id, v.upi_qr_code, v.accepts_online_payment,
               vs.title as service_title
        FROM vendor_bookings vb
        JOIN vendors v ON vb.vendor_id = v.id
        LEFT JOIN vendor_services vs ON vb.service_id = vs.id
        WHERE vb.user_id = %s
        ORDER BY vb.created_at DESC
    """, (g.current_user_id,))
    
    return render_template('marketplace_my_bookings.html', bookings=bookings)


@marketplace_bp.route('/booking/<int:booking_id>/payment', methods=['GET', 'POST'])
@login_required
def make_payment(booking_id):
    """Make payment for a booking"""
    # Get booking details
    booking = execute_query("""
        SELECT vb.*, v.business_name, v.upi_id, v.upi_qr_code, 
               v.accepts_online_payment, v.payment_terms,
               vs.title as service_title
        FROM vendor_bookings vb
        JOIN vendors v ON vb.vendor_id = v.id
        LEFT JOIN vendor_services vs ON vb.service_id = vs.id
        WHERE vb.id = %s AND vb.user_id = %s
    """, (booking_id, g.current_user_id), fetch_one=True)
    
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('marketplace.my_bookings'))
    
    if request.method == 'GET':
        return render_template('marketplace_payment.html', booking=booking)
    
    # Process payment submission
    payment_type = request.form.get('payment_type')  # 'advance' or 'final'
    payment_method = request.form.get('payment_method', 'UPI')
    transaction_id = request.form.get('transaction_id', '').strip()
    amount = request.form.get('amount', '').strip()
    notes = request.form.get('notes', '').strip()
    
    if not amount:
        flash('Payment amount is required.', 'danger')
        return redirect(request.url)
    
    amount_val = float(amount)
    
    # Handle payment proof upload
    payment_proof = None
    if 'payment_proof' in request.files and request.files['payment_proof'].filename:
        file = request.files['payment_proof']
        if file and allowed_file(file.filename):
            from config import UPLOAD_FOLDER
            UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            user_dir = UPLOAD_FOLDER / str(g.current_user_id) / 'payments'
            user_dir.mkdir(parents=True, exist_ok=True)
            
            fn = secure_filename(file.filename)
            unique = f"payment_{secrets.token_hex(4)}_{fn}"
            filepath = user_dir / unique
            file.save(str(filepath))
            payment_proof = f"uploads/{g.current_user_id}/payments/{unique}"
    
    # Update booking with payment info
    if payment_type == 'advance':
        execute_update("""
            UPDATE vendor_bookings 
            SET advance_amount = %s, advance_payment_proof = %s,
                payment_method = %s, payment_notes = %s,
                payment_status = 'Advance Paid'
            WHERE id = %s
        """, (amount_val, payment_proof, payment_method, notes, booking_id))
    else:  # final
        execute_update("""
            UPDATE vendor_bookings 
            SET final_amount = %s, final_payment_proof = %s,
                payment_method = %s, payment_notes = %s,
                payment_status = 'Fully Paid'
            WHERE id = %s
        """, (amount_val, payment_proof, payment_method, notes, booking_id))
    
    # Create payment transaction record
    execute_update("""
        INSERT INTO payment_transactions 
        (booking_id, vendor_id, user_id, transaction_type, amount, payment_method, 
         payment_proof, transaction_id, notes, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
    """, (booking_id, booking['vendor_id'], g.current_user_id, 
          payment_type.capitalize(), amount_val, payment_method,
          payment_proof, transaction_id, notes))
    
    flash('Payment submitted successfully! Vendor will verify it soon.', 'success')
    return redirect(url_for('marketplace.my_bookings'))


@marketplace_bp.route('/vendor/<int:vendor_id>/review', methods=['POST'])
@login_required
def add_review(vendor_id):
    """Add or update review for a vendor"""
    rating = request.form.get('rating')
    review_text = request.form.get('review_text', '').strip()
    
    if not rating or int(rating) < 1 or int(rating) > 5:
        flash('Please provide a valid rating (1-5 stars).', 'danger')
        return redirect(url_for('marketplace.vendor_profile', vendor_id=vendor_id))
    
    # Check if user has booked this vendor
    booking = execute_query("""
        SELECT id FROM vendor_bookings 
        WHERE vendor_id = %s AND user_id = %s AND status = 'Completed'
        LIMIT 1
    """, (vendor_id, g.current_user_id), fetch_one=True)
    
    is_verified = True if booking else False
    
    # Check if review already exists
    existing_review = execute_query("""
        SELECT id FROM vendor_reviews 
        WHERE vendor_id = %s AND user_id = %s
    """, (vendor_id, g.current_user_id), fetch_one=True)
    
    if existing_review:
        # Update existing review
        execute_update("""
            UPDATE vendor_reviews 
            SET rating = %s, review_text = %s, updated_at = NOW()
            WHERE id = %s
        """, (rating, review_text, existing_review['id']))
        flash('Review updated successfully!', 'success')
    else:
        # Insert new review
        execute_update("""
            INSERT INTO vendor_reviews (vendor_id, user_id, rating, review_text, is_verified_booking)
            VALUES (%s, %s, %s, %s, %s)
        """, (vendor_id, g.current_user_id, rating, review_text, is_verified))
        flash('Review submitted successfully!', 'success')
    
    # Update vendor's average rating and total reviews
    stats = execute_query("""
        SELECT AVG(rating) as avg_rating, COUNT(*) as total
        FROM vendor_reviews
        WHERE vendor_id = %s
    """, (vendor_id,), fetch_one=True)
    
    execute_update("""
        UPDATE vendors 
        SET average_rating = %s, total_reviews = %s
        WHERE id = %s
    """, (stats['avg_rating'], stats['total'], vendor_id))
    
    return redirect(url_for('marketplace.vendor_profile', vendor_id=vendor_id))


@marketplace_bp.route('/review/<int:review_id>/helpful', methods=['POST'])
@login_required
def mark_review_helpful(review_id):
    """Mark a review as helpful or unhelpful"""
    is_helpful = request.form.get('is_helpful') == '1'
    
    # Check if user already voted
    existing = execute_query("""
        SELECT id, is_helpful FROM review_helpfulness 
        WHERE review_id = %s AND user_id = %s
    """, (review_id, g.current_user_id), fetch_one=True)
    
    if existing:
        if existing['is_helpful'] == is_helpful:
            # Remove vote (toggle off)
            execute_update("""
                DELETE FROM review_helpfulness 
                WHERE review_id = %s AND user_id = %s
            """, (review_id, g.current_user_id))
        else:
            # Change vote
            execute_update("""
                UPDATE review_helpfulness 
                SET is_helpful = %s 
                WHERE review_id = %s AND user_id = %s
            """, (is_helpful, review_id, g.current_user_id))
    else:
        # New vote
        execute_update("""
            INSERT INTO review_helpfulness (review_id, user_id, is_helpful)
            VALUES (%s, %s, %s)
        """, (review_id, g.current_user_id, is_helpful))
    
    # Update review helpful counts
    counts = execute_query("""
        SELECT 
            SUM(CASE WHEN is_helpful = 1 THEN 1 ELSE 0 END) as helpful,
            SUM(CASE WHEN is_helpful = 0 THEN 1 ELSE 0 END) as unhelpful
        FROM review_helpfulness
        WHERE review_id = %s
    """, (review_id,), fetch_one=True)
    
    execute_update("""
        UPDATE vendor_reviews 
        SET helpful_count = %s, unhelpful_count = %s
        WHERE id = %s
    """, (counts['helpful'] or 0, counts['unhelpful'] or 0, review_id))
    
    return jsonify({'success': True, 'helpful': counts['helpful'] or 0, 'unhelpful': counts['unhelpful'] or 0})


@marketplace_bp.route('/review/<int:review_id>/report', methods=['POST'])
@login_required
def report_review(review_id):
    """Report an inappropriate review"""
    reason = request.form.get('reason')
    description = request.form.get('description', '').strip()
    
    if reason not in ['Spam', 'Offensive', 'Fake', 'Irrelevant', 'Other']:
        flash('Invalid report reason.', 'danger')
        return redirect(request.referrer or url_for('marketplace.index'))
    
    # Check if already reported by this user
    existing = execute_query("""
        SELECT id FROM review_reports 
        WHERE review_id = %s AND reporter_user_id = %s
    """, (review_id, g.current_user_id), fetch_one=True)
    
    if existing:
        flash('You have already reported this review.', 'warning')
    else:
        execute_update("""
            INSERT INTO review_reports (review_id, reporter_user_id, reason, description)
            VALUES (%s, %s, %s, %s)
        """, (review_id, g.current_user_id, reason, description))
        flash('Review reported. Our team will review it shortly.', 'success')
    
    return redirect(request.referrer or url_for('marketplace.index'))


@marketplace_bp.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    """Delete own review"""
    review = execute_query("""
        SELECT vendor_id FROM vendor_reviews 
        WHERE id = %s AND user_id = %s
    """, (review_id, g.current_user_id), fetch_one=True)
    
    if not review:
        flash('Review not found or you do not have permission to delete it.', 'danger')
        return redirect(request.referrer or url_for('marketplace.index'))
    
    vendor_id = review['vendor_id']
    
    # Delete review
    execute_update("DELETE FROM vendor_reviews WHERE id = %s", (review_id,))
    
    # Update vendor's average rating
    stats = execute_query("""
        SELECT AVG(rating) as avg_rating, COUNT(*) as total
        FROM vendor_reviews
        WHERE vendor_id = %s
    """, (vendor_id,), fetch_one=True)
    
    execute_update("""
        UPDATE vendors 
        SET average_rating = %s, total_reviews = %s
        WHERE id = %s
    """, (stats['avg_rating'] or 0, stats['total'], vendor_id))
    
    flash('Review deleted successfully.', 'success')
    return redirect(url_for('marketplace.vendor_profile', vendor_id=vendor_id))



