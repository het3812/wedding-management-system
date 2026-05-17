# 💰 Commission Tracking System

A comprehensive 2.5% commission tracking and reporting system for the Wedding Management Platform admin panel.

## 🎯 Overview

This system automatically tracks, calculates, and manages commission from all vendor transactions. It provides real-time analytics, visual reports, and streamlined collection management.

## ✨ Key Features

- ✅ **Automated Calculation**: 2.5% commission calculated automatically on verified transactions
- 📊 **Visual Dashboard**: Real-time statistics with interactive charts
- 📈 **Analytics**: Monthly trends and vendor rankings
- 💼 **Collection Management**: Easy commission collection and tracking
- 📄 **Detailed Reports**: Per-vendor commission reports with charts
- 📥 **CSV Export**: Export filtered data for accounting
- 🔐 **Secure**: Admin-only access with full audit trail

## 🚀 Quick Start

### 1. Install Database Schema

**Windows:**
```bash
install_commission_system.bat
```

**Any OS:**
```bash
python install_commission_system.py
```

**Manual:**
```bash
mysql -u root wedding_db < database_commission_system.sql
```

### 2. Restart Flask Application

```bash
python app.py
```

### 3. Access Dashboard

```
URL: http://localhost:5000/admin/commissions
Login: Use admin credentials
```

## 📊 Dashboard Features

### Statistics Overview
- **Total Commission**: All commissions generated
- **Collected**: Successfully collected amount  
- **Pending**: Awaiting collection
- **Waived**: Forgiven commissions

### Visual Analytics
- **Monthly Trend Chart**: 6-month commission trend (line chart)
- **Status Distribution**: Commission breakdown (pie chart)
- **Top Vendors**: Ranked by commission amount

### Management Tools
- Filter by status, vendor, date range
- View detailed commission records
- Collect or waive commissions
- Export to CSV

## 📁 What's Included

### Database
- `database_commission_system.sql` - Complete schema with triggers

### Backend (Python/Flask)
- Commission tracking routes in `blueprints/admin.py`
- Automated commission calculation
- Collection and waiving functionality

### Frontend (HTML/Bootstrap/Chart.js)
- `admin_commission_dashboard.html` - Main dashboard
- `admin_commission_detail.html` - Detail view
- `admin_vendor_commission_report.html` - Vendor reports

### Documentation
- `COMMISSION_SYSTEM_GUIDE.md` - Complete usage guide
- `COMMISSION_SYSTEM_SUMMARY.md` - Technical summary
- `COMMISSION_VISUAL_GUIDE.txt` - Visual layouts
- `COMMISSION_QUICK_REFERENCE.md` - Quick reference card
- `README_COMMISSION_SYSTEM.md` - This file

### Installation Scripts
- `install_commission_system.bat` - Windows installer
- `install_commission_system.py` - Cross-platform installer

## 🔧 How It Works

### Workflow

```
1. Vendor Transaction Verified
   ↓
2. Database Trigger Fires
   ↓
3. Commission Calculated (2.5%)
   ↓
4. Record Created (Status: Pending)
   ↓
5. Admin Reviews Dashboard
   ↓
6. Admin Collects/Waives
   ↓
7. Status Updated
   ↓
8. Reports Generated
```

### Example Calculation

```
Transaction Amount: ₹10,000
Commission Rate: 2.5%
Commission Amount: ₹250
```

## 📱 Screenshots

### Dashboard
- 4 statistics cards with color coding
- 2 interactive charts (line + pie)
- Top 10 vendors table
- Filterable commission records

### Detail Page
- Complete commission information
- Vendor and booking details
- Collection form
- Waive form

### Vendor Report
- Vendor-specific statistics
- Monthly breakdown chart
- Complete transaction history
- Print-friendly format

## 🗄️ Database Structure

### Tables Created
- `commission_records` - Individual commission tracking
- `commission_summary` - Monthly aggregates

### Columns Added to payment_transactions
- `commission_rate` - Commission percentage
- `commission_amount` - Calculated amount
- `commission_status` - Status tracking
- `commission_collected_date` - Collection date
- `commission_notes` - Additional notes

## 🎨 Technology Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: Bootstrap 5
- **Charts**: Chart.js 4.4.0
- **Icons**: Font Awesome 6.4.0

## 📋 Routes

| Route | Purpose |
|-------|---------|
| `/admin/commissions` | Main dashboard |
| `/admin/commissions/<id>` | Detail view |
| `/admin/commissions/<id>/collect` | Collect commission |
| `/admin/commissions/<id>/waive` | Waive commission |
| `/admin/commissions/vendor/<id>` | Vendor report |
| `/admin/commissions/export` | CSV export |

## 🔐 Security

- Admin-only access via `@admin_required` decorator
- All actions logged with admin user ID
- Audit trail for collections and waivers
- Reason required for waiving commissions

## 📊 Reports Available

1. **Commission Dashboard**
   - Overall statistics
   - Visual charts
   - Filterable records

2. **Vendor Commission Report**
   - Vendor-specific analytics
   - Monthly breakdown
   - Complete history

3. **CSV Export**
   - Customizable via filters
   - All commission details
   - Ready for accounting software

## 💡 Usage Tips

### For Daily Use
1. Check pending commissions regularly
2. Use filters to find specific records
3. Add notes when collecting
4. Export monthly reports

### For Collection
1. Navigate to commission detail
2. Fill in payment method and reference
3. Add notes for documentation
4. Click "Mark as Collected"

### For Waiving
1. Navigate to commission detail
2. Enter reason for waiving
3. Confirm action
4. Record is marked as waived

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Commission not calculated | Verify transaction is "Verified" status |
| Charts not displaying | Check Chart.js library loaded |
| Export not working | Verify CSV module imported |
| Access denied | Ensure logged in as admin |

## 📚 Documentation

- **Complete Guide**: See `COMMISSION_SYSTEM_GUIDE.md`
- **Visual Layouts**: See `COMMISSION_VISUAL_GUIDE.txt`
- **Quick Reference**: See `COMMISSION_QUICK_REFERENCE.md`
- **Technical Summary**: See `COMMISSION_SYSTEM_SUMMARY.md`

## 🔄 Updates & Maintenance

### Regular Tasks
- Review pending commissions weekly
- Export monthly reports for accounting
- Verify commission calculations
- Update vendor information

### Database Maintenance
- Backup commission records regularly
- Archive old records annually
- Monitor table sizes
- Optimize indexes if needed

## 🎯 Best Practices

1. ✅ Review pending commissions weekly
2. ✅ Always add notes when collecting
3. ✅ Provide clear reasons when waiving
4. ✅ Export monthly reports for records
5. ✅ Cross-check with vendor payment records
6. ✅ Keep audit trail for accounting

## 🚀 Future Enhancements

Potential additions:
- Email notifications for pending commissions
- Automated monthly reports
- Custom commission rates per vendor
- Payment gateway integration
- Mobile app
- Advanced analytics dashboard

## 📞 Support

For help:
1. Check documentation files
2. Review Flask application logs
3. Verify database installation
4. Ensure proper admin permissions

## 📄 License

Internal use for Wedding Management Platform

## 👥 Credits

Developed for Wedding Management Platform  
Version 1.0  
Date: 2024

---

**Need Help?** Check `COMMISSION_SYSTEM_GUIDE.md` for detailed instructions.

**Quick Reference?** See `COMMISSION_QUICK_REFERENCE.md` for common tasks.

**Visual Guide?** Check `COMMISSION_VISUAL_GUIDE.txt` for layouts.
