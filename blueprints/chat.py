"""
Chat Blueprint - Real-time messaging between users and vendors
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify
from db import execute_query, execute_update
from datetime import datetime

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')


def login_required(f):
    """Decorator: require any logged-in user"""
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access chat.', 'warning')
            return redirect(url_for('host.login'))
        g.current_user_id = session['user_id']
        g.current_user = execute_query(
            "SELECT * FROM users WHERE id = %s",
            (session['user_id'],),
            fetch_one=True
        )
        return f(*args, **kwargs)
    return wrapped


@chat_bp.route('/')
@login_required
def index():
    """List all chats for current user"""
    user_role = g.current_user['role']
    
    if user_role == 'vendor':
        # Get vendor's chats
        vendor = execute_query(
            "SELECT id FROM vendors WHERE user_id = %s",
            (g.current_user_id,),
            fetch_one=True
        )
        if not vendor:
            flash('Vendor profile not found.', 'danger')
            return redirect(url_for('vendor.dashboard'))
        
        chats = execute_query("""
            SELECT vc.*, u.name as user_name, u.email as user_email
            FROM vendor_chats vc
            JOIN users u ON vc.user_id = u.id
            WHERE vc.vendor_id = %s
            ORDER BY vc.last_message_at DESC
        """, (vendor['id'],))
    else:
        # Get user's chats
        chats = execute_query("""
            SELECT vc.*, v.business_name, u.name as vendor_name
            FROM vendor_chats vc
            JOIN vendors v ON vc.vendor_id = v.id
            JOIN users u ON v.user_id = u.id
            WHERE vc.user_id = %s
            ORDER BY vc.last_message_at DESC
        """, (g.current_user_id,))
    
    return render_template('chat_list.html', chats=chats, user_role=user_role)


@chat_bp.route('/vendor/<int:vendor_id>')
@login_required
def start_chat(vendor_id):
    """Start or continue chat with a vendor"""
    if g.current_user['role'] == 'vendor':
        flash('Vendors cannot chat with other vendors.', 'warning')
        return redirect(url_for('chat.index'))
    
    # Check if chat exists
    chat = execute_query("""
        SELECT id FROM vendor_chats 
        WHERE vendor_id = %s AND user_id = %s
    """, (vendor_id, g.current_user_id), fetch_one=True)
    
    if not chat:
        # Create new chat
        chat_id = execute_update("""
            INSERT INTO vendor_chats (vendor_id, user_id, last_message, last_message_at)
            VALUES (%s, %s, 'Chat started', %s)
        """, (vendor_id, g.current_user_id, datetime.now()))
    else:
        chat_id = chat['id']
    
    return redirect(url_for('chat.view_chat', chat_id=chat_id))


@chat_bp.route('/<int:chat_id>')
@login_required
def view_chat(chat_id):
    """View chat conversation"""
    # Get chat details
    chat = execute_query("""
        SELECT vc.*, v.business_name, v.id as vendor_id,
               u1.name as user_name, u2.name as vendor_user_name
        FROM vendor_chats vc
        JOIN vendors v ON vc.vendor_id = v.id
        JOIN users u1 ON vc.user_id = u1.id
        JOIN users u2 ON v.user_id = u2.id
        WHERE vc.id = %s
    """, (chat_id,), fetch_one=True)
    
    if not chat:
        flash('Chat not found.', 'danger')
        return redirect(url_for('chat.index'))
    
    # Check access permission
    user_role = g.current_user['role']
    if user_role == 'vendor':
        vendor = execute_query(
            "SELECT id FROM vendors WHERE user_id = %s",
            (g.current_user_id,),
            fetch_one=True
        )
        if not vendor or vendor['id'] != chat['vendor_id']:
            flash('Access denied.', 'danger')
            return redirect(url_for('chat.index'))
    else:
        if chat['user_id'] != g.current_user_id:
            flash('Access denied.', 'danger')
            return redirect(url_for('chat.index'))
    
    # Get messages
    messages = execute_query("""
        SELECT cm.*, u.name as sender_name
        FROM chat_messages cm
        JOIN users u ON cm.sender_id = u.id
        WHERE cm.chat_id = %s
        ORDER BY cm.sent_at ASC
    """, (chat_id,))
    
    # Mark messages as read
    if user_role == 'vendor':
        execute_update(
            "UPDATE chat_messages SET is_read = 1 WHERE chat_id = %s AND sender_type = 'user'",
            (chat_id,)
        )
        execute_update(
            "UPDATE vendor_chats SET unread_vendor = 0 WHERE id = %s",
            (chat_id,)
        )
    else:
        execute_update(
            "UPDATE chat_messages SET is_read = 1 WHERE chat_id = %s AND sender_type = 'vendor'",
            (chat_id,)
        )
        execute_update(
            "UPDATE vendor_chats SET unread_user = 0 WHERE id = %s",
            (chat_id,)
        )
    
    return render_template('chat_view.html', chat=chat, messages=messages, user_role=user_role)


@chat_bp.route('/<int:chat_id>/send', methods=['POST'])
@login_required
def send_message(chat_id):
    """Send a message in chat"""
    message_text = request.form.get('message', '').strip()
    
    if not message_text:
        return jsonify({'success': False, 'error': 'Message cannot be empty'})
    
    # Get chat details
    chat = execute_query(
        "SELECT vendor_id, user_id FROM vendor_chats WHERE id = %s",
        (chat_id,),
        fetch_one=True
    )
    
    if not chat:
        return jsonify({'success': False, 'error': 'Chat not found'})
    
    # Determine sender type
    user_role = g.current_user['role']
    if user_role == 'vendor':
        vendor = execute_query(
            "SELECT id FROM vendors WHERE user_id = %s",
            (g.current_user_id,),
            fetch_one=True
        )
        if not vendor or vendor['id'] != chat['vendor_id']:
            return jsonify({'success': False, 'error': 'Access denied'})
        sender_type = 'vendor'
    else:
        if chat['user_id'] != g.current_user_id:
            return jsonify({'success': False, 'error': 'Access denied'})
        sender_type = 'user'
    
    # Insert message
    execute_update("""
        INSERT INTO chat_messages (chat_id, sender_id, sender_type, message, sent_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (chat_id, g.current_user_id, sender_type, message_text, datetime.now()))
    
    # Update chat last message
    if sender_type == 'vendor':
        execute_update("""
            UPDATE vendor_chats 
            SET last_message = %s, last_message_at = %s, unread_user = unread_user + 1
            WHERE id = %s
        """, (message_text[:100], datetime.now(), chat_id))
    else:
        execute_update("""
            UPDATE vendor_chats 
            SET last_message = %s, last_message_at = %s, unread_vendor = unread_vendor + 1
            WHERE id = %s
        """, (message_text[:100], datetime.now(), chat_id))
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    return redirect(url_for('chat.view_chat', chat_id=chat_id))


@chat_bp.route('/<int:chat_id>/messages')
@login_required
def get_messages(chat_id):
    """API endpoint to get new messages (for polling)"""
    since_id = request.args.get('since', 0, type=int)
    
    messages = execute_query("""
        SELECT cm.*, u.name as sender_name
        FROM chat_messages cm
        JOIN users u ON cm.sender_id = u.id
        WHERE cm.chat_id = %s AND cm.id > %s
        ORDER BY cm.sent_at ASC
    """, (chat_id, since_id))
    
    return jsonify({
        'messages': [{
            'id': m['id'],
            'sender_name': m['sender_name'],
            'sender_type': m['sender_type'],
            'message': m['message'],
            'sent_at': m['sent_at'].strftime('%Y-%m-%d %H:%M:%S'),
            'is_read': m['is_read']
        } for m in messages]
    })
