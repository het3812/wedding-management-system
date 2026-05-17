"""
Host Blueprint - Wedding host (bride/groom) dashboard
Manages own invitations, guests, events, gallery - no vendor management
"""
import secrets
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, g, session

from db import execute_query, execute_update
from blueprints.auth import host_required
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from werkzeug.utils import secure_filename

host_bp = Blueprint('host', __name__, url_prefix='/host')


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_invite_token():
    """Generate a cryptographically secure unique token for invitation URL"""
    return secrets.token_urlsafe(32)


# ========== Login ==========
@host_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Host login - wedding couple / event host"""
    from werkzeug.security import check_password_hash

    if request.method == 'GET':
        if 'user_id' in session:
            user = execute_query("SELECT role FROM users WHERE id = %s", (session['user_id'],), fetch_one=True)
            if user and user['role'] == 'host':
                return redirect(url_for('host.dashboard'))
        return render_template('host_login.html')

    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    if not email or not password:
        flash('Email and password are required.', 'danger')
        return render_template('host_login.html')

    user = execute_query(
        "SELECT id, name, email, password, role FROM users WHERE email = %s",
        (email,),
        fetch_one=True
    )

    if not user or user['role'] != 'host':
        flash('Invalid credentials or not a host account.', 'danger')
        return render_template('host_login.html')

    if not check_password_hash(user['password'], password):
        flash('Invalid email or password.', 'danger')
        return render_template('host_login.html')

    session.clear()
    session['user_id'] = user['id']
    session['user_role'] = 'host'
    flash(f'Welcome, {user["name"]}!', 'success')
    return redirect(url_for('host.dashboard'))


@host_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))


# ========== Registration (self-register as host) ==========
@host_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Host self-registration - anyone can create a host account"""
    from werkzeug.security import generate_password_hash

    if request.method == 'GET':
        return render_template('host_register.html')

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    if not all([name, email, password]):
        flash('Name, email and password are required.', 'danger')
        return render_template('host_register.html')

    if len(password) < 6:
        flash('Password must be at least 6 characters.', 'danger')
        return render_template('host_register.html')

    existing = execute_query("SELECT id FROM users WHERE email = %s", (email,), fetch_one=True)
    if existing:
        flash('This email is already registered. Please login or use another email.', 'danger')
        return render_template('host_register.html')

    hashed = generate_password_hash(password)
    execute_update(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'host')",
        (name, email, hashed)
    )
    flash('Account created successfully! You can now login.', 'success')
    return redirect(url_for('host.login'))


# ========== Dashboard (own invitations only) ==========
@host_bp.route('/')
@host_required
def dashboard():
    """Host dashboard: own invitations only"""
    invitations = execute_query(
        """SELECT id, bride_name, groom_name, wedding_date, venue, invite_token, is_active, created_at
           FROM invitations WHERE user_id = %s ORDER BY created_at DESC""",
        (g.current_user_id,)
    )
    return render_template('host_dashboard.html', invitations=invitations)


# ========== Invitation CRUD ==========
@host_bp.route('/invitation/create', methods=['GET', 'POST'])
@host_required
def create_invitation():
    if request.method == 'GET':
        return render_template('host_invitation_form.html', invitation=None)

    bride_name = request.form.get('bride_name', '').strip()
    groom_name = request.form.get('groom_name', '').strip()
    wedding_date = request.form.get('wedding_date', '').strip()
    venue = request.form.get('venue', '').strip()
    message = request.form.get('message', '').strip()

    if not all([bride_name, groom_name, wedding_date, venue]):
        flash('Bride name, Groom name, Wedding date, and Venue are required.', 'danger')
        return render_template('host_invitation_form.html', invitation=None)

    token = generate_invite_token()
    while execute_query("SELECT id FROM invitations WHERE invite_token = %s", (token,), fetch_one=True):
        token = generate_invite_token()

    execute_update(
        """INSERT INTO invitations (user_id, bride_name, groom_name, wedding_date, venue, message, invite_token)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (g.current_user_id, bride_name, groom_name, wedding_date, venue, message, token)
    )
    flash('Invitation created successfully! Share the link below.', 'success')
    return redirect(url_for('host.dashboard'))


@host_bp.route('/invitation/<int:inv_id>/edit', methods=['GET', 'POST'])
@host_required
def edit_invitation(inv_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s AND user_id = %s",
        (inv_id, g.current_user_id),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('host.dashboard'))

    if request.method == 'GET':
        return render_template('host_invitation_form.html', invitation=inv)

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
        return render_template('host_invitation_form.html', invitation=inv)

    # Handle profile image upload
    profile_image = inv.get('profile_image')
    if 'profile_image' in request.files and request.files['profile_image'].filename:
        file = request.files['profile_image']
        if file and allowed_file(file.filename):
            upload_dir = UPLOAD_FOLDER / str(inv_id) / 'profile'
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Delete old profile image if exists
            if profile_image:
                from flask import current_app
                old_path = Path(current_app.root_path) / 'static' / profile_image
                if old_path.exists():
                    old_path.unlink(missing_ok=True)
            
            filename = secure_filename(file.filename)
            unique_name = f"profile_{secrets.token_hex(4)}_{filename}"
            filepath = upload_dir / unique_name
            file.save(str(filepath))
            profile_image = f"uploads/{inv_id}/profile/{unique_name}"

    execute_update(
        """UPDATE invitations SET bride_name=%s, groom_name=%s, wedding_date=%s, venue=%s, message=%s, is_active=%s, profile_image=%s
           WHERE id=%s AND user_id=%s""",
        (bride_name, groom_name, wedding_date, venue, message, is_active, profile_image, inv_id, g.current_user_id)
    )
    flash('Invitation updated.', 'success')
    return redirect(url_for('host.dashboard'))


# ========== Image Upload ==========
@host_bp.route('/invitation/<int:inv_id>/upload', methods=['GET', 'POST'])
@host_required
def upload_images(inv_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s AND user_id = %s",
        (inv_id, g.current_user_id),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('host.dashboard'))

    if request.method == 'GET':
        images = execute_query("SELECT * FROM wedding_images WHERE invitation_id = %s ORDER BY upload_date DESC", (inv_id,))
        return render_template('host_upload.html', invitation=inv, images=images)

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

    return redirect(url_for('host.upload_images', inv_id=inv_id))


# ========== Guests ==========
@host_bp.route('/invitation/<int:inv_id>/guests')
@host_required
def manage_guests(inv_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s AND user_id = %s",
        (inv_id, g.current_user_id),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('host.dashboard'))
    guests = execute_query(
        "SELECT * FROM guests WHERE invitation_id = %s ORDER BY category, name",
        (inv_id,)
    )
    return render_template('host_guests.html', invitation=inv, guests=guests)


@host_bp.route('/invitation/<int:inv_id>/guests/add', methods=['GET', 'POST'])
@host_required
def add_guest(inv_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s AND user_id = %s",
        (inv_id, g.current_user_id),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('host.dashboard'))

    if request.method == 'GET':
        return render_template('host_guest_form.html', invitation=inv, guest=None)

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    category = request.form.get('category', 'Friend')
    if not name:
        flash('Guest name required.', 'danger')
        return render_template('host_guest_form.html', invitation=inv, guest=None)

    # Generate unique RSVP token
    rsvp_token = secrets.token_urlsafe(32)
    while execute_query("SELECT id FROM guests WHERE rsvp_token = %s", (rsvp_token,), fetch_one=True):
        rsvp_token = secrets.token_urlsafe(32)

    execute_update(
        """INSERT INTO guests (invitation_id, name, email, phone, category, rsvp_token) 
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (inv_id, name, email or None, phone or None, category, rsvp_token)
    )
    flash('Guest added with RSVP link.', 'success')
    return redirect(url_for('host.manage_guests', inv_id=inv_id))


@host_bp.route('/invitation/<int:inv_id>/guests/<int:guest_id>/edit', methods=['GET', 'POST'])
@host_required
def edit_guest(inv_id, guest_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s AND user_id = %s",
        (inv_id, g.current_user_id),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('host.dashboard'))
    guest = execute_query(
        "SELECT * FROM guests WHERE id = %s AND invitation_id = %s",
        (guest_id, inv_id),
        fetch_one=True
    )
    if not guest:
        flash('Guest not found.', 'danger')
        return redirect(url_for('host.manage_guests', inv_id=inv_id))

    if request.method == 'GET':
        return render_template('host_guest_form.html', invitation=inv, guest=guest)

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    category = request.form.get('category', 'Friend')
    rsvp_status = request.form.get('rsvp_status', 'Pending')
    if not name:
        flash('Guest name required.', 'danger')
        return render_template('host_guest_form.html', invitation=inv, guest=guest)

    # Generate RSVP token if not exists
    if not guest.get('rsvp_token'):
        rsvp_token = secrets.token_urlsafe(32)
        while execute_query("SELECT id FROM guests WHERE rsvp_token = %s", (rsvp_token,), fetch_one=True):
            rsvp_token = secrets.token_urlsafe(32)
        execute_update(
            """UPDATE guests SET name=%s, email=%s, phone=%s, category=%s, rsvp_status=%s, rsvp_token=%s
               WHERE id=%s AND invitation_id=%s""",
            (name, email or None, phone or None, category, rsvp_status, rsvp_token, guest_id, inv_id)
        )
    else:
        execute_update(
            """UPDATE guests SET name=%s, email=%s, phone=%s, category=%s, rsvp_status=%s
               WHERE id=%s AND invitation_id=%s""",
            (name, email or None, phone or None, category, rsvp_status, guest_id, inv_id)
        )
    flash('Guest updated.', 'success')
    return redirect(url_for('host.manage_guests', inv_id=inv_id))


@host_bp.route('/invitation/<int:inv_id>/guests/<int:guest_id>/delete')
@host_required
def delete_guest(inv_id, guest_id):
    inv = execute_query(
        "SELECT id FROM invitations WHERE id = %s AND user_id = %s",
        (inv_id, g.current_user_id),
        fetch_one=True
    )
    if inv:
        execute_update("DELETE FROM guests WHERE id = %s AND invitation_id = %s", (guest_id, inv_id))
        flash('Guest removed.', 'info')
    return redirect(url_for('host.manage_guests', inv_id=inv_id))


@host_bp.route('/invitation/<int:inv_id>/guests/<int:guest_id>/view-rsvp')
@host_required
def view_guest_rsvp(inv_id, guest_id):
    """View detailed RSVP response from a guest"""
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s AND user_id = %s",
        (inv_id, g.current_user_id),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('host.dashboard'))
    
    guest = execute_query(
        "SELECT * FROM guests WHERE id = %s AND invitation_id = %s",
        (guest_id, inv_id),
        fetch_one=True
    )
    if not guest:
        flash('Guest not found.', 'danger')
        return redirect(url_for('host.manage_guests', inv_id=inv_id))
    
    return render_template('host_guest_rsvp_detail.html', invitation=inv, guest=guest)


# ========== Events ==========
@host_bp.route('/invitation/<int:inv_id>/events')
@host_required
def manage_events(inv_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s AND user_id = %s",
        (inv_id, g.current_user_id),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('host.dashboard'))
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
    return render_template('host_events.html', invitation=inv, events=events)


@host_bp.route('/invitation/<int:inv_id>/events/add', methods=['GET', 'POST'])
@host_required
def add_event(inv_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s AND user_id = %s",
        (inv_id, g.current_user_id),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('host.dashboard'))

    if request.method == 'GET':
        return render_template('host_event_form.html', invitation=inv, event=None)

    event_name = request.form.get('event_name', '').strip()
    event_date = request.form.get('event_date', '').strip()
    event_time = request.form.get('event_time', '').strip()
    venue = request.form.get('venue', '').strip()
    if not all([event_name, event_date, venue]):
        flash('Event name, date, and venue required.', 'danger')
        return render_template('host_event_form.html', invitation=inv, event=None)

    execute_update(
        """INSERT INTO wedding_events (invitation_id, event_name, event_date, event_time, venue)
           VALUES (%s, %s, %s, %s, %s)""",
        (inv_id, event_name, event_date, event_time or None, venue)
    )
    flash('Event added.', 'success')
    return redirect(url_for('host.manage_events', inv_id=inv_id))


@host_bp.route('/invitation/<int:inv_id>/events/<int:evt_id>/edit', methods=['GET', 'POST'])
@host_required
def edit_event(inv_id, evt_id):
    inv = execute_query(
        "SELECT * FROM invitations WHERE id = %s AND user_id = %s",
        (inv_id, g.current_user_id),
        fetch_one=True
    )
    if not inv:
        flash('Invitation not found.', 'danger')
        return redirect(url_for('host.dashboard'))
    event = execute_query(
        "SELECT * FROM wedding_events WHERE id = %s AND invitation_id = %s",
        (evt_id, inv_id),
        fetch_one=True
    )
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('host.manage_events', inv_id=inv_id))

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
        return render_template('host_event_form.html', invitation=inv, event=event)

    event_name = request.form.get('event_name', '').strip()
    event_date = request.form.get('event_date', '').strip()
    event_time = request.form.get('event_time', '').strip()
    venue = request.form.get('venue', '').strip()
    if not all([event_name, event_date, venue]):
        flash('Event name, date, and venue required.', 'danger')
        return render_template('host_event_form.html', invitation=inv, event=event)

    execute_update(
        """UPDATE wedding_events SET event_name=%s, event_date=%s, event_time=%s, venue=%s
           WHERE id=%s AND invitation_id=%s""",
        (event_name, event_date, event_time or None, venue, evt_id, inv_id)
    )
    flash('Event updated.', 'success')
    return redirect(url_for('host.manage_events', inv_id=inv_id))


@host_bp.route('/invitation/<int:inv_id>/events/<int:evt_id>/delete')
@host_required
def delete_event(inv_id, evt_id):
    inv = execute_query(
        "SELECT id FROM invitations WHERE id = %s AND user_id = %s",
        (inv_id, g.current_user_id),
        fetch_one=True
    )
    if inv:
        execute_update("DELETE FROM wedding_events WHERE id = %s AND invitation_id = %s", (evt_id, inv_id))
        flash('Event deleted.', 'info')
    return redirect(url_for('host.manage_events', inv_id=inv_id))


# ========== Delete Image ==========
@host_bp.route('/invitation/<int:inv_id>/delete-image/<int:img_id>')
@host_required
def delete_image(inv_id, img_id):
    inv = execute_query(
        "SELECT id FROM invitations WHERE id = %s AND user_id = %s",
        (inv_id, g.current_user_id),
        fetch_one=True
    )
    if not inv:
        flash('Not found.', 'danger')
        return redirect(url_for('host.dashboard'))

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
    return redirect(url_for('host.upload_images', inv_id=inv_id))
