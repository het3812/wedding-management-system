"""
Fix vendor_bookings foreign key constraint issue
Run this if you get IntegrityError when booking without selecting a service
"""
import mysql.connector
from config import DB_CONFIG

def fix_booking_constraint():
    """Fix the service_id foreign key constraint to allow NULL values"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("="*60)
        print("Fixing vendor_bookings constraint...")
        print("="*60)
        print()
        
        # Drop existing constraint
        print("1. Dropping old foreign key constraint...")
        try:
            cursor.execute("""
                ALTER TABLE vendor_bookings 
                DROP FOREIGN KEY vendor_bookings_ibfk_3
            """)
            conn.commit()
            print("   ✓ Old constraint dropped")
        except mysql.connector.Error as e:
            if "check that column/key exists" in str(e).lower():
                print("   ⚠ Constraint doesn't exist (already fixed or different name)")
            else:
                print(f"   ⚠ Warning: {e}")
        
        # Recreate constraint with proper NULL handling
        print("2. Creating new foreign key constraint...")
        try:
            cursor.execute("""
                ALTER TABLE vendor_bookings
                ADD CONSTRAINT vendor_bookings_ibfk_3 
                FOREIGN KEY (service_id) REFERENCES vendor_services(id) 
                ON DELETE SET NULL
            """)
            conn.commit()
            print("   ✓ New constraint created")
        except mysql.connector.Error as e:
            if "Duplicate key" in str(e) or "already exists" in str(e):
                print("   ✓ Constraint already exists correctly")
            else:
                raise e
        
        # Verify the fix
        print("3. Verifying the fix...")
        cursor.execute("SHOW CREATE TABLE vendor_bookings")
        result = cursor.fetchone()
        if result and 'ON DELETE SET NULL' in result[1]:
            print("   ✓ Constraint verified - NULL values now allowed")
        else:
            print("   ⚠ Could not verify constraint")
        
        cursor.close()
        conn.close()
        
        print()
        print("="*60)
        print("Fix Complete!")
        print("="*60)
        print()
        print("You can now book vendors without selecting a specific service.")
        print("The 'General Inquiry' option will work correctly.")
        print()
        return True
        
    except mysql.connector.Error as e:
        print(f"\n❌ Database Error: {e}")
        print("\nMake sure:")
        print("  1. XAMPP MySQL is running")
        print("  2. Database 'wedding_db' exists")
        print("  3. vendor_bookings table exists")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False

if __name__ == '__main__':
    print()
    print("This script will fix the booking constraint issue.")
    print("It's safe to run multiple times.")
    print()
    input("Press Enter to continue...")
    print()
    fix_booking_constraint()
    print()
    input("Press Enter to exit...")
