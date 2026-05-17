"""
RSVP System Setup Script
Run this after starting XAMPP MySQL to set up RSVP functionality
"""
import mysql.connector
from config import DB_CONFIG

def setup_rsvp_system():
    """Add RSVP columns to guests table and generate tokens for existing guests"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Setting up RSVP system...")
        
        # Check if columns already exist
        cursor.execute("SHOW COLUMNS FROM guests LIKE 'rsvp_token'")
        if cursor.fetchone():
            print("✓ RSVP columns already exist")
        else:
            print("Adding RSVP columns to guests table...")
            
            # Add RSVP token column
            cursor.execute("""
                ALTER TABLE guests 
                ADD COLUMN rsvp_token VARCHAR(64) UNIQUE AFTER phone
            """)
            
            # Add RSVP response column
            cursor.execute("""
                ALTER TABLE guests 
                ADD COLUMN rsvp_response TEXT AFTER rsvp_status
            """)
            
            # Add RSVP submitted timestamp
            cursor.execute("""
                ALTER TABLE guests 
                ADD COLUMN rsvp_submitted_at TIMESTAMP NULL AFTER rsvp_response
            """)
            
            # Add plus one columns
            cursor.execute("""
                ALTER TABLE guests 
                ADD COLUMN plus_one BOOLEAN DEFAULT FALSE AFTER category
            """)
            
            cursor.execute("""
                ALTER TABLE guests 
                ADD COLUMN plus_one_name VARCHAR(100) AFTER plus_one
            """)
            
            # Create index
            cursor.execute("""
                CREATE INDEX idx_rsvp_token ON guests(rsvp_token)
            """)
            
            conn.commit()
            print("✓ RSVP columns added successfully")
        
        # Generate tokens for existing guests without tokens
        cursor.execute("SELECT COUNT(*) FROM guests WHERE rsvp_token IS NULL")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Generating RSVP tokens for {count} existing guests...")
            cursor.execute("""
                UPDATE guests 
                SET rsvp_token = CONCAT(MD5(CONCAT(id, COALESCE(email, ''), RAND())), SUBSTRING(MD5(RAND()), 1, 8))
                WHERE rsvp_token IS NULL
            """)
            conn.commit()
            print(f"✓ Generated {count} RSVP tokens")
        else:
            print("✓ All guests already have RSVP tokens")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*50)
        print("RSVP System Setup Complete!")
        print("="*50)
        print("\nYou can now:")
        print("1. Start the Flask app: python app.py")
        print("2. Login as host")
        print("3. Add guests and share RSVP links")
        print("\nFor more info, see RSVP_SYSTEM_GUIDE.md")
        
    except mysql.connector.Error as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. XAMPP MySQL is running")
        print("2. Database 'wedding_db' exists")
        print("3. You have run database.sql first")
        return False
    
    return True

if __name__ == '__main__':
    print("="*50)
    print("Wedding Management System - RSVP Setup")
    print("="*50)
    print()
    setup_rsvp_system()
