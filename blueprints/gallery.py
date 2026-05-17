"""
Gallery Blueprint - View wedding images
Access: Admin (any) OR Guest with valid invite token in session
URL: /gallery/<token>
"""
from flask import Blueprint, render_template, redirect, url_for, session, abort

from db import execute_query
from blueprints.auth import admin_required

gallery_bp = Blueprint('gallery', __name__)


def has_gallery_access(token):
    """
    Check if current user can view gallery for this token.
    Returns (has_access, invitation_dict or None)
    """
    inv = execute_query(
        """SELECT id, user_id, bride_name, groom_name, wedding_date, venue, invite_token, is_active
           FROM invitations WHERE invite_token = %s""",
        (token,),
        fetch_one=True
    )

    if not inv or not inv['is_active']:
        return False, None

    # Admin can access any gallery; Host can access own galleries
    if session.get('user_id'):
        user = execute_query("SELECT role FROM users WHERE id = %s", (session['user_id'],), fetch_one=True)
        if user:
            if user['role'] == 'admin':
                return True, inv
            if user['role'] == 'host' and inv.get('user_id') == session['user_id']:
                return True, inv

    # Guest must have accessed invitation link (token in session)
    if session.get('guest_invite_token') == token:
        return True, inv

    return False, None


@gallery_bp.route('/<token>')
def view_gallery(token):
    """
    Display wedding image gallery.
    Access: Admin OR guest who visited /invite/<token>
    """
    has_access, inv = has_gallery_access(token)

    if not has_access or not inv:
        return render_template('gallery_error.html', message='You do not have access to this gallery.'), 403

    # Fetch images - album_name for album-wise view (after migration)
    try:
        images = execute_query(
            "SELECT id, image_path, upload_date, IFNULL(album_name, 'Main') as album_name FROM wedding_images WHERE invitation_id = %s ORDER BY IFNULL(album_name,'Main'), upload_date DESC",
            (inv['id'],)
        )
    except Exception:
        images = execute_query(
            "SELECT id, image_path, upload_date FROM wedding_images WHERE invitation_id = %s ORDER BY upload_date DESC",
            (inv['id'],)
        )
        for img in images:
            img['album_name'] = 'Main'

    # Group by album for album-wise view
    albums = {}
    for img in images:
        album = img.get('album_name', 'Main')
        if album not in albums:
            albums[album] = []
        albums[album].append(img)

    return render_template('gallery.html', invitation=inv, images=images, albums=albums)
