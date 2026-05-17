# Commission System - Quick Reference Card

## 🚀 Quick Start

### Installation
```bash
# Windows
install_commission_system.bat

# Any OS
python install_commission_system.py
```

### Access
```
URL: http://localhost:5000/admin/commissions
Login: Admin credentials
```

## 📊 Dashboard Overview

### Statistics Cards
- **Total Commission**: All commissions generated
- **Collected**: Successfully collected amount
- **Pending**: Awaiting collection
- **Waived**: Forgiven commissions

### Charts
- **Monthly Trend**: Line chart (last 6 months)
- **Status Distribution**: Pie chart breakdown

### Top Vendors
- Ranked by total commission
- Shows transactions, amounts, status

## 🔧 Common Tasks

### Collect Commission
1. Click "View" on pending commission
2. Fill collection form:
   - Payment Method
   - Reference Number (optional)
   - Notes (optional)
3. Click "Mark as Collected"

### Waive Commission
1. Click "View" on pending commission
2. Scroll to "Waive Commission"
3. Enter reason
4. Click "Waive Commission"

### Filter Records
1. Select Status (All/Pending/Collected/Waived)
2. Select Vendor (optional)
3. Set Date Range (optional)
4. Click "Filter"

### Export Data
1. Apply desired filters
2. Click "Export CSV"
3. File downloads automatically

### View Vendor Report
1. Click "Report" next to vendor in top vendors
2. Or from commission detail page
3. View complete history and charts

## 💡 Key Features

| Feature | Description |
|---------|-------------|
| Auto-Calculate | 2.5% calculated automatically on verified transactions |
| Real-time Stats | Dashboard updates instantly |
| Visual Charts | Interactive Chart.js visualizations |
| Filtering | Multi-criteria filtering |
| Export | CSV export with filters |
| Vendor Reports | Detailed per-vendor analytics |
| Audit Trail | All actions logged with admin ID |

## 📁 Files Created

| File | Purpose |
|------|---------|
| `database_commission_system.sql` | Database schema |
| `blueprints/admin.py` | Backend routes (appended) |
| `templates/admin_commission_dashboard.html` | Main dashboard |
| `templates/admin_commission_detail.html` | Detail page |
| `templates/admin_vendor_commission_report.html` | Vendor report |
| `COMMISSION_SYSTEM_GUIDE.md` | Complete guide |
| `COMMISSION_SYSTEM_SUMMARY.md` | Summary |
| `COMMISSION_VISUAL_GUIDE.txt` | Visual layouts |
| `install_commission_system.bat` | Windows installer |
| `install_commission_system.py` | Python installer |

## 🔗 Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/admin/commissions` | GET | Dashboard |
| `/admin/commissions/<id>` | GET | Detail view |
| `/admin/commissions/<id>/collect` | POST | Collect |
| `/admin/commissions/<id>/waive` | POST | Waive |
| `/admin/commissions/vendor/<id>` | GET | Vendor report |
| `/admin/commissions/export` | GET | CSV export |

## 🗄️ Database Tables

### commission_records
- Individual commission tracking
- Links to transactions, bookings, vendors
- Status: Pending/Collected/Waived

### commission_summary
- Monthly aggregates per vendor
- Auto-updated summaries

## 🎨 Status Colors

| Status | Color | Badge |
|--------|-------|-------|
| Collected | Green | 🟢 |
| Pending | Yellow | 🟡 |
| Waived | Gray | ⚪ |

## 📈 Commission Calculation

```
Transaction Amount × 2.5% = Commission Amount

Example:
₹10,000 × 2.5% = ₹250
```

## 🔐 Security

- Admin-only access
- All actions logged
- Audit trail maintained
- Reason required for waiving

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Commission not calculated | Verify transaction status is "Verified" |
| Charts not showing | Check Chart.js library loaded |
| Export not working | Verify CSV module imported |
| Access denied | Ensure logged in as admin |

## 📞 Support

1. Check `COMMISSION_SYSTEM_GUIDE.md` for detailed help
2. Review `COMMISSION_VISUAL_GUIDE.txt` for layouts
3. Verify database installation
4. Check Flask application logs

## 🎯 Best Practices

1. ✅ Review pending commissions weekly
2. ✅ Add notes when collecting
3. ✅ Provide reason when waiving
4. ✅ Export monthly reports
5. ✅ Cross-check with vendor records

## 📊 Sample Workflow

```
1. Vendor completes service
2. Host makes payment
3. Admin verifies transaction
   ↓
4. Commission auto-calculated (2.5%)
5. Record created (Status: Pending)
   ↓
6. Admin reviews dashboard
7. Admin collects commission
   ↓
8. Status updated to "Collected"
9. Record appears in reports
```

## 🔢 Quick Stats Example

```
Total Transactions: ₹1,000,000
Commission Rate: 2.5%
Total Commission: ₹25,000

Breakdown:
- Collected: ₹15,000 (60%)
- Pending: ₹8,000 (32%)
- Waived: ₹2,000 (8%)
```

## 🎨 Dashboard Elements

### Cards (4)
- Total, Collected, Pending, Waived
- Color-coded borders
- Hover effects

### Charts (2)
- Monthly Trend (Line)
- Status Distribution (Pie)

### Tables (2)
- Top Vendors (10 rows)
- Commission Records (All)

### Filters (4)
- Status dropdown
- Vendor dropdown
- Date from
- Date to

## 🖨️ Print Features

- Vendor reports are print-friendly
- Hides navigation and buttons
- Optimized layout for paper

## 📱 Responsive Design

- Bootstrap 5 framework
- Mobile-friendly tables
- Responsive charts
- Touch-friendly buttons

## ⚡ Performance

- Indexed database queries
- Efficient aggregations
- Limited chart data (6 months)
- Pagination-ready structure

## 🔄 Auto-Updates

- Dashboard refreshes on page load
- Charts update with new data
- Statistics recalculate automatically
- No manual refresh needed

## 📝 Notes

- All amounts in Indian Rupees (₹)
- Timestamps in local timezone
- Commission rate configurable
- Default rate: 2.5%

---

**Version**: 1.0  
**Platform**: Flask + MySQL + Bootstrap 5 + Chart.js  
**License**: Internal Use  
**Support**: See COMMISSION_SYSTEM_GUIDE.md
