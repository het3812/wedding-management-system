"""
Initialize database and create default admin user.
Run this ONCE after creating the database and tables (database.sql).
Usage: python init_db.py
"""
import sys
from werkzeug.security import generate_password_hash
from db import get_db_connection


def create_tables(conn):
    """Create tables if they don't exist"""
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('admin', 'host', 'vendor') DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invitations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            bride_name VARCHAR(100) NOT NULL,
            groom_name VARCHAR(100) NOT NULL,
            wedding_date DATE NOT NULL,
            venue VARCHAR(255) NOT NULL,
            message TEXT,
            invite_token VARCHAR(64) UNIQUE NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wedding_images (
            id INT AUTO_INCREMENT PRIMARY KEY,
            invitation_id INT NOT NULL,
            image_path VARCHAR(255) NOT NULL,
            album_name VARCHAR(100) DEFAULT 'Main',
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invitation_id) REFERENCES invitations(id) ON DELETE CASCADE
        )
    """)
    
    # New tables: guests, wedding_events, vendors, vendor_services
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            invitation_id INT NOT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150),
            phone VARCHAR(20),
            category ENUM('Family', 'Friend', 'VIP') DEFAULT 'Friend',
            rsvp_status ENUM('Pending', 'Confirmed', 'Declined') DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invitation_id) REFERENCES invitations(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wedding_events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            invitation_id INT NOT NULL,
            event_name VARCHAR(100) NOT NULL,
            event_date DATE NOT NULL,
            event_time TIME,
            venue VARCHAR(255) NOT NULL,
            sort_order INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invitation_id) REFERENCES invitations(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL UNIQUE,
            business_name VARCHAR(150) NOT NULL,
            service_type VARCHAR(100) NOT NULL,
            contact_email VARCHAR(150) NOT NULL,
            contact_phone VARCHAR(20),
            is_approved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendor_services (
            id INT AUTO_INCREMENT PRIMARY KEY,
            vendor_id INT NOT NULL,
            title VARCHAR(150) NOT NULL,
            description TEXT,
            price DECIMAL(12,2),
            image_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
        )
    """)
    try:
        cursor.execute("CREATE INDEX idx_invite_token ON invitations(invite_token)")
    except Exception:
        pass
    conn.commit()
    cursor.close()


def create_admin(email="admin@wedding.com", password="admin123", name="Admin"):
    """Create default admin user if not exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        print(f"Admin user '{email}' already exists.")
    else:
        hashed = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'admin')",
            (name, email, hashed)
        )
        conn.commit()
        print(f"Admin user created: {email} / {password}")
    
    cursor.close()
    conn.close()
    print("IMPORTANT: Change the admin password after first login!")


def create_host(email="host@wedding.com", password="host123", name="Wedding Host"):
    """Create default host user if not exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        print(f"Host user '{email}' already exists.")
    else:
        hashed = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'host')",
            (name, email, hashed)
        )
        conn.commit()
        print(f"Host user created: {email} / {password}")
    
    cursor.close()
    conn.close()


def main():
    # Create database first (requires manual step in phpMyAdmin or mysql command)
    conn = None
    try:
        conn = get_db_connection()
        print("Database connection OK.")
        create_tables(conn)
        print("Tables created/verified.")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. XAMPP MySQL is running")
        print("2. Database 'wedding_db' exists (create it in phpMyAdmin)")
        print("3. config.py DB settings match your XAMPP setup")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

    create_admin()
    create_host()
    print("\nSetup complete. Run: python app.py")


if __name__ == "__main__":
    main()
