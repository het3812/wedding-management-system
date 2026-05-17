"""
Commission Tracking System Installation Script
Installs the 2.5% commission tracking system for Wedding Management Platform
"""
import mysql.connector
from pathlib import Path

def install_commission_system():
    """Install commission tracking system database schema"""
    print("=" * 60)
    print("Commission Tracking System Installation")
    print("=" * 60)
    print()
    print("This will install the 2.5% commission tracking system")
    print("for the Wedding Management Platform.")
    print()
    
    # Get database credentials
    print("Enter MySQL credentials:")
    host = input("Host (default: localhost): ").strip() or "localhost"
    user = input("User (default: root): ").strip() or "root"
    password = input("Password (press Enter if none): ").strip()
    database = input("Database (default: wedding_db): ").strip() or "wedding_db"
    
    print()
    print("Connecting to database...")
    
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        print("✓ Connected successfully!")
        print()
        print("Reading SQL file...")
        
        # Read SQL file
        sql_file = Path("database_commission_system.sql")
        if not sql_file.exists():
            print("✗ Error: database_commission_system.sql not found!")
            return False
        
        sql_content = sql_file.read_text(encoding='utf-8')
        
        print("✓ SQL file loaded")
        print()
        print("Executing SQL statements...")
        
        # Split and execute SQL statements
        statements = []
        current_statement = []
        in_delimiter = False
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('--'):
                continue
            
            # Handle DELIMITER changes
            if line.startswith('DELIMITER'):
                in_delimiter = not in_delimiter
                continue
            
            current_statement.append(line)
            
            # Check for statement end
            if not in_delimiter and line.endswith(';'):
                statement = ' '.join(current_statement)
                if statement.strip():
                    statements.append(statement)
                current_statement = []
            elif in_delimiter and line.endswith('//'):
                statement = ' '.join(current_statement)
                if statement.strip():
                    statements.append(statement.replace('//', ''))
                current_statement = []
        
        # Execute statements
        success_count = 0
        for statement in statements:
            try:
                # Skip USE database and verification queries
                if statement.startswith('USE ') or statement.startswith('SELECT '):
                    continue
                
                cursor.execute(statement)
                success_count += 1
            except mysql.connector.Error as e:
                # Ignore "already exists" errors
                if "already exists" not in str(e).lower():
                    print(f"Warning: {e}")
        
        conn.commit()
        
        print(f"✓ Executed {success_count} SQL statements successfully")
        print()
        
        # Verify installation
        print("Verifying installation...")
        
        # Check if commission_records table exists
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = 'commission_records'
        """, (database,))
        
        if cursor.fetchone()[0] > 0:
            print("✓ commission_records table created")
        else:
            print("✗ commission_records table not found")
            return False
        
        # Check if commission_summary table exists
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = 'commission_summary'
        """, (database,))
        
        if cursor.fetchone()[0] > 0:
            print("✓ commission_summary table created")
        else:
            print("✗ commission_summary table not found")
            return False
        
        # Check if commission columns added to payment_transactions
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = %s 
            AND table_name = 'payment_transactions' 
            AND column_name = 'commission_amount'
        """, (database,))
        
        if cursor.fetchone()[0] > 0:
            print("✓ Commission columns added to payment_transactions")
        else:
            print("✗ Commission columns not found in payment_transactions")
            return False
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("SUCCESS! Commission system installed.")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Restart your Flask application")
        print("2. Login as Admin")
        print("3. Navigate to /admin/commissions")
        print()
        print("Features available:")
        print("- Commission Dashboard with charts")
        print("- Automated 2.5% commission calculation")
        print("- Collection and waiving management")
        print("- Vendor commission reports")
        print("- CSV export functionality")
        print()
        print("For detailed usage, see COMMISSION_SYSTEM_GUIDE.md")
        print()
        
        return True
        
    except mysql.connector.Error as e:
        print()
        print("=" * 60)
        print("ERROR: Installation failed!")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("Possible issues:")
        print("- MySQL is not running")
        print("- Database credentials are incorrect")
        print("- Database 'wedding_db' does not exist")
        print()
        return False
    
    except Exception as e:
        print()
        print(f"Unexpected error: {e}")
        return False


if __name__ == "__main__":
    try:
        success = install_commission_system()
        input("\nPress Enter to exit...")
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        exit(1)
