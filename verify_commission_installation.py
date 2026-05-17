"""
Commission System Installation Verification Script
Checks if all components are properly installed
"""
import mysql.connector
from pathlib import Path

def verify_installation():
    """Verify commission system installation"""
    print("=" * 70)
    print("Commission System Installation Verification")
    print("=" * 70)
    print()
    
    # Check files
    print("📁 Checking Files...")
    print("-" * 70)
    
    required_files = {
        'Database': 'database_commission_system.sql',
        'Backend': 'blueprints/admin.py',
        'Dashboard Template': 'templates/admin_commission_dashboard.html',
        'Detail Template': 'templates/admin_commission_detail.html',
        'Report Template': 'templates/admin_vendor_commission_report.html',
        'Guide': 'COMMISSION_SYSTEM_GUIDE.md',
        'Summary': 'COMMISSION_SYSTEM_SUMMARY.md',
        'Visual Guide': 'COMMISSION_VISUAL_GUIDE.txt',
        'Quick Reference': 'COMMISSION_QUICK_REFERENCE.md',
        'README': 'README_COMMISSION_SYSTEM.md'
    }
    
    files_ok = True
    for name, filepath in required_files.items():
        if Path(filepath).exists():
            print(f"✓ {name}: {filepath}")
        else:
            print(f"✗ {name}: {filepath} - NOT FOUND")
            files_ok = False
    
    print()
    
    # Check database
    print("🗄️  Checking Database...")
    print("-" * 70)
    
    try:
        host = input("MySQL Host (default: localhost): ").strip() or "localhost"
        user = input("MySQL User (default: root): ").strip() or "root"
        password = input("MySQL Password (press Enter if none): ").strip()
        database = input("Database (default: wedding_db): ").strip() or "wedding_db"
        
        print()
        print("Connecting to database...")
        
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        print("✓ Database connection successful")
        print()
        
        # Check tables
        tables_to_check = ['commission_records', 'commission_summary']
        tables_ok = True
        
        for table in tables_to_check:
            cursor.execute(f"""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
            """, (database, table))
            
            if cursor.fetchone()[0] > 0:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✓ Table '{table}' exists ({count} records)")
            else:
                print(f"✗ Table '{table}' NOT FOUND")
                tables_ok = False
        
        print()
        
        # Check columns in payment_transactions
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_schema = %s 
            AND table_name = 'payment_transactions' 
            AND column_name LIKE 'commission%%'
        """, (database,))
        
        commission_columns = [row[0] for row in cursor.fetchall()]
        
        expected_columns = ['commission_rate', 'commission_amount', 'commission_status', 
                          'commission_collected_date', 'commission_notes']
        
        columns_ok = True
        for col in expected_columns:
            if col in commission_columns:
                print(f"✓ Column 'payment_transactions.{col}' exists")
            else:
                print(f"✗ Column 'payment_transactions.{col}' NOT FOUND")
                columns_ok = False
        
        print()
        
        # Check triggers
        cursor.execute("""
            SELECT trigger_name FROM information_schema.triggers 
            WHERE trigger_schema = %s 
            AND trigger_name LIKE '%%commission%%'
        """, (database,))
        
        triggers = [row[0] for row in cursor.fetchall()]
        
        if triggers:
            print(f"✓ Commission triggers found: {', '.join(triggers)}")
        else:
            print("⚠ No commission triggers found (may need manual setup)")
        
        print()
        
        # Check stored procedures
        cursor.execute("""
            SELECT routine_name FROM information_schema.routines 
            WHERE routine_schema = %s 
            AND routine_name LIKE '%%commission%%'
        """, (database,))
        
        procedures = [row[0] for row in cursor.fetchall()]
        
        if procedures:
            print(f"✓ Commission procedures found: {', '.join(procedures)}")
        else:
            print("⚠ No commission procedures found (may need manual setup)")
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 70)
        
        if files_ok and tables_ok and columns_ok:
            print("✅ SUCCESS! Commission system is properly installed.")
            print("=" * 70)
            print()
            print("Next Steps:")
            print("1. Restart your Flask application: python app.py")
            print("2. Login as Admin")
            print("3. Navigate to: http://localhost:5000/admin/commissions")
            print()
            print("Documentation:")
            print("- Complete Guide: COMMISSION_SYSTEM_GUIDE.md")
            print("- Quick Reference: COMMISSION_QUICK_REFERENCE.md")
            print("- Visual Guide: COMMISSION_VISUAL_GUIDE.txt")
            print()
            return True
        else:
            print("⚠️  WARNING! Some components are missing.")
            print("=" * 70)
            print()
            if not files_ok:
                print("Missing files detected. Please ensure all files are present.")
            if not tables_ok:
                print("Missing database tables. Run: install_commission_system.py")
            if not columns_ok:
                print("Missing database columns. Run: install_commission_system.py")
            print()
            return False
            
    except mysql.connector.Error as e:
        print()
        print("=" * 70)
        print("❌ DATABASE ERROR!")
        print("=" * 70)
        print()
        print(f"Error: {e}")
        print()
        print("Possible issues:")
        print("- MySQL is not running")
        print("- Database credentials are incorrect")
        print("- Database 'wedding_db' does not exist")
        print("- Commission system not installed yet")
        print()
        print("To install, run: install_commission_system.py")
        print()
        return False
    
    except Exception as e:
        print()
        print(f"Unexpected error: {e}")
        return False


def check_routes():
    """Check if commission routes are in admin.py"""
    print()
    print("🔍 Checking Backend Routes...")
    print("-" * 70)
    
    admin_file = Path('blueprints/admin.py')
    
    if not admin_file.exists():
        print("✗ blueprints/admin.py not found")
        return False
    
    content = admin_file.read_text(encoding='utf-8')
    
    routes_to_check = [
        'commission_dashboard',
        'commission_detail',
        'collect_commission',
        'waive_commission',
        'vendor_commission_report',
        'export_commissions'
    ]
    
    routes_ok = True
    for route in routes_to_check:
        if f"def {route}" in content:
            print(f"✓ Route '{route}' found")
        else:
            print(f"✗ Route '{route}' NOT FOUND")
            routes_ok = False
    
    return routes_ok


if __name__ == "__main__":
    try:
        print()
        routes_ok = check_routes()
        print()
        
        db_ok = verify_installation()
        
        print()
        
        if routes_ok and db_ok:
            print("🎉 All checks passed! Commission system is ready to use.")
        elif routes_ok and not db_ok:
            print("⚠️  Backend routes are ready, but database needs installation.")
            print("   Run: install_commission_system.py")
        elif not routes_ok and db_ok:
            print("⚠️  Database is ready, but backend routes may be missing.")
            print("   Check blueprints/admin.py for commission routes.")
        else:
            print("❌ Installation incomplete. Please run installation script.")
        
        print()
        input("Press Enter to exit...")
        
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user.")
        exit(1)
