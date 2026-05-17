"""
Profile Image Diagnostic Script
Checks if profile image feature is properly installed
"""
import mysql.connector
from pathlib import Path

def check_profile_image():
    """Check profile image installation"""
    print("=" * 60)
    print("PROFILE IMAGE DIAGNOSTIC")
    print("=" * 60)
    
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'wedding_db'
    }
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        print("✓ Connected to database\n")
        
        # Check 1: Column exists
        print("Check 1: Database Column")
        print("-" * 60)
        cursor.execute("SHOW COLUMNS FROM invitations LIKE 'profile_image'")
        column = cursor.fetchone()
        
        if column:
            print("✓ profile_image column EXISTS")
            print(f"  Type: {column['Type']}")
            print(f"  Null: {column['Null']}")
            print(f"  Default: {column['Default']}")
        else:
            print("✗ profile_image column DOES NOT EXIST")
            print("\n  FIX: Run this command:")
            print("  python install_invitation_profile_image.py")
            return False
        
        # Check 2: Invitations with profile images
        print("\nCheck 2: Invitations with Profile Images")
        print("-" * 60)
        cursor.execute("""
            SELECT id, bride_name, groom_name, profile_image 
            FROM invitations
        """)
        invitations = cursor.fetchall()
        
        if not invitations:
            print("⚠ No invitations found in database")
        else:
            print(f"Found {len(invitations)} invitation(s):\n")
            for inv in invitations:
                print(f"  ID: {inv['id']} - {inv['bride_name']} & {inv['groom_name']}")
                if inv['profile_image']:
                    print(f"    ✓ Has profile image: {inv['profile_image']}")
                    
                    # Check if file exists
                    file_path = Path(__file__).parent / 'static' / inv['profile_image']
                    if file_path.exists():
                        print(f"    ✓ File exists on disk")
                    else:
                        print(f"    ✗ File NOT found on disk: {file_path}")
                else:
                    print(f"    ✗ No profile image uploaded")
        
        # Check 3: Upload folder structure
        print("\nCheck 3: Upload Folder Structure")
        print("-" * 60)
        static_dir = Path(__file__).parent / 'static'
        uploads_dir = static_dir / 'uploads'
        
        if uploads_dir.exists():
            print(f"✓ Uploads folder exists: {uploads_dir}")
            
            # Check for profile folders
            profile_folders = list(uploads_dir.glob('*/profile'))
            if profile_folders:
                print(f"✓ Found {len(profile_folders)} profile folder(s):")
                for folder in profile_folders:
                    images = list(folder.glob('*'))
                    print(f"  {folder} ({len(images)} file(s))")
            else:
                print("⚠ No profile folders found yet")
        else:
            print(f"⚠ Uploads folder doesn't exist: {uploads_dir}")
        
        print("\n" + "=" * 60)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 60)
        
        # Summary
        print("\nSUMMARY:")
        if column:
            print("✓ Database column is installed")
        else:
            print("✗ Database column is NOT installed")
        
        has_images = any(inv['profile_image'] for inv in invitations)
        if has_images:
            print("✓ At least one invitation has a profile image")
        else:
            print("⚠ No invitations have profile images yet")
        
        print("\nNEXT STEPS:")
        if not column:
            print("1. Run: python install_invitation_profile_image.py")
            print("2. Restart Flask app")
            print("3. Upload profile image in Edit Invitation")
        elif not has_images:
            print("1. Go to Host Dashboard")
            print("2. Click 'Edit' on invitation")
            print("3. Upload a profile image")
            print("4. Click 'Save Invitation'")
            print("5. Refresh dashboard")
        else:
            print("1. Restart Flask app if running")
            print("2. Refresh browser")
            print("3. Profile images should appear!")
        
    except mysql.connector.Error as e:
        print(f"\n✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == '__main__':
    check_profile_image()
    input("\nPress Enter to exit...")
