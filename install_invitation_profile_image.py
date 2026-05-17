"""
Invitation Profile Image Installation Script
Adds profile_image column to invitations table
"""
import mysql.connector
from pathlib import Path

def install_profile_image():
    """Install profile image feature"""
    print("=" * 60)
    print("INVITATION PROFILE IMAGE INSTALLATION")
    print("=" * 60)
    
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'wedding_db'
    }
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        print("✓ Connected to database\n")
        
        # Read SQL file
        sql_file = Path(__file__).parent / 'database_invitation_profile_image.sql'
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Execute SQL
        try:
            # Remove comments and split by semicolon
            statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for statement in statements:
                cursor.execute(statement)
                print("✓ Added profile_image column to invitations table")
            
            conn.commit()
            print("\n" + "=" * 60)
            print("✓ INSTALLATION SUCCESSFUL!")
            print("=" * 60)
            print("\nFeature added:")
            print("  • Profile image upload for invitations")
            print("  • Couple photo display on invitation cards")
            print("  • Easy invitation identification")
            print("\nHow to use:")
            print("  1. Go to Edit Invitation")
            print("  2. Upload a couple/profile photo")
            print("  3. Photo will appear on invitation card")
            
        except mysql.connector.Error as e:
            if 'Duplicate column' in str(e):
                print("⚠ Column already exists - skipping")
                print("\n" + "=" * 60)
                print("✓ FEATURE ALREADY INSTALLED")
                print("=" * 60)
            else:
                raise
        
    except mysql.connector.Error as e:
        print(f"\n✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == '__main__':
    install_profile_image()
