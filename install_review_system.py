"""
Rating & Review System Installer
Automated installation script for the review system
"""
import os
import sys
from db import execute_query, execute_update, get_db_connection

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60 + "\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def check_database_connection():
    """Check if database connection works"""
    try:
        conn = get_db_connection()
        conn.close()
        return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False

def check_existing_tables():
    """Check if review tables already exist"""
    try:
        # Check for review_helpfulness table
        result = execute_query(
            "SHOW TABLES LIKE 'review_helpfulness'",
            fetch_one=True
        )
        return result is not None
    except:
        return False

def run_sql_file(filename):
    """Execute SQL file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for statement in statements:
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except Exception as e:
                    # Skip errors for IF NOT EXISTS statements
                    if 'already exists' not in str(e).lower():
                        print_info(f"Skipped: {str(e)[:50]}...")
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print_error(f"SQL execution failed: {e}")
        return False

def verify_installation():
    """Verify that tables were created"""
    try:
        # Check vendor_reviews columns
        result = execute_query(
            "SHOW COLUMNS FROM vendor_reviews LIKE 'helpful_count'",
            fetch_one=True
        )
        if not result:
            return False
        
        # Check review_helpfulness table
        result = execute_query(
            "SHOW TABLES LIKE 'review_helpfulness'",
            fetch_one=True
        )
        if not result:
            return False
        
        # Check review_reports table
        result = execute_query(
            "SHOW TABLES LIKE 'review_reports'",
            fetch_one=True
        )
        if not result:
            return False
        
        return True
    except Exception as e:
        print_error(f"Verification failed: {e}")
        return False

def show_statistics():
    """Show current review statistics"""
    try:
        # Count reviews
        result = execute_query(
            "SELECT COUNT(*) as count FROM vendor_reviews",
            fetch_one=True
        )
        review_count = result['count'] if result else 0
        
        # Count vendors with reviews
        result = execute_query(
            "SELECT COUNT(DISTINCT vendor_id) as count FROM vendor_reviews",
            fetch_one=True
        )
        vendor_count = result['count'] if result else 0
        
        # Average rating
        result = execute_query(
            "SELECT AVG(rating) as avg_rating FROM vendor_reviews",
            fetch_one=True
        )
        avg_rating = result['avg_rating'] if result and result['avg_rating'] else 0
        
        print_info(f"Total Reviews: {review_count}")
        print_info(f"Vendors with Reviews: {vendor_count}")
        print_info(f"Average Rating: {avg_rating:.2f}/5.0")
        
    except Exception as e:
        print_info("Statistics not available yet")

def main():
    """Main installation function"""
    print_header("RATING & REVIEW SYSTEM INSTALLER")
    
    print("This script will install the rating and review system.")
    print("\nPrerequisites:")
    print("- MySQL/XAMPP running")
    print("- wedding_db database exists")
    print("- Python Flask application installed")
    print()
    
    input("Press Enter to continue...")
    
    # Step 1: Check database connection
    print_header("Step 1: Checking Database Connection")
    if not check_database_connection():
        print_error("Cannot connect to database!")
        print("\nPlease check:")
        print("1. MySQL is running (XAMPP)")
        print("2. Database 'wedding_db' exists")
        print("3. Database credentials in config.py are correct")
        sys.exit(1)
    print_success("Database connection successful!")
    
    # Step 2: Check if already installed
    print_header("Step 2: Checking Existing Installation")
    if check_existing_tables():
        print_info("Review system tables already exist.")
        response = input("Do you want to reinstall? (y/n): ")
        if response.lower() != 'y':
            print_info("Installation cancelled.")
            sys.exit(0)
    
    # Step 3: Run SQL migration
    print_header("Step 3: Installing Database Enhancements")
    sql_file = "database_review_enhancement.sql"
    
    if not os.path.exists(sql_file):
        print_error(f"SQL file not found: {sql_file}")
        sys.exit(1)
    
    print_info(f"Executing {sql_file}...")
    if not run_sql_file(sql_file):
        print_error("Database installation failed!")
        sys.exit(1)
    print_success("Database tables created successfully!")
    
    # Step 4: Verify installation
    print_header("Step 4: Verifying Installation")
    if not verify_installation():
        print_error("Installation verification failed!")
        print_info("Some tables may not have been created correctly.")
        sys.exit(1)
    print_success("All tables verified successfully!")
    
    # Step 5: Show statistics
    print_header("Step 5: Current Statistics")
    show_statistics()
    
    # Success message
    print_header("INSTALLATION COMPLETE!")
    print("✅ Rating & Review System installed successfully!")
    print("\nNext steps:")
    print("1. Restart your Flask application: python app.py")
    print("2. Login as host and book a vendor")
    print("3. Vendor marks booking as completed")
    print("4. Host writes a review")
    print("5. Test all features!")
    print("\nDocumentation:")
    print("- Quick Start: REVIEW_SYSTEM_QUICK_START.md")
    print("- Full Guide: RATING_REVIEW_SYSTEM_GUIDE.md")
    print("- Summary: REVIEW_IMPLEMENTATION_SUMMARY.md")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
