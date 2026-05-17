"""
Vendor Management System Enhancement Setup
Run this to add all vendor features to the database
"""
import mysql.connector
from config import DB_CONFIG

def setup_vendor_enhancement():
    """Add vendor enhancement features to database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("="*60)
        print("Vendor Management System Enhancement Setup")
        print("="*60)
        print()
        
        # Read and execute SQL file
        print("Reading SQL migration file...")
        with open('database_vendor_enhancement.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
        
        print(f"Executing {len(statements)} SQL statements...")
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                try:
                    cursor.execute(statement)
                    conn.commit()
                    print(f"  ✓ Statement {i}/{len(statements)}")
                except mysql.connector.Error as e:
                    if "Duplicate column" in str(e) or "already exists" in str(e):
                        print(f"  ⚠ Statement {i}: Already exists (skipped)")
                    else:
                        print(f"  ✗ Statement {i}: {e}")
        
        print()
        print("="*60)
        print("Setup Complete!")
        print("="*60)
        print()
        print("New Features Added:")
        print("  ✓ Enhanced vendor profiles (website, Instagram, location)")
        print("  ✓ Vendor gallery for multiple photos")
        print("  ✓ Rating & review system")
        print("  ✓ Booking/order tracking")
        print("  ✓ Real-time chat system")
        print("  ✓ Vendor inactivity tracking")
        print("  ✓ Auto-blocking policy")
        print("  ✓ Advanced filtering & search")
        print()
        print("Next Steps:")
        print("  1. Start Flask app: python app.py")
        print("  2. Vendors can update their profiles")
        print("  3. Users can browse, filter, and book vendors")
        print("  4. Admin can manage vendor blocks")
        print()
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"\n❌ Database Error: {e}")
        print("\nMake sure:")
        print("  1. XAMPP MySQL is running")
        print("  2. Database 'wedding_db' exists")
        print("  3. You have run database.sql first")
        return False
    except FileNotFoundError:
        print("\n❌ Error: database_vendor_enhancement.sql not found")
        print("Make sure the SQL file is in the same directory")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False

if __name__ == '__main__':
    setup_vendor_enhancement()
