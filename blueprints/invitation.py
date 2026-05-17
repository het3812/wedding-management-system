"""
Invitation Blueprint - Public invitation view via shareable link
URL: /invite/<token>
No login required. Valid token grants access; stores token in session for gallery access.
"""
from flask import Blueprint, render_template, request, session, abort, redirect, url_for, flash
from datetime import datetime

from db import execute_query, execute_update

invitation_bp = Blueprint('invitation', __name__, url_prefix='')


@invitation_bp.route('/invite/<token>')
def view_invitation(token):
    """
    Display unified wedding invitation page with events, RSVP, and gallery.
    Validates token, handles invalid/expired gracefully.
    Stores token in session so guest can access gallery.
    """
    inv = execute_query(
        """SELECT id, bride_name, groom_name, wedding_date, venue, message, invite_token, is_active, profile_image
           FROM invitations WHERE invite_token = %s""",
        (token,),
        fetch_one=True
    )

    if not inv:
        return render_template('invitation_error.html', message='This invitation link is invalid or does not exist.'), 404

    if not inv['is_active']:
        return render_template('invitation_error.html', message='This invitation has been deactivated by the host.'), 403

    # Store token in session - guest can now access gallery for this wedding
    session['guest_invite_token'] = token
    session['guest_invitation_id'] = inv['id']

    # Fetch wedding events (schedule)
    events = execute_query(
        "SELECT * FROM wedding_events WHERE invitation_id = %s ORDER BY event_date, event_time",
        (inv['id'],)
    )
    # Format event_time for display (MySQL returns timedelta)
    for e in events:
        if e.get('event_time'):
            t = e['event_time']
            if hasattr(t, 'total_seconds'):
                secs = int(t.total_seconds())
                e['time_display'] = f"{secs // 3600:02d}:{(secs % 3600) // 60:02d}"
            else:
                e['time_display'] = str(t)[:5] if t else ''
        else:
            e['time_display'] = ''

    # Try to find guest info for RSVP (if they have a personal RSVP link)
    guest = None
    # Check if there's a guest with matching invitation who might be viewing
    # We'll pass None if no specific guest, they can still view invitation
    
    # Fetch gallery images
    images = execute_query(
        "SELECT * FROM wedding_images WHERE invitation_id = %s ORDER BY album_name, upload_date DESC",
        (inv['id'],)
    )
    
    # Group images by album
    albums = {}
    for img in images:
        album = img.get('album_name') or 'Wedding Photos'
        if album not in albums:
            albums[album] = []
        albums[album].append(img)

    return render_template('invitation_unified.html', 
                         invitation=inv, 
                         events=events, 
                         guest=guest,
                         images=images,
                         albums=albums)



@invitation_bp.route('/invite/<token>/rsvp', methods=['POST'])
def submit_general_rsvp(token):
    """
    Handle RSVP submission from general invitation link.
    Creates a new guest record if they don't exist.
    """
    # Verify invitation exists and is active
    inv = execute_query(
        "SELECT id, bride_name, groom_name FROM invitations WHERE invite_token = %s AND is_active = 1",
        (token,),
        fetch_one=True
    )
    
    if not inv:
        flash('Invalid invitation link.', 'danger')
        return redirect(url_for('invitation.view_invitation', token=token))
    
    # Get form data
    guest_name = request.form.get('guest_name', '').strip()
    guest_email = request.form.get('guest_email', '').strip()
    guest_phone = request.form.get('guest_phone', '').strip()
    rsvp_status = request.form.get('rsvp_status')
    rsvp_response = request.form.get('rsvp_response', '').strip()
    guest_count = request.form.get('guest_count', '1')
    
    # Convert guest_count to integer
    try:
        guest_count = int(guest_count)
        if guest_count < 1:
            guest_count = 1
        elif guest_count > 10:
            guest_count = 10
    except (ValueError, TypeError):
        guest_count = 1
    
    if not guest_name or not rsvp_status:
        flash('Please provide your name and RSVP status.', 'danger')
        return redirect(url_for('invitation.view_invitation', token=token))
    
    if not guest_phone:
        flash('Please provide your phone number.', 'danger')
        return redirect(url_for('invitation.view_invitation', token=token))
    
    if rsvp_status not in ['Confirmed', 'Declined']:
        flash('Invalid RSVP status.', 'danger')
        return redirect(url_for('invitation.view_invitation', token=token))
    
    # Check if guest already exists (by name and email/phone)
    existing_guest = None
    if guest_email:
        existing_guest = execute_query(
            "SELECT id FROM guests WHERE invitation_id = %s AND email = %s",
            (inv['id'], guest_email),
            fetch_one=True
        )
    
    if existing_guest:
        # Update existing guest
        execute_update(
            """UPDATE guests 
               SET rsvp_status = %s, 
                   rsvp_response = %s, 
                   rsvp_submitted_at = %s,
                   guest_count = %s,
                   phone = %s
               WHERE id = %s""",
            (rsvp_status, rsvp_response, datetime.now(), guest_count, guest_phone, existing_guest['id'])
        )
    else:
        # Create new guest record
        import secrets
        rsvp_token = secrets.token_urlsafe(32)
        
        execute_update(
            """INSERT INTO guests 
               (invitation_id, name, email, phone, rsvp_status, rsvp_response, 
                rsvp_submitted_at, guest_count, rsvp_token, category)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Friend')""",
            (inv['id'], guest_name, guest_email or None, guest_phone or None, 
             rsvp_status, rsvp_response, datetime.now(), guest_count, rsvp_token)
        )
    
    # Show success message
    flash(f'Thank you for your RSVP, {guest_name}! Your response has been recorded.', 'success')
    return redirect(url_for('invitation.view_invitation', token=token))
