"""
Authentication Blueprint - Login, Logout
Session-based, no JWT
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from db import execute_query, execute_update

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator: require logged-in user (admin)"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapped


def admin_required(f):
    """Decorator: require admin role"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        user = execute_query("SELECT role FROM users WHERE id = %s", (session['user_id'],), fetch_one=True)
        if not user or user['role'] != 'admin':
            flash('Access denied. Admin only.', 'danger')
            return redirect(url_for('auth.login'))
        g.current_user_id = session['user_id']
        return f(*args, **kwargs)
    return wrapped


def host_required(f):
    """Decorator: require host role"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('host.login'))
        user = execute_query("SELECT role FROM users WHERE id = %s", (session['user_id'],), fetch_one=True)
        if not user or user['role'] != 'host':
            flash('Access denied. Host only.', 'danger')
            return redirect(url_for('host.login'))
        g.current_user_id = session['user_id']
        return f(*args, **kwargs)
    return wrapped


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page. Accepts email and password.
    On success: sets session, redirects to admin dashboard.
    """
    if request.method == 'GET':
        # If already logged in, redirect to dashboard
        if 'user_id' in session:
            return redirect(url_for('admin.dashboard'))
        return render_template('login.html')

    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    if not email or not password:
        flash('Email and password are required.', 'danger')
        return render_template('login.html')

    user = execute_query(
        "SELECT id, name, email, password, role FROM users WHERE email = %s",
        (email,),
        fetch_one=True
    )

    if not user:
        flash('Invalid email or password.', 'danger')
        return render_template('login.html')

    if not check_password_hash(user['password'], password):
        flash('Invalid email or password.', 'danger')
        return render_template('login.html')

    # Only allow admin login through this form
    if user['role'] != 'admin':
        flash('Access denied. Admin login only.', 'danger')
        return render_template('login.html')

    # Session-based login
    session.clear()
    session['user_id'] = user['id']
    session['user_role'] = user['role']
    flash(f'Welcome back, {user["name"]}!', 'success')
    return redirect(url_for('admin.dashboard'))


@auth_bp.route('/logout')
def logout():
    """Clear session and redirect to home"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
