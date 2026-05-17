# Admin Payment Transaction Monitoring

## Overview
Admin panel feature for monitoring and managing all payment transactions between hosts and vendors in the wedding management system.

---

## Features

### Payment Transaction Dashboard
- View all payment transactions in one place
- Real-time statistics (total, pending, verified, rejected)
- Filter by status and vendor
- Export transactions to CSV
- Detailed transaction view

### Statistics Display
- **Total Transactions**: Count of all payment transactions
- **Pending Count**: Transactions awaiting vendor verification
- **Verified Count**: Successfully verified transactions
- **Total Verified Amount**: Sum of all verified payment amounts

### Filtering Options
- **By Status**: All, Pending, Verified, Rejected
- **By Vendor**: Filter transactions for specific vendors
- Clear filters option

### Transaction Details
Each transaction shows:
- Transaction ID and date
- Vendor and host information
- Service details
- Payment type (Advance/Final)
- Amount and payment method
- Transaction reference number
- Current status
- Payment proof image

---

## Access

### URL Routes
- **All Transactions**: `/admin/payments`
- **Transaction Detail**: `/admin/payments/<transaction_id>`
- **Export CSV**: `/admin/payments/export`

### Navigation
From Admin Dashboard:
1. Look for "Payment Transactions" card
2. Click "View All Transactions" button

---

## Using the Payment Dashboard

### View All Transactions
1. Login as admin
2. Go to Admin Dashboard
3. Click "View All Transactions" in Payment Transactions card
4. See list of all payment transactions

### Filter Transactions
1. Use "Status" dropdown to filter by payment status
2. Use "Vendor" dropdown to filter by specific vendor
3. Click "Clear Filters" to reset

### View Transaction Details
1. Click "View" button on any transaction
2. See complete transaction information:
   - Transaction details
   - Payment proof image
   - Vendor information
   - Host information
   - Booking details
   - All related transactions

### Export Data
1. Click "Export CSV" button on transactions page
2. CSV file downloads with all transaction data
3. Open in Excel or Google Sheets

---

## Transaction Information

### Transaction Details
- **Transaction ID**: Unique identifier
- **Booking ID**: Associated booking reference
- **Transaction Type**: Advance or Final payment
- **Amount**: Payment amount in ₹
- **Payment Method**: UPI, Bank Transfer, etc.
- **Transaction Ref**: Reference number from payment
- **Submitted Date**: When host submitted payment
- **Verified Date**: When vendor verified (if applicable)
- **Notes**: Additional payment notes

### Vendor Information
- Business name
- Contact email and phone
- Service provided
- Service price

### Host Information
- Host name
- Contact email and phone
- Event date
- Booking status

### Booking Information
- Event date
- Booking status (Pending, Confirmed, Completed, Cancelled)
- Payment status (Not Paid, Advance Paid, Fully Paid)
- Total booking amount
- Advance and final amounts

---

## Payment Status Badges

### Color Coding
- 🟢 **Green (Verified)**: Payment verified by vendor
- 🟡 **Yellow (Pending)**: Awaiting vendor verification
- 🔴 **Red (Rejected)**: Payment rejected by vendor
- ⚫ **Gray (Other)**: Other status

### Transaction Type Badges
- 🔵 **Blue (Advance)**: Advance payment
- 🟣 **Purple (Final)**: Final payment

---

## CSV Export Format

### Exported Columns
1. Transaction ID
2. Date (YYYY-MM-DD HH:MM:SS)
3. Type (Advance/Final)
4. Amount (₹)
5. Payment Method
6. Transaction Reference
7. Status
8. Verified Date
9. Vendor Name
10. Host Name
11. Host Email
12. Event Date

### Use Cases
- Financial reporting
- Accounting reconciliation
- Transaction auditing
- Data analysis
- Record keeping

---

## Admin Capabilities

### What Admins Can Do
✅ View all payment transactions
✅ Filter and search transactions
✅ View detailed transaction information
✅ See payment proof images
✅ Export transaction data to CSV
✅ Monitor payment statistics
✅ Track vendor-host transactions

### What Admins Cannot Do
❌ Verify or reject payments (vendor only)
❌ Modify transaction amounts
❌ Delete transactions
❌ Process refunds
❌ Change payment status directly

---

## Statistics Dashboard

### Real-Time Metrics
- **Total Transactions**: All payment transactions in system
- **Pending**: Transactions awaiting verification
- **Verified**: Successfully verified transactions
- **Verified Amount**: Total amount of verified payments

### Summary View
On transaction list page:
- Pending verification count
- Verified count
- Rejected count

---

## Payment Proof Viewing

### Image Display
- Payment proof screenshots shown in detail view
- Click image to view full size in new tab
- Supports PNG, JPG, GIF, WEBP formats

### Security
- Images stored in secure user-specific folders
- Only admin can view all payment proofs
- Vendors can only see their own bookings

---

## Monitoring Best Practices

### Regular Checks
1. **Daily**: Check pending transactions
2. **Weekly**: Review verified transactions
3. **Monthly**: Export data for accounting

### Red Flags to Watch
- Multiple rejected payments
- Large amounts pending verification
- Unusual transaction patterns
- Mismatched amounts

### Reporting
- Export monthly transaction reports
- Track vendor payment verification rates
- Monitor payment method trends
- Analyze transaction volumes

---

## Integration with Other Features

### Related to Bookings
- Transactions linked to vendor bookings
- Booking status affects payment flow
- Completed bookings enable reviews

### Related to Vendors
- Vendor payment settings
- Vendor verification actions
- Vendor transaction history

### Related to Hosts
- Host payment submissions
- Host booking management
- Host transaction tracking

---

## Technical Details

### Database Tables Used
- `payment_transactions`: Main transaction records
- `vendor_bookings`: Booking information
- `vendors`: Vendor details
- `users`: Host details
- `vendor_services`: Service information

### Query Performance
- Indexed on transaction date
- Filtered queries optimized
- Pagination ready (can be added)

---

## Future Enhancements

### Potential Features
- Payment analytics dashboard
- Automated payment reminders
- Dispute resolution system
- Refund management
- Payment gateway integration
- Real-time notifications
- Advanced filtering options
- Date range filters
- Search functionality
- Pagination for large datasets

---

## Troubleshooting

### Issue: No transactions showing
**Solution**: Check if payment system database is installed

### Issue: Export not working
**Solution**: Check file permissions and CSV module

### Issue: Images not loading
**Solution**: Verify upload folder paths and file permissions

### Issue: Statistics incorrect
**Solution**: Check database queries and transaction status values

---

## Security Considerations

### Access Control
- Only admin users can access payment monitoring
- Admin authentication required
- Session-based security

### Data Privacy
- Payment proofs stored securely
- Sensitive data protected
- No credit card information stored

### Audit Trail
- All transactions timestamped
- Verification dates recorded
- Status changes tracked

---

## Quick Reference

### Key URLs
```
/admin/payments                    - All transactions
/admin/payments/<id>              - Transaction detail
/admin/payments/export            - Export CSV
```

### Key Features
- 📊 Statistics dashboard
- 🔍 Filter and search
- 📥 CSV export
- 🖼️ Payment proof viewing
- 📋 Detailed transaction info

### Status Values
- `Pending` - Awaiting verification
- `Verified` - Approved by vendor
- `Rejected` - Declined by vendor

---

## Implementation Status

✅ Payment transaction listing
✅ Transaction detail view
✅ Statistics dashboard
✅ Filter by status and vendor
✅ CSV export functionality
✅ Payment proof viewing
✅ Admin dashboard integration
✅ Responsive design
✅ Security measures

---

## Support

For issues or questions:
1. Check this documentation
2. Review payment system implementation docs
3. Check database schema
4. Verify admin permissions
5. Test with sample data

---

**Last Updated**: Implementation Complete
**Version**: 1.0
**Status**: Production Ready
