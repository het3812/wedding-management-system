# Commission Tracking System - Implementation Guide

## Overview
This system tracks and manages 2.5% commission from all vendor transactions in the wedding management platform. It provides comprehensive reporting, analytics, and collection management for administrators.

## Features

### 1. Automated Commission Calculation
- Automatically calculates 2.5% commission on all verified vendor transactions
- Creates commission records when payment transactions are verified
- Tracks commission status: Pending, Collected, Waived

### 2. Commission Dashboard
- **Real-time Statistics**: Total, Collected, Pending, and Waived commissions
- **Visual Charts**: 
  - Monthly trend line chart showing commission over time
  - Status distribution pie chart
- **Top Vendors**: List of top 10 vendors by commission amount
- **Filtering**: Filter by status, vendor, and date range
- **Export**: CSV export functionality for reports

### 3. Commission Management
- **View Details**: Detailed view of each commission record
- **Collect Commission**: Mark commission as collected with payment details
- **Waive Commission**: Forgive commission with reason tracking
- **Vendor Reports**: Detailed commission reports per vendor

### 4. Vendor Commission Reports
- Complete transaction history per vendor
- Monthly breakdown with charts
- Statistics: Total transactions, commissions, collected, pending
- Printable format for documentation

## Installation Steps

### Step 1: Run Database Migration
```bash
# Open MySQL in XAMPP phpMyAdmin or command line
# Run the commission system SQL file
mysql -u root wedding_db < database_commission_system.sql
```

Or in phpMyAdmin:
1. Open phpMyAdmin
2. Select `wedding_db` database
3. Go to "Import" tab
4. Choose `database_commission_system.sql`
5. Click "Go"

### Step 2: Verify Database Tables
The following tables should be created:
- `commission_records` - Individual commission records
- `commission_summary` - Monthly aggregated summaries

The following columns should be added to `payment_transactions`:
- `commission_rate` - Commission percentage (default 2.5%)
- `commission_amount` - Calculated commission
- `commission_status` - Status tracking
- `commission_collected_date` - Collection date
- `commission_notes` - Additional notes

### Step 3: Access Commission Dashboard
1. Login as Admin
2. Navigate to: `/admin/commissions`
3. Or click "Commissions" in the admin navigation menu

## Usage Guide

### For Administrators

#### Viewing Commission Dashboard
1. Go to Admin Panel → Commissions
2. View overall statistics at the top
3. Review charts for trends and distribution
4. Check top vendors by commission

#### Filtering Records
1. Use the filter form to narrow down records:
   - Status: All, Pending, Collected, Waived
   - Vendor: Select specific vendor
   - Date Range: From and To dates
2. Click "Filter" to apply

#### Collecting Commission
1. Click "View" on any pending commission record
2. In the detail page, fill in the collection form:
   - Payment Method (Cash, Bank Transfer, UPI, Other)
   - Reference Number (optional)
   - Notes (optional)
3. Click "Mark as Collected"

#### Waiving Commission
1. Click "View" on any pending commission record
2. Scroll to "Waive Commission" section
3. Enter reason for waiving
4. Click "Waive Commission"
5. Confirm the action

#### Viewing Vendor Reports
1. From commission dashboard, click "Report" next to any vendor in top vendors list
2. Or go to commission detail and click "View Full Vendor Report"
3. View complete transaction history and monthly breakdown
4. Use "Print Report" button for documentation

#### Exporting Data
1. Apply desired filters on commission dashboard
2. Click "Export CSV" button
3. CSV file will download with all filtered records

## Database Schema

### commission_records Table
```sql
- id: Primary key
- transaction_id: Link to payment_transactions
- booking_id: Link to vendor_bookings
- vendor_id: Link to vendors
- transaction_amount: Original transaction amount
- commission_rate: Commission percentage (2.5%)
- commission_amount: Calculated commission
- status: Pending/Collected/Waived
- collected_date: When commission was collected
- collected_by: Admin user who collected
- payment_method: How commission was paid
- reference_number: Payment reference
- notes: Additional information
- created_at: Record creation timestamp
```

### commission_summary Table
```sql
- id: Primary key
- vendor_id: Link to vendors
- month: Month (1-12)
- year: Year
- total_transactions: Sum of transaction amounts
- total_commission: Sum of commissions
- collected_commission: Sum of collected
- pending_commission: Sum of pending
- transaction_count: Number of transactions
- last_updated: Last update timestamp
```

## API Endpoints

### Commission Routes
- `GET /admin/commissions` - Commission dashboard
- `GET /admin/commissions/<id>` - Commission detail
- `POST /admin/commissions/<id>/collect` - Collect commission
- `POST /admin/commissions/<id>/waive` - Waive commission
- `GET /admin/commissions/vendor/<vendor_id>` - Vendor report
- `GET /admin/commissions/export` - Export CSV

## Automated Features

### Trigger: calculate_commission_after_verification
- Automatically runs when payment transaction status changes to "Verified"
- Calculates commission amount (transaction_amount × 2.5%)
- Creates commission record in `commission_records` table
- Sets initial status as "Pending"

### Stored Procedure: update_commission_summary
- Updates monthly commission summaries
- Can be called manually or scheduled
- Aggregates data by vendor, month, and year

## Reports Available

### 1. Commission Dashboard
- Overall statistics
- Monthly trend chart (last 6 months)
- Status distribution pie chart
- Top 10 vendors by commission
- Filterable commission records list

### 2. Vendor Commission Report
- Vendor-specific statistics
- Monthly breakdown table
- Monthly commission chart
- Complete transaction history
- Printable format

### 3. CSV Export
- Customizable based on filters
- Includes all commission details
- Vendor and host information
- Transaction references

## Best Practices

1. **Regular Collection**: Review pending commissions weekly
2. **Documentation**: Always add notes when collecting or waiving
3. **Verification**: Cross-check with vendor payment records
4. **Reporting**: Generate monthly reports for accounting
5. **Backup**: Export CSV regularly for backup purposes

## Troubleshooting

### Commission Not Calculated
- Verify payment transaction status is "Verified"
- Check if trigger is enabled in database
- Manually insert commission record if needed

### Charts Not Displaying
- Ensure Chart.js library is loaded
- Check browser console for JavaScript errors
- Verify data is being passed to template

### Export Not Working
- Check if CSV module is imported in admin.py
- Verify file permissions for downloads
- Check browser download settings

## Future Enhancements

Potential additions:
- Email notifications for pending commissions
- Automated monthly reports
- Commission rate customization per vendor
- Payment reminders
- Integration with accounting software
- Mobile-responsive dashboard improvements

## Support

For issues or questions:
1. Check database logs for errors
2. Review Flask application logs
3. Verify all database tables exist
4. Ensure proper user permissions

## Version History

- v1.0 (Current): Initial commission tracking system
  - Automated calculation
  - Dashboard with charts
  - Collection and waiving functionality
  - Vendor reports
  - CSV export
