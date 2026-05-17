"""
Wedding Management System - Main Flask Application
Session-based auth, invitation links, private gallery
"""
import os
from pathlib import Path
from flask import Flask, session, redirect, url_for, render_template
from werkzeug.security import check_password_hash, generate_password_hash

from config import SECRET_KEY, UPLOAD_FOLDER, VENDOR_UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from db import execute_query, execute_update

# ============================================
# Create Flask App
# ============================================
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload folders exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
VENDOR_UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


# ============================================
# Auth Helpers (used by decorators)
# ============================================
def get_current_user():
    """Get logged-in user from session, or None (admin or vendor)"""
    if 'user_id' not in session:
        return None
    user = execute_query(
        "SELECT id, name, email, role FROM users WHERE id = %s",
        (session['user_id'],),
        fetch_one=True
    )
    return user


def is_admin():
    """Check if current user is admin"""
    user = get_current_user()
    return user and user['role'] == 'admin'


def is_host():
    """Check if current user is host"""
    user = get_current_user()
    return user and user['role'] == 'host'


# ============================================
# Register Blueprints
# ============================================
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.host import host_bp
from blueprints.vendor import vendor_bp
from blueprints.invitation import invitation_bp
from blueprints.gallery import gallery_bp
from blueprints.rsvp import rsvp_bp
from blueprints.marketplace import marketplace_bp
from blueprints.chat import chat_bp

app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(host_bp)
app.register_blueprint(vendor_bp)
app.register_blueprint(invitation_bp)  # Routes: /invite/<token>
app.register_blueprint(gallery_bp, url_prefix='/gallery')
app.register_blueprint(rsvp_bp)  # Routes: /rsvp/<token>
app.register_blueprint(marketplace_bp)  # Routes: /marketplace
app.register_blueprint(chat_bp)  # Routes: /chat


# ============================================
# Root redirect - choose Admin or Vendor login
# ============================================
@app.route('/')
def index():
    """Landing: redirect logged-in users, else show login choice"""
    if 'user_id' in session:
        user = execute_query("SELECT role FROM users WHERE id = %s", (session['user_id'],), fetch_one=True)
        if user:
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            if user['role'] == 'host':
                return redirect(url_for('host.dashboard'))
            if user['role'] == 'vendor':
                return redirect(url_for('vendor.dashboard'))
    return render_template('index.html')


# ============================================
# Context Processor - make user available in templates
# ============================================
@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())


@app.context_processor
def inject_wedding_countdown():
    """Inject wedding date for countdown timer across all pages"""
    wedding_datetime = None
    
    if 'user_id' in session:
        user = get_current_user()
        if user:
            # For hosts: get their wedding date from invitations
            if user['role'] == 'host':
                invitation = execute_query(
                    """SELECT i.wedding_date, we.event_time 
                       FROM invitations i
                       LEFT JOIN wedding_events we ON we.invitation_id = i.id
                       WHERE i.user_id = %s AND i.is_active = 1
                       ORDER BY i.wedding_date ASC, we.event_time ASC
                       LIMIT 1""",
                    (user['id'],),
                    fetch_one=True
                )
                if invitation and invitation['wedding_date']:
                    # Combine date and time if available
                    date_str = invitation['wedding_date'].strftime('%Y-%m-%d')
                    if invitation.get('event_time'):
                        time_obj = invitation['event_time']
                        if hasattr(time_obj, 'total_seconds'):
                            secs = int(time_obj.total_seconds())
                            time_str = f"{secs // 3600:02d}:{(secs % 3600) // 60:02d}:00"
                        else:
                            time_str = str(time_obj)
                    else:
                        time_str = "00:00:00"
                    wedding_datetime = f"{date_str} {time_str}"
    
    # For guests viewing invitation (no login required)
    elif 'guest_invitation_id' in session:
        invitation = execute_query(
            """SELECT i.wedding_date, we.event_time 
               FROM invitations i
               LEFT JOIN wedding_events we ON we.invitation_id = i.id
               WHERE i.id = %s AND i.is_active = 1
               ORDER BY we.event_date ASC, we.event_time ASC
               LIMIT 1""",
            (session['guest_invitation_id'],),
            fetch_one=True
        )
        if invitation and invitation['wedding_date']:
            date_str = invitation['wedding_date'].strftime('%Y-%m-%d')
            if invitation.get('event_time'):
                time_obj = invitation['event_time']
                if hasattr(time_obj, 'total_seconds'):
                    secs = int(time_obj.total_seconds())
                    time_str = f"{secs // 3600:02d}:{(secs % 3600) // 60:02d}:00"
                else:
                    time_str = str(time_obj)
            else:
                time_str = "00:00:00"
            wedding_datetime = f"{date_str} {time_str}"
    
    return dict(wedding_datetime=wedding_datetime)


# ============================================
# Error Handlers
# ============================================
@app.errorhandler(404)
def not_found(e):
    return "Page not found", 404


@app.errorhandler(500)
def server_error(e):
    return "Internal server error", 500


@app.errorhandler(RuntimeError)
def db_connection_error(e):
    """Show friendly message when MySQL is not running"""
    if "Database connection failed" in str(e):
        return (
            "<h2>Database Connection Failed</h2>"
            "<p>MySQL is not running or not reachable.</p>"
            "<p><b>Fix:</b> Open XAMPP Control Panel and start <b>MySQL</b>.</p>"
            "<p>Then ensure database <code>wedding_db</code> exists (run database.sql in phpMyAdmin).</p>",
            503
        )
    raise e  # Re-raise other RuntimeErrors


@app.errorhandler(413)
def too_large(e):
    return "File too large (max 16MB)", 413


# ============================================
# Run Application
# ============================================
if __name__ == '__main__':
    # host='0.0.0.0' allows access from other devices on the same network
    app.run(debug=True, host='0.0.0.0', port=5000)
