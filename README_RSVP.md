# 💒 Wedding RSVP System

A complete, mobile-friendly RSVP system for your wedding management platform. Guests can confirm or decline attendance from any device using personalized shareable links.

## 🌟 Features

### For Hosts
- ✅ Generate unique RSVP links for each guest
- ✅ One-click copy to clipboard
- ✅ Real-time response tracking
- ✅ View guest messages and special requests
- ✅ Track plus-one responses
- ✅ Summary statistics dashboard
- ✅ Detailed RSVP information per guest

### For Guests
- ✅ Mobile-responsive design
- ✅ Simple confirm/decline interface
- ✅ Add plus-one information
- ✅ Send messages to the couple
- ✅ View event schedule
- ✅ Update RSVP anytime
- ✅ No login required

## 🚀 Quick Start

### 1. Setup Database
```bash
python setup_rsvp.py
```

### 2. Start Application
```bash
python app.py
```

### 3. Use the System
1. Login as host at `http://127.0.0.1:5000/host/login`
2. Add guests to your wedding
3. Copy RSVP links and share with guests
4. Monitor responses in real-time

## 📱 How It Works

### Host Workflow
```
Add Guest → System Generates Token → Copy Link → Share → Track Responses
```

### Guest Workflow
```
Receive Link → Open Form → Fill Details → Submit → Confirmation
```

## 🔗 URLs

| Purpose | URL |
|---------|-----|
| RSVP Form | `/rsvp/<unique-token>` |
| Host Dashboard | `/host/` |
| Guest List | `/host/invitation/<id>/guests` |

## 📊 Database Schema

New columns added to `guests` table:
- `rsvp_token` - Unique shareable link token
- `rsvp_status` - Confirmed/Declined/Pending
- `rsvp_response` - Guest message
- `rsvp_submitted_at` - Submission timestamp
- `plus_one` - Whether bringing a guest
- `plus_one_name` - Plus one guest name

## 🎨 Screenshots

### RSVP Form (Mobile)
```
┌──────────────────┐
│  You're invited  │
│  Sarah & John    │
│  June 15, 2026   │
│                  │
│  ┌────┐  ┌────┐ │
│  │ ✓  │  │ ✗  │ │
│  │Yes │  │ No │ │
│  └────┘  └────┘ │
│                  │
│  [Submit RSVP]   │
└──────────────────┘
```

### Host Dashboard
```
┌─────────────────────────────────────┐
│ Guest List                          │
├─────────────────────────────────────┤
│ John Doe    ✓Confirmed    +1 (Jane) │
│ [View Details] [Copy Link]          │
├─────────────────────────────────────┤
│ Summary: 18 Confirmed, 2 Declined   │
└─────────────────────────────────────┘
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [RSVP_SYSTEM_GUIDE.md](RSVP_SYSTEM_GUIDE.md) | Complete implementation guide |
| [RSVP_QUICK_START.md](RSVP_QUICK_START.md) | Quick reference for hosts |
| [test_rsvp.md](test_rsvp.md) | Testing procedures |
| [RSVP_CHECKLIST.md](RSVP_CHECKLIST.md) | Implementation checklist |
| [RSVP_VISUAL_GUIDE.txt](RSVP_VISUAL_GUIDE.txt) | Visual architecture guide |

## 🔒 Security

- Cryptographically secure tokens (32 bytes)
- Unique per guest
- Non-guessable
- Token validation on every request
- No authentication needed (token is the key)

## 📱 Mobile Support

Works perfectly on:
- iPhone (Safari, Chrome)
- Android (Chrome, Firefox)
- iPad/Tablets
- All desktop browsers

## 🛠️ Technical Stack

- **Backend**: Python Flask
- **Database**: MySQL (XAMPP)
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Bootstrap 5.3.2
- **Security**: Token-based authentication

## 📦 Files Structure

```
wedding_management_system/
├── blueprints/
│   └── rsvp.py                    # RSVP blueprint
├── templates/
│   ├── rsvp_form.html             # RSVP form
│   ├── rsvp_success.html          # Success page
│   ├── rsvp_error.html            # Error page
│   └── host_guest_rsvp_detail.html # RSVP details
├── database_rsvp_migration.sql    # Database migration
├── setup_rsvp.py                  # Setup script
└── Documentation/
    ├── RSVP_SYSTEM_GUIDE.md
    ├── RSVP_QUICK_START.md
    └── test_rsvp.md
```

## 🧪 Testing

Run the test suite:
```bash
# See test_rsvp.md for detailed testing guide
```

Test scenarios:
- ✅ Add guest and generate token
- ✅ Copy and share RSVP link
- ✅ Submit RSVP from mobile device
- ✅ View response in host dashboard
- ✅ Update RSVP
- ✅ Track plus-one responses

## 🆘 Troubleshooting

### RSVP link doesn't work
- Check XAMPP MySQL is running
- Verify database migration completed
- Ensure invitation is active

### Can't copy link
- Use manual copy (right-click)
- Or use "View Details" page

### Status not updating
- Refresh the page
- Check database directly
- Verify form submission succeeded

## 🎯 Best Practices

### Timing
- Send RSVP links 6-8 weeks before wedding
- Set deadline 2-3 weeks before
- Send reminders 1 week before deadline

### Communication
- Include RSVP deadline in message
- Provide contact info for questions
- Thank guests for responding

## 🔧 Customization

### Change Colors
Edit `templates/rsvp_form.html`:
```css
/* Line ~15 */
background: linear-gradient(135deg, #fdf8f3 0%, #f5e6d3 100%);
color: #c9a227; /* Gold color */
```

### Add Fields
1. Update database schema
2. Modify `templates/rsvp_form.html`
3. Update `blueprints/rsvp.py`

## 📈 Future Enhancements

Potential improvements:
- Email automation for RSVP links
- SMS notifications
- QR code generation
- Bulk guest import
- CSV export
- Dietary restrictions field
- Event-specific RSVP
- Guest check-in system

## 🤝 Support

Need help?
1. Check documentation files
2. Review test_rsvp.md
3. Verify database migration
4. Check Flask console for errors

## 📄 License

Part of Wedding Management System

## 🎉 Success!

Your RSVP system is ready! Start sharing links with your guests and track their responses in real-time.

---

**Made with ❤️ for your special day!**

For detailed documentation, see [RSVP_SYSTEM_GUIDE.md](RSVP_SYSTEM_GUIDE.md)
