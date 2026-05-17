"""
RSVP Blueprint - Guest RSVP form via shareable link
URL: /rsvp/<token>
No login required. Guests can confirm/decline attendance.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import execute_query, execute_update
from datetime import datetime

rsvp_bp = Blueprint('rsvp', __name__, url_prefix='/rsvp')


@rsvp_bp.route('/<token>', methods=['GET', 'POST'])
def rsvp_form(token):
    """
    Display unified invitation page with RSVP form for guest with valid token.
    Handles both GET (show form) and POST (submit response).
    """
    # Fetch guest and invitation details
    guest = execute_query(
        """SELECT g.*, i.bride_name, i.groom_name, i.wedding_date, i.venue, i.id as invitation_id, i.invite_token, i.profile_image, i.message
           FROM guests g
           JOIN invitations i ON g.invitation_id = i.id
           WHERE g.rsvp_token = %s AND i.is_active = 1""",
        (token,),
        fetch_one=True
    )
    
    if not guest:
        return render_template('rsvp_error.html', 
                             message='This RSVP link is invalid or has expired.'), 404
    
    # POST request - process RSVP submission
    if request.method == 'POST':
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
        
        if not rsvp_status or rsvp_status not in ['Confirmed', 'Declined']:
            flash('Please select whether you will attend.', 'danger')
            return redirect(request.url)
        
        # Update guest RSVP
        execute_update(
            """UPDATE guests 
               SET rsvp_status = %s, 
                   rsvp_response = %s, 
                   rsvp_submitted_at = %s,
                   guest_count = %s
               WHERE rsvp_token = %s""",
            (rsvp_status, rsvp_response, datetime.now(), guest_count, token)
        )
        
        return render_template('rsvp_success.html', 
                             guest=guest, 
                             rsvp_status=rsvp_status,
                             guest_count=guest_count)
    
    # GET request - show unified invitation page with RSVP form
    # Fetch wedding events for display
    events = execute_query(
        """SELECT event_name, event_date, event_time, venue, description
           FROM wedding_events 
           WHERE invitation_id = %s 
           ORDER BY event_date, event_time""",
        (guest['invitation_id'],)
    )
    
    # Format event times
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
    
    # Fetch gallery images
    images = execute_query(
        "SELECT * FROM wedding_images WHERE invitation_id = %s ORDER BY album_name, upload_date DESC",
        (guest['invitation_id'],)
    )
    
    # Group images by album
    albums = {}
    for img in images:
        album = img.get('album_name') or 'Wedding Photos'
        if album not in albums:
            albums[album] = []
        albums[album].append(img)
    
    # Create invitation object from guest data
    invitation = {
        'id': guest['invitation_id'],
        'bride_name': guest['bride_name'],
        'groom_name': guest['groom_name'],
        'wedding_date': guest['wedding_date'],
        'venue': guest['venue'],
        'message': guest.get('message'),
        'profile_image': guest.get('profile_image'),
        'invite_token': guest['invite_token']
    }
    
    return render_template('invitation_unified.html', 
                         invitation=invitation,
                         guest=guest, 
                         events=events,
                         images=images,
                         albums=albums)
