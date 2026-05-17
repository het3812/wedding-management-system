"""
Admin Blueprint - Dashboard, Create Invitation, Upload Images
Protected: admin only
"""
import secrets
import os
from pathlib import Path
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, g
from werkzeug.utils import secure_filename

from werkzeug.security import generate_password_hash

from db import execute_query, execute_update
from blueprints.auth import admin_required
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

admin_bp = Blueprint('admin', __name__)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_invite_token():
    """Generate a cryptographically secure unique token for invitation URL"""
    return secrets.token_urlsafe(32)


@admin_bp.route('/')
@admin_required
def dashboard():
    """
    Admin dashboard: ALL invitations (from all hosts), vendor summary
    Filter by date range, status, and host
    """
    # Get filter parameters
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    status_filter = request.args.get('status', 'all')
    host_filter = request.args.get('host', 'all')
    search = request.args.get('search', '')
    
    # Build query with filters
    query = """SELECT i.id, i.bride_name, i.groom_name, i.wedding_date, i.venue, i.invite_token, i.is_active,
                      i.created_at, u.name as host_name, u.id as host_id
               FROM invitations i
               LEFT JOIN users u ON i.user_id = u.id
               WHERE 1=1"""
    params = []
    
    # Apply date filters
    if date_from:
        query += " AND i.wedding_date >= %s"
        params.append(date_from)
    
    if date_to:
        query += " AND i.wedding_date <= %s"
        params.append(date_to)
    
    # Apply status filter
    if status_filter == 'active':
        query += " AND i.is_active = 1"
    elif status_filter == 'inactive':
        query += " AND i.is_active = 0"
    
    # Apply host filter
    if host_filter != 'all':
        query += " AND u.id = %s"
        params.append(int(host_filter))
    
    # Apply search filter
    if search:
        query += " AND (i.bride_name LIKE %s OR i.groom_name LIKE %s OR i.venue LIKE %s OR u.name LIKE %s)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term, search_term])
    
    query += " ORDER BY i.wedding_date DESC, i.created_at DESC"
    
    invitations = execute_query(query, tuple(params) if params else None)
    
    # Get all hosts for filter dropdown
    hosts = execute_query(
        "SELECT id, name FROM users WHERE role = 'host' ORDER BY name"
    )
    
    # Stats for admin
    host_count = execute_query(
        "SELECT COUNT(*) as c FROM users WHERE role = 'host'",
        fetch_one=True
    ) or {'c': 0}
    vendor_count = execute_query(
        "SELECT COUNT(*) as c FROM vendors",
        fetch_one=True
    ) or {'c': 0}
    service_count = execute_query(
        "SELECT COUNT(*) as c FROM vendor_services",
        fetch_one=True
    ) or {'c': 0}
    
    # Count filtered results
    total_invitations = len(invitations)
    active_invitations = sum(1 for i in invitations if i['is_active'])
    upcoming_invitations = sum(1 for i in invitations if i['wedding_date'] and i['wedding_date'] >= datetime.now().date())
    
    return render_template('admin_dashboard.html', 
                          invitations=invitations,
                          hosts=hosts,
                          total_hosts=host_count['c'], 
                          total_vendors=vendor_count['c'], 
                          total_services=service_count['c'],
                          total_invitations=total_invitations,
                          active_invitations=active_invitations,
                          upcoming_invitations=upcoming_invitations,
                          date_from=date_from,
                          date_to=date_to,
                          status_filter=status_filter,
                          host_filter=host_filter,
                          search=search)


@admin_bp.route('/invitation/create', methods=['GET', 'POST'])
@admin_required
def create_invitation():
    """
    Create a new wedding invitation.
    Generates unique token and stores in DB.
    """
    if request.method == 'GET':
        return render_template('admin_invitation_form.html', invitation=None)

    bride_name = request.form.get('bride_name', '').strip()
    groom_name = request.form.get('groom_name', '').strip()
    wedding_date = request.form.get('wedding_date', '').strip()
    venue = request.form.get('venue', '').strip()
    message = request.form.get('message', '').strip()

    if not all([bride_name, groom_name, wedding_date, venue]):
        flash('Bride name, Groom name, Wedding date, and Venue are required.', 'danger')
        return render_template('admin_invitation_form.html', invitation=None)

    # Generate unique token (retry if collision - extremely rare)
    token = generate_invite_token()
    while execute_query("SELECT id FROM invitations WHERE invite_token = %s", (token,), fetch_one=True):
        token = generate_invite_token()

    execute_update(
        """INSERT INTO invitations (user_id, bride_name, groom_name, wedding_date, venue, message, invite_token)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (g.current_user_id, bride_name, groom_name, wedding_date, venue, message, token)
    )
    flash('Invitation created successfully! Share the link below.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/invitation/<int:inv_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_invitation(inv_id):
    """Edit existing invitation"""
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s",
        (inv_id,),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'GET':
        return render_template('admin_invitation_form.html', invitation=inv)

    bride_name = request.form.get('bride_name', '').strip()
    groom_name = request.form.get('groom_name', '').strip()
    wedding_date = request.form.get('wedding_date', '').strip()
    venue = request.form.get('venue', '').strip()
    message = request.form.get('message', '').strip()
    is_active = request.form.get('is_active') == 'on'

    if not all([bride_name, groom_name, wedding_date, venue]):
        flash('Bride name, Groom name, Wedding date, and Venue are required.', 'danger')
        inv.update({'bride_name': bride_name, 'groom_name': groom_name, 'wedding_date': wedding_date,
                    'venue': venue, 'message': message, 'is_active': is_active})
        return render_template('admin_invitation_form.html', invitation=inv)

    execute_update(
        """UPDATE invitations SET bride_name=%s, groom_name=%s, wedding_date=%s, venue=%s, message=%s, is_active=%s
           WHERE id=%s""",
        (bride_name, groom_name, wedding_date, venue, message, is_active, inv_id)
    )
    flash('Invitation updated.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/invitation/<int:inv_id>/upload', methods=['GET', 'POST'])
@admin_required
def upload_images(inv_id):
    """
    Upload wedding images for an invitation.
    Stores in static/uploads and saves path in DB.
    """
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s",
        (inv_id,),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'GET':
        images = execute_query("SELECT * FROM wedding_images WHERE invitation_id = %s ORDER BY upload_date DESC", (inv_id,))
        return render_template('admin_upload.html', invitation=inv, images=images)

    # Handle file upload
    if 'images' not in request.files and 'image' not in request.files:
        flash('No file selected.', 'warning')
        return redirect(request.url)

    album_name = request.form.get('album_name', '').strip() or 'Main'
    files = request.files.getlist('images') if request.files.getlist('images') else [request.files.get('image')]
    upload_dir = UPLOAD_FOLDER / str(inv_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{secrets.token_hex(4)}_{filename}"
            filepath = upload_dir / unique_name
            file.save(str(filepath))
            rel_path = f"uploads/{inv_id}/{unique_name}"
            # Insert with album_name if column exists (migration adds it)
            try:
                execute_update(
                    "INSERT INTO wedding_images (invitation_id, image_path, album_name) VALUES (%s, %s, %s)",
                    (inv_id, rel_path, album_name)
                )
            except Exception:
                execute_update(
                    "INSERT INTO wedding_images (invitation_id, image_path) VALUES (%s, %s)",
                    (inv_id, rel_path)
                )
            count += 1

    if count > 0:
        flash(f'{count} image(s) uploaded successfully.', 'success')
    else:
        flash('No valid images uploaded. Allowed: png, jpg, jpeg, gif, webp', 'warning')

    return redirect(url_for('admin.upload_images', inv_id=inv_id))


# ========== Guest Management ==========
@admin_bp.route('/invitation/<int:inv_id>/guests')
@admin_required
def manage_guests(inv_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s",
        (inv_id,),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('admin.dashboard'))
    guests = execute_query(
        "SELECT * FROM guests WHERE invitation_id = %s ORDER BY category, name",
        (inv_id,)
    )
    return render_template('admin_guests.html', invitation=inv, guests=guests)


@admin_bp.route('/invitation/<int:inv_id>/guests/add', methods=['GET', 'POST'])
@admin_required
def add_guest(inv_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s",
        (inv_id,),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'GET':
        return render_template('admin_guest_form.html', invitation=inv, guest=None)

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    category = request.form.get('category', 'Friend')
    if not name:
        flash('Guest name required.', 'danger')
        return render_template('admin_guest_form.html', invitation=inv, guest=None)

    execute_update(
        """INSERT INTO guests (invitation_id, name, email, phone, category) VALUES (%s, %s, %s, %s, %s)""",
        (inv_id, name, email or None, phone or None, category)
    )
    flash('Guest added.', 'success')
    return redirect(url_for('admin.manage_guests', inv_id=inv_id))


@admin_bp.route('/invitation/<int:inv_id>/guests/<int:guest_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_guest(inv_id, guest_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s",
        (inv_id,),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('admin.dashboard'))
    guest = execute_query(
        "SELECT * FROM guests WHERE id = %s AND invitation_id = %s",
        (guest_id, inv_id),
        fetch_one=True
    )
    if not guest:
        flash('Guest not found.', 'danger')
        return redirect(url_for('admin.manage_guests', inv_id=inv_id))

    if request.method == 'GET':
        return render_template('admin_guest_form.html', invitation=inv, guest=guest)

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    category = request.form.get('category', 'Friend')
    rsvp_status = request.form.get('rsvp_status', 'Pending')
    if not name:
        flash('Guest name required.', 'danger')
        return render_template('admin_guest_form.html', invitation=inv, guest=guest)

    execute_update(
        """UPDATE guests SET name=%s, email=%s, phone=%s, category=%s, rsvp_status=%s
           WHERE id=%s AND invitation_id=%s""",
        (name, email or None, phone or None, category, rsvp_status, guest_id, inv_id)
    )
    flash('Guest updated.', 'success')
    return redirect(url_for('admin.manage_guests', inv_id=inv_id))


@admin_bp.route('/invitation/<int:inv_id>/guests/<int:guest_id>/delete')
@admin_required
def delete_guest(inv_id, guest_id):
    inv = execute_query(
        "SELECT id FROM invitations WHERE id = %s",
        (inv_id,),
        fetch_one=True
    )
    if inv:
        execute_update("DELETE FROM guests WHERE id = %s AND invitation_id = %s", (guest_id, inv_id))
        flash('Guest removed.', 'info')
    return redirect(url_for('admin.manage_guests', inv_id=inv_id))


# ========== Wedding Events ==========
@admin_bp.route('/invitation/<int:inv_id>/events')
@admin_required
def manage_events(inv_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s",
        (inv_id,),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('admin.dashboard'))
    events = execute_query(
        "SELECT * FROM wedding_events WHERE invitation_id = %s ORDER BY event_date, event_time",
        (inv_id,)
    )
    for e in events:
        if e.get('event_time') and hasattr(e['event_time'], 'total_seconds'):
            secs = int(e['event_time'].total_seconds())
            e['time_display'] = f"{(secs // 3600) % 12 or 12}:{(secs % 3600) // 60:02d} {'AM' if secs < 43200 else 'PM'}"
        else:
            e['time_display'] = str(e.get('event_time') or '')[:5]
    return render_template('admin_events.html', invitation=inv, events=events)


@admin_bp.route('/invitation/<int:inv_id>/events/add', methods=['GET', 'POST'])
@admin_required
def add_event(inv_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s",
        (inv_id,),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'GET':
        return render_template('admin_event_form.html', invitation=inv, event=None)

    event_name = request.form.get('event_name', '').strip()
    event_date = request.form.get('event_date', '').strip()
    event_time = request.form.get('event_time', '').strip()
    venue = request.form.get('venue', '').strip()
    if not all([event_name, event_date, venue]):
        flash('Event name, date, and venue required.', 'danger')
        return render_template('admin_event_form.html', invitation=inv, event=None)

    execute_update(
        """INSERT INTO wedding_events (invitation_id, event_name, event_date, event_time, venue)
           VALUES (%s, %s, %s, %s, %s)""",
        (inv_id, event_name, event_date, event_time or None, venue)
    )
    flash('Event added.', 'success')
    return redirect(url_for('admin.manage_events', inv_id=inv_id))


@admin_bp.route('/invitation/<int:inv_id>/events/<int:evt_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_event(inv_id, evt_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s",
        (inv_id,),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('admin.dashboard'))
    event = execute_query(
        "SELECT * FROM wedding_events WHERE id = %s AND invitation_id = %s",
        (evt_id, inv_id),
        fetch_one=True
    )
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('admin.manage_events', inv_id=inv_id))

    if request.method == 'GET':
        # Format event_time for HTML time input (MySQL returns timedelta)
        t = event.get('event_time')
        if t and hasattr(t, 'total_seconds'):
            secs = int(t.total_seconds())
            event['time_value'] = f"{(secs // 3600) % 24:02d}:{(secs % 3600) // 60:02d}"
        elif t and hasattr(t, 'strftime'):
            event['time_value'] = t.strftime('%H:%M')
        else:
            event['time_value'] = ''
        return render_template('admin_event_form.html', invitation=inv, event=event)

    event_name = request.form.get('event_name', '').strip()
    event_date = request.form.get('event_date', '').strip()
    event_time = request.form.get('event_time', '').strip()
    venue = request.form.get('venue', '').strip()
    if not all([event_name, event_date, venue]):
        flash('Event name, date, and venue required.', 'danger')
        return render_template('admin_event_form.html', invitation=inv, event=event)

    execute_update(
        """UPDATE wedding_events SET event_name=%s, event_date=%s, event_time=%s, venue=%s
           WHERE id=%s AND invitation_id=%s""",
        (event_name, event_date, event_time or None, venue, evt_id, inv_id)
    )
    flash('Event updated.', 'success')
    return redirect(url_for('admin.manage_events', inv_id=inv_id))


@admin_bp.route('/invitation/<int:inv_id>/events/<int:evt_id>/delete')
@admin_required
def delete_event(inv_id, evt_id):
    inv = execute_query(
        "SELECT id FROM invitations WHERE id = %s",
        (inv_id,),
        fetch_one=True
    )
    if inv:
        execute_update("DELETE FROM wedding_events WHERE id = %s AND invitation_id = %s", (evt_id, inv_id))
        flash('Event deleted.', 'info')
    return redirect(url_for('admin.manage_events', inv_id=inv_id))


# ========== Vendor Management (Admin View) ==========
# ========== Host Management (Admin only) ==========
@admin_bp.route('/hosts')
@admin_required
def list_hosts():
    """List all host users with activity summary (invitations, guests, events)"""
    hosts = execute_query(
        "SELECT id, name, email, created_at FROM users WHERE role = 'host' ORDER BY created_at DESC"
    )
    for h in hosts:
        inv_count = execute_query(
            "SELECT COUNT(*) as c FROM invitations WHERE user_id = %s", (h['id'],), fetch_one=True
        ) or {'c': 0}
        h['invitation_count'] = inv_count['c']
        guest_count = execute_query(
            """SELECT COUNT(*) as c FROM guests g
               JOIN invitations i ON g.invitation_id = i.id WHERE i.user_id = %s""",
            (h['id'],), fetch_one=True
        ) or {'c': 0}
        h['guest_count'] = guest_count['c']
        event_count = execute_query(
            """SELECT COUNT(*) as c FROM wedding_events e
               JOIN invitations i ON e.invitation_id = i.id WHERE i.user_id = %s""",
            (h['id'],), fetch_one=True
        ) or {'c': 0}
        h['event_count'] = event_count['c']
    return render_template('admin_hosts.html', hosts=hosts)


@admin_bp.route('/hosts/<int:host_id>/activity')
@admin_required
def host_activity(host_id):
    """Admin view: all activity of one host (invitations with guest/event counts)"""
    host = execute_query(
        "SELECT id, name, email, created_at FROM users WHERE id = %s AND role = 'host'",
        (host_id,), fetch_one=True
    )
    if not host:
        flash('Host not found.', 'danger')
        return redirect(url_for('admin.list_hosts'))
    invitations = execute_query(
        """SELECT id, bride_name, groom_name, wedding_date, venue, invite_token, is_active, created_at
           FROM invitations WHERE user_id = %s ORDER BY created_at DESC""",
        (host_id,)
    )
    for inv in invitations:
        gc = execute_query("SELECT COUNT(*) as c FROM guests WHERE invitation_id = %s", (inv['id'],), fetch_one=True) or {'c': 0}
        ec = execute_query("SELECT COUNT(*) as c FROM wedding_events WHERE invitation_id = %s", (inv['id'],), fetch_one=True) or {'c': 0}
        inv['guest_count'] = gc['c']
        inv['event_count'] = ec['c']
    return render_template('admin_host_activity.html', host=host, invitations=invitations)


@admin_bp.route('/hosts/add', methods=['GET', 'POST'])
@admin_required
def add_host():
    """Create new host account"""
    if request.method == 'GET':
        return render_template('admin_host_form.html', host=None)

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    if not all([name, email, password]):
        flash('Name, email and password are required.', 'danger')
        return render_template('admin_host_form.html', host=None)

    if len(password) < 6:
        flash('Password must be at least 6 characters.', 'danger')
        return render_template('admin_host_form.html', host=None)

    existing = execute_query("SELECT id FROM users WHERE email = %s", (email,), fetch_one=True)
    if existing:
        flash('Email already registered.', 'danger')
        return render_template('admin_host_form.html', host=None)

    hashed = generate_password_hash(password)
    execute_update(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'host')",
        (name, email, hashed)
    )
    flash(f'Host "{name}" created. They can now login at Host Login.', 'success')
    return redirect(url_for('admin.list_hosts'))


# ========== Vendor Management (Admin View) ==========
@admin_bp.route('/vendors')
@admin_required
def list_vendors():
    vendors = execute_query(
        """SELECT v.*, u.name as user_name, u.email as user_email,
           (SELECT COUNT(*) FROM vendor_services WHERE vendor_id = v.id) as service_count
           FROM vendors v JOIN users u ON v.user_id = u.id ORDER BY v.created_at DESC"""
    )
    total_services = execute_query("SELECT COUNT(*) as c FROM vendor_services", fetch_one=True) or {'c': 0}
    return render_template('admin_vendors.html', vendors=vendors, total_services=total_services['c'])


@admin_bp.route('/vendors/all-services')
@admin_required
def all_vendor_services():
    """Admin view: all vendor services from all vendors in one list"""
    services = execute_query(
        """SELECT vs.id, vs.vendor_id, vs.title, vs.description, vs.price, vs.image_path, vs.created_at,
                  v.business_name, v.service_type, v.contact_email, v.is_approved,
                  u.name as vendor_user_name
           FROM vendor_services vs
           JOIN vendors v ON vs.vendor_id = v.id
           JOIN users u ON v.user_id = u.id
           ORDER BY vs.created_at DESC"""
    )
    return render_template('admin_all_vendor_services.html', services=services)


@admin_bp.route('/vendors/<int:vendor_id>/toggle')
@admin_required
def toggle_vendor(vendor_id):
    vendor = execute_query("SELECT * FROM vendors WHERE id = %s", (vendor_id,), fetch_one=True)
    if vendor:
        new_val = not vendor['is_approved']
        execute_update("UPDATE vendors SET is_approved = %s WHERE id = %s", (new_val, vendor_id))
        flash(f"Vendor {'approved' if new_val else 'disabled'}.", 'success')
    return redirect(url_for('admin.list_vendors'))


@admin_bp.route('/vendors/<int:vendor_id>/services')
@admin_required
def view_vendor_services(vendor_id):
    vendor = execute_query(
        """SELECT v.*, u.name as user_name FROM vendors v JOIN users u ON v.user_id = u.id WHERE v.id = %s""",
        (vendor_id,),
        fetch_one=True
    )
    if not vendor:
        flash('Vendor not found.', 'danger')
        return redirect(url_for('admin.list_vendors'))
    services = execute_query("SELECT * FROM vendor_services WHERE vendor_id = %s", (vendor_id,))
    return render_template('admin_vendor_services.html', vendor=vendor, services=services)


@admin_bp.route('/invitation/<int:inv_id>/delete-image/<int:img_id>')
@admin_required
def delete_image(inv_id, img_id):
    """Delete an image (admin only)"""
    inv = execute_query(
        "SELECT id FROM invitations WHERE id = %s",
        (inv_id,),
        fetch_one=True
    )
    if not inv:
        flash('Not found.', 'danger')
        return redirect(url_for('admin.dashboard'))

    img = execute_query(
        "SELECT image_path FROM wedding_images WHERE id = %s AND invitation_id = %s",
        (img_id, inv_id),
        fetch_one=True
    )
    if img:
        physical_path = Path(current_app.root_path) / 'static' / img['image_path']
        if physical_path.exists():
            physical_path.unlink(missing_ok=True)
        execute_update("DELETE FROM wedding_images WHERE id = %s", (img_id,))
        flash('Image deleted.', 'info')
    return redirect(url_for('admin.upload_images', inv_id=inv_id))


# ==================== PAYMENT TRANSACTION MANAGEMENT ====================

@admin_bp.route('/payments')
def payment_transactions():
    """View all payment transactions"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    vendor_filter = request.args.get('vendor', 'all')
    
    # Base query
    query = """
        SELECT 
            pt.id, pt.booking_id, pt.transaction_type, pt.amount, 
            pt.payment_method, pt.transaction_id, pt.status, 
            pt.created_at, pt.verified_at,
            v.business_name as vendor_name, v.id as vendor_id,
            u.name as host_name, u.email as host_email,
            vb.event_date, vb.status as booking_status,
            vs.title as service_title
        FROM payment_transactions pt
        JOIN vendors v ON pt.vendor_id = v.id
        JOIN users u ON pt.user_id = u.id
        JOIN vendor_bookings vb ON pt.booking_id = vb.id
        LEFT JOIN vendor_services vs ON vb.service_id = vs.id
        WHERE 1=1
    """
    params = []
    
    # Apply filters
    if status_filter != 'all':
        query += " AND pt.status = %s"
        params.append(status_filter)
    
    if vendor_filter != 'all':
        query += " AND v.id = %s"
        params.append(int(vendor_filter))
    
    query += " ORDER BY pt.created_at DESC"
    
    transactions = execute_query(query, tuple(params) if params else None)
    
    # Get all vendors for filter dropdown
    vendors = execute_query("SELECT id, business_name FROM vendors ORDER BY business_name")
    
    # Calculate statistics
    stats = execute_query("""
        SELECT 
            COUNT(*) as total_transactions,
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending_count,
            SUM(CASE WHEN status = 'Verified' THEN 1 ELSE 0 END) as verified_count,
            SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) as rejected_count,
            SUM(amount) as total_amount,
            SUM(CASE WHEN status = 'Verified' THEN amount ELSE 0 END) as verified_amount
        FROM payment_transactions
    """, fetch_one=True)
    
    return render_template('admin_payments.html', 
                         transactions=transactions,
                         vendors=vendors,
                         stats=stats,
                         status_filter=status_filter,
                         vendor_filter=vendor_filter)


@admin_bp.route('/payments/<int:transaction_id>')
def payment_detail(transaction_id):
    """View payment transaction details"""
    transaction = execute_query("""
        SELECT 
            pt.*,
            v.business_name, v.contact_email as vendor_email, v.contact_phone as vendor_phone,
            u.name as host_name, u.email as host_email,
            vb.event_date, vb.status as booking_status, vb.total_amount as booking_amount,
            vb.advance_amount, vb.final_amount, vb.payment_status,
            vs.title as service_title, vs.price as service_price
        FROM payment_transactions pt
        JOIN vendors v ON pt.vendor_id = v.id
        JOIN users u ON pt.user_id = u.id
        JOIN vendor_bookings vb ON pt.booking_id = vb.id
        LEFT JOIN vendor_services vs ON vb.service_id = vs.id
        WHERE pt.id = %s
    """, (transaction_id,), fetch_one=True)
    
    if not transaction:
        flash('Transaction not found.', 'danger')
        return redirect(url_for('admin.payment_transactions'))
    
    # Get all transactions for this booking
    booking_transactions = execute_query("""
        SELECT * FROM payment_transactions 
        WHERE booking_id = %s 
        ORDER BY created_at DESC
    """, (transaction['booking_id'],))
    
    return render_template('admin_payment_detail.html', 
                         transaction=transaction,
                         booking_transactions=booking_transactions)


@admin_bp.route('/payments/export')
def export_payments():
    """Export payment transactions to CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    transactions = execute_query("""
        SELECT 
            pt.id, pt.created_at, pt.transaction_type, pt.amount, 
            pt.payment_method, pt.transaction_id, pt.status, pt.verified_at,
            v.business_name as vendor_name,
            u.name as host_name, u.email as host_email,
            vb.event_date
        FROM payment_transactions pt
        JOIN vendors v ON pt.vendor_id = v.id
        JOIN users u ON pt.user_id = u.id
        JOIN vendor_bookings vb ON pt.booking_id = vb.id
        ORDER BY pt.created_at DESC
    """)
    
    # Create CSV
    si = StringIO()
    writer = csv.writer(si)
    
    # Write header
    writer.writerow(['Transaction ID', 'Date', 'Type', 'Amount', 'Payment Method', 
                    'Transaction Ref', 'Status', 'Verified Date', 'Vendor', 
                    'Host Name', 'Host Email', 'Event Date'])
    
    # Write data
    for t in transactions:
        writer.writerow([
            t['id'],
            t['created_at'].strftime('%Y-%m-%d %H:%M:%S') if t['created_at'] else '',
            t['transaction_type'],
            f"₹{t['amount']:.2f}" if t['amount'] else '',
            t['payment_method'] or '',
            t['transaction_id'] or '',
            t['status'],
            t['verified_at'].strftime('%Y-%m-%d %H:%M:%S') if t['verified_at'] else '',
            t['vendor_name'],
            t['host_name'],
            t['host_email'],
            t['event_date'].strftime('%Y-%m-%d') if t['event_date'] else ''
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=payment_transactions.csv"
    output.headers["Content-type"] = "text/csv"
    return output


# ==================== COMMISSION TRACKING & REPORTING ====================

@admin_bp.route('/commissions')
@admin_required
def commission_dashboard():
    """Commission tracking dashboard with statistics and charts"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    vendor_filter = request.args.get('vendor', 'all')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    # Base query for commission records
    query = """
        SELECT
            cr.id, cr.transaction_id, cr.booking_id, cr.vendor_id,
            cr.transaction_amount, cr.commission_rate, cr.commission_amount,
            cr.status, cr.collected_date, cr.payment_method, cr.reference_number,
            cr.notes, cr.created_at,
            v.business_name as vendor_name, v.contact_email as vendor_email,
            v.contact_phone as vendor_phone,
            pt.transaction_type, pt.payment_method as original_payment_method,
            pt.transaction_id as original_transaction_id,
            u.name as host_name, u.email as host_email,
            vb.event_date, vs.title as service_title
        FROM commission_records cr
        JOIN vendors v ON cr.vendor_id = v.id
        JOIN payment_transactions pt ON cr.transaction_id = pt.id
        JOIN users u ON pt.user_id = u.id
        JOIN vendor_bookings vb ON cr.booking_id = vb.id
        LEFT JOIN vendor_services vs ON vb.service_id = vs.id
        WHERE 1=1
    """
    params = []

    # Apply filters
    if status_filter != 'all':
        query += " AND cr.status = %s"
        params.append(status_filter)

    if vendor_filter != 'all':
        query += " AND v.id = %s"
        params.append(int(vendor_filter))

    if date_from:
        query += " AND DATE(cr.created_at) >= %s"
        params.append(date_from)

    if date_to:
        query += " AND DATE(cr.created_at) <= %s"
        params.append(date_to)

    query += " ORDER BY cr.created_at DESC"

    commissions = execute_query(query, tuple(params) if params else None)

    # Get all vendors for filter dropdown
    vendors = execute_query("SELECT id, business_name FROM vendors ORDER BY business_name")

    # Calculate overall statistics
    stats = execute_query("""
        SELECT
            COUNT(*) as total_records,
            SUM(transaction_amount) as total_transactions,
            SUM(commission_amount) as total_commission,
            SUM(CASE WHEN status = 'Pending' THEN commission_amount ELSE 0 END) as pending_commission,
            SUM(CASE WHEN status = 'Collected' THEN commission_amount ELSE 0 END) as collected_commission,
            SUM(CASE WHEN status = 'Waived' THEN commission_amount ELSE 0 END) as waived_commission,
            COUNT(CASE WHEN status = 'Pending' THEN 1 END) as pending_count,
            COUNT(CASE WHEN status = 'Collected' THEN 1 END) as collected_count,
            COUNT(CASE WHEN status = 'Waived' THEN 1 END) as waived_count
        FROM commission_records
    """, fetch_one=True)

    # Get monthly commission trend (last 6 months)
    monthly_trend = execute_query("""
        SELECT
            DATE_FORMAT(created_at, '%Y-%m') as month,
            SUM(commission_amount) as total_commission,
            SUM(CASE WHEN status = 'Collected' THEN commission_amount ELSE 0 END) as collected,
            SUM(CASE WHEN status = 'Pending' THEN commission_amount ELSE 0 END) as pending
        FROM commission_records
        WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        GROUP BY DATE_FORMAT(created_at, '%Y-%m')
        ORDER BY month DESC
    """)

    # Get top vendors by commission
    top_vendors = execute_query("""
        SELECT
            v.id, v.business_name,
            COUNT(cr.id) as transaction_count,
            SUM(cr.transaction_amount) as total_transactions,
            SUM(cr.commission_amount) as total_commission,
            SUM(CASE WHEN cr.status = 'Collected' THEN cr.commission_amount ELSE 0 END) as collected_commission,
            SUM(CASE WHEN cr.status = 'Pending' THEN cr.commission_amount ELSE 0 END) as pending_commission
        FROM vendors v
        LEFT JOIN commission_records cr ON v.id = cr.vendor_id
        GROUP BY v.id, v.business_name
        HAVING total_commission > 0
        ORDER BY total_commission DESC
        LIMIT 10
    """)

    return render_template('admin_commission_dashboard.html',
                         commissions=commissions,
                         vendors=vendors,
                         stats=stats,
                         monthly_trend=monthly_trend,
                         top_vendors=top_vendors,
                         status_filter=status_filter,
                         vendor_filter=vendor_filter,
                         date_from=date_from,
                         date_to=date_to)


@admin_bp.route('/commissions/<int:commission_id>')
@admin_required
def commission_detail(commission_id):
    """View detailed commission record"""
    commission = execute_query("""
        SELECT
            cr.*,
            v.business_name, v.contact_email as vendor_email,
            v.contact_phone as vendor_phone, v.service_type,
            pt.transaction_type, pt.payment_method as original_payment_method,
            pt.transaction_id as original_transaction_id, pt.status as transaction_status,
            pt.created_at as transaction_date,
            u.name as host_name, u.email as host_email,
            vb.event_date, vb.status as booking_status, vb.total_amount as booking_amount,
            vs.title as service_title, vs.price as service_price,
            admin_user.name as collected_by_name
        FROM commission_records cr
        JOIN vendors v ON cr.vendor_id = v.id
        JOIN payment_transactions pt ON cr.transaction_id = pt.id
        JOIN users u ON pt.user_id = u.id
        JOIN vendor_bookings vb ON cr.booking_id = vb.id
        LEFT JOIN vendor_services vs ON vb.service_id = vs.id
        LEFT JOIN users admin_user ON cr.collected_by = admin_user.id
        WHERE cr.id = %s
    """, (commission_id,), fetch_one=True)

    if not commission:
        flash('Commission record not found.', 'danger')
        return redirect(url_for('admin.commission_dashboard'))

    return render_template('admin_commission_detail.html', commission=commission)


@admin_bp.route('/commissions/<int:commission_id>/collect', methods=['POST'])
@admin_required
def collect_commission(commission_id):
    """Mark commission as collected"""
    payment_method = request.form.get('payment_method', 'Cash')
    reference_number = request.form.get('reference_number', '').strip()
    notes = request.form.get('notes', '').strip()

    # Verify commission exists and is pending
    commission = execute_query(
        "SELECT * FROM commission_records WHERE id = %s",
        (commission_id,),
        fetch_one=True
    )

    if not commission:
        flash('Commission record not found.', 'danger')
        return redirect(url_for('admin.commission_dashboard'))

    if commission['status'] == 'Collected':
        flash('Commission already collected.', 'warning')
        return redirect(url_for('admin.commission_detail', commission_id=commission_id))

    # Update commission record
    from datetime import datetime
    execute_update("""
        UPDATE commission_records
        SET status = 'Collected',
            collected_date = %s,
            collected_by = %s,
            payment_method = %s,
            reference_number = %s,
            notes = %s
        WHERE id = %s
    """, (datetime.now(), g.current_user_id, payment_method, reference_number, notes, commission_id))

    # Update payment transaction commission status
    execute_update("""
        UPDATE payment_transactions
        SET commission_status = 'Collected',
            commission_collected_date = %s
        WHERE id = %s
    """, (datetime.now(), commission['transaction_id']))

    flash(f'Commission of ₹{commission["commission_amount"]:.2f} marked as collected!', 'success')
    return redirect(url_for('admin.commission_detail', commission_id=commission_id))


@admin_bp.route('/commissions/<int:commission_id>/waive', methods=['POST'])
@admin_required
def waive_commission(commission_id):
    """Waive commission (forgive)"""
    reason = request.form.get('reason', '').strip()

    if not reason:
        flash('Please provide a reason for waiving the commission.', 'danger')
        return redirect(url_for('admin.commission_detail', commission_id=commission_id))

    # Verify commission exists
    commission = execute_query(
        "SELECT * FROM commission_records WHERE id = %s",
        (commission_id,),
        fetch_one=True
    )

    if not commission:
        flash('Commission record not found.', 'danger')
        return redirect(url_for('admin.commission_dashboard'))

    # Update commission record
    execute_update("""
        UPDATE commission_records
        SET status = 'Waived',
            notes = %s
        WHERE id = %s
    """, (f"Waived: {reason}", commission_id))

    # Update payment transaction commission status
    execute_update("""
        UPDATE payment_transactions
        SET commission_status = 'Waived',
            commission_notes = %s
        WHERE id = %s
    """, (f"Waived: {reason}", commission['transaction_id']))

    flash(f'Commission of ₹{commission["commission_amount"]:.2f} has been waived.', 'info')
    return redirect(url_for('admin.commission_detail', commission_id=commission_id))


@admin_bp.route('/commissions/vendor/<int:vendor_id>')
@admin_required
def vendor_commission_report(vendor_id):
    """Detailed commission report for a specific vendor"""
    vendor = execute_query(
        "SELECT * FROM vendors WHERE id = %s",
        (vendor_id,),
        fetch_one=True
    )

    if not vendor:
        flash('Vendor not found.', 'danger')
        return redirect(url_for('admin.commission_dashboard'))

    # Get all commission records for this vendor
    commissions = execute_query("""
        SELECT
            cr.*,
            pt.transaction_type, pt.payment_method as original_payment_method,
            u.name as host_name,
            vb.event_date, vs.title as service_title
        FROM commission_records cr
        JOIN payment_transactions pt ON cr.transaction_id = pt.id
        JOIN users u ON pt.user_id = u.id
        JOIN vendor_bookings vb ON cr.booking_id = vb.id
        LEFT JOIN vendor_services vs ON vb.service_id = vs.id
        WHERE cr.vendor_id = %s
        ORDER BY cr.created_at DESC
    """, (vendor_id,))

    # Get vendor statistics
    vendor_stats = execute_query("""
        SELECT
            COUNT(*) as total_records,
            SUM(transaction_amount) as total_transactions,
            SUM(commission_amount) as total_commission,
            SUM(CASE WHEN status = 'Collected' THEN commission_amount ELSE 0 END) as collected_commission,
            SUM(CASE WHEN status = 'Pending' THEN commission_amount ELSE 0 END) as pending_commission,
            SUM(CASE WHEN status = 'Waived' THEN commission_amount ELSE 0 END) as waived_commission
        FROM commission_records
        WHERE vendor_id = %s
    """, (vendor_id,), fetch_one=True)

    # Get monthly breakdown
    monthly_breakdown = execute_query("""
        SELECT
            DATE_FORMAT(created_at, '%Y-%m') as month,
            COUNT(*) as transaction_count,
            SUM(transaction_amount) as total_transactions,
            SUM(commission_amount) as total_commission,
            SUM(CASE WHEN status = 'Collected' THEN commission_amount ELSE 0 END) as collected,
            SUM(CASE WHEN status = 'Pending' THEN commission_amount ELSE 0 END) as pending
        FROM commission_records
        WHERE vendor_id = %s
        GROUP BY DATE_FORMAT(created_at, '%Y-%m')
        ORDER BY month DESC
        LIMIT 12
    """, (vendor_id,))

    return render_template('admin_vendor_commission_report.html',
                         vendor=vendor,
                         commissions=commissions,
                         vendor_stats=vendor_stats,
                         monthly_breakdown=monthly_breakdown)


@admin_bp.route('/commissions/export')
@admin_required
def export_commissions():
    """Export commission records to CSV"""
    import csv
    from io import StringIO
    from flask import make_response

    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    vendor_filter = request.args.get('vendor', 'all')

    query = """
        SELECT
            cr.id, cr.created_at, cr.transaction_amount, cr.commission_rate,
            cr.commission_amount, cr.status, cr.collected_date, cr.payment_method,
            cr.reference_number,
            v.business_name as vendor_name, v.contact_email as vendor_email,
            pt.transaction_type, pt.transaction_id as original_transaction_id,
            u.name as host_name, vb.event_date
        FROM commission_records cr
        JOIN vendors v ON cr.vendor_id = v.id
        JOIN payment_transactions pt ON cr.transaction_id = pt.id
        JOIN users u ON pt.user_id = u.id
        JOIN vendor_bookings vb ON cr.booking_id = vb.id
        WHERE 1=1
    """
    params = []

    if status_filter != 'all':
        query += " AND cr.status = %s"
        params.append(status_filter)

    if vendor_filter != 'all':
        query += " AND v.id = %s"
        params.append(int(vendor_filter))

    query += " ORDER BY cr.created_at DESC"

    records = execute_query(query, tuple(params) if params else None)

    # Create CSV
    si = StringIO()
    writer = csv.writer(si)

    # Write header
    writer.writerow([
        'Commission ID', 'Date', 'Vendor Name', 'Vendor Email',
        'Transaction Type', 'Transaction Amount', 'Commission Rate (%)',
        'Commission Amount', 'Status', 'Collected Date', 'Payment Method',
        'Reference Number', 'Host Name', 'Event Date', 'Original Transaction ID'
    ])

    # Write data
    for r in records:
        writer.writerow([
            r['id'],
            r['created_at'].strftime('%Y-%m-%d %H:%M:%S') if r['created_at'] else '',
            r['vendor_name'],
            r['vendor_email'],
            r['transaction_type'],
            f"₹{r['transaction_amount']:.2f}" if r['transaction_amount'] else '',
            f"{r['commission_rate']:.2f}%" if r['commission_rate'] else '',
            f"₹{r['commission_amount']:.2f}" if r['commission_amount'] else '',
            r['status'],
            r['collected_date'].strftime('%Y-%m-%d') if r['collected_date'] else '',
            r['payment_method'] or '',
            r['reference_number'] or '',
            r['host_name'],
            r['event_date'].strftime('%Y-%m-%d') if r['event_date'] else '',
            r['original_transaction_id'] or ''
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=commission_records.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@admin_bp.route('/commissions/summary')
@admin_required
def commission_summary():
    """Monthly commission summary report"""
    # Get monthly summaries
    summaries = execute_query("""
        SELECT
            cs.*,
            v.business_name as vendor_name
        FROM commission_summary cs
        JOIN vendors v ON cs.vendor_id = v.id
        ORDER BY cs.year DESC, cs.month DESC, v.business_name
    """)

    # Get overall summary by month
    monthly_totals = execute_query("""
        SELECT
            year, month,
            SUM(total_transactions) as total_transactions,
            SUM(total_commission) as total_commission,
            SUM(collected_commission) as collected_commission,
            SUM(pending_commission) as pending_commission,
            SUM(transaction_count) as transaction_count
        FROM commission_summary
        GROUP BY year, month
        ORDER BY year DESC, month DESC
    """)

    return render_template('admin_commission_summary.html',
                         summaries=summaries,
                         monthly_totals=monthly_totals)
