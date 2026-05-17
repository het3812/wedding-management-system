"""
Quick script to add guest_count column to guests table
Run this: python add_guest_count_column.py
"""
import mysql.connector
from config import DB_CONFIG

def add_guest_count_column():
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Connected to database...")
        
        # Check if column already exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'wedding_db' 
            AND TABLE_NAME = 'guests' 
            AND COLUMN_NAME = 'guest_count'
        """)
        
        exists = cursor.fetchone()[0]
        
        if exists:
            print("✓ Column 'guest_count' already exists!")
        else:
            print("Adding 'guest_count' column...")
            
            # Add the column
            cursor.execute("""
                ALTER TABLE guests 
                ADD COLUMN guest_count INT DEFAULT 1 AFTER rsvp_submitted_at
            """)
            
            print("✓ Column added successfully!")
            
            # Migrate existing data
            print("Migrating existing plus_one data...")
            cursor.execute("""
                UPDATE guests 
                SET guest_count = CASE 
                    WHEN plus_one = TRUE THEN 2 
                    ELSE 1 
                END
                WHERE guest_count IS NULL OR guest_count = 0
            """)
            
            print("✓ Data migrated successfully!")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ All done! You can now use the guest count feature.")
        
    except mysql.connector.Error as err:
        print(f"✗ Error: {err}")
        print("\nPlease run this SQL manually in phpMyAdmin:")
        print("ALTER TABLE guests ADD COLUMN guest_count INT DEFAULT 1 AFTER rsvp_submitted_at;")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Adding guest_count column to guests table")
    print("=" * 60)
    add_guest_count_column()
