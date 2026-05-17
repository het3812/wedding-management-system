# RSVP System - Quick Start Guide

## 🚀 Setup (One-Time)

### Step 1: Run Database Migration
```bash
python setup_rsvp.py
```
OR manually run `database_rsvp_migration.sql` in phpMyAdmin

### Step 2: Start Application
```bash
python app.py
```

## 📱 How to Use RSVP System

### For Wedding Hosts:

#### 1️⃣ Add Guests
1. Login at `http://127.0.0.1:5000/host/login`
2. Select your wedding invitation
3. Click "Guests"
4. Click "+ Add Guest"
5. Fill in guest details
6. RSVP link is automatically created!

#### 2️⃣ Share RSVP Links
- Click "📋 Copy Link" next to guest name
- Share via:
  - 📧 Email
  - 💬 WhatsApp
  - 📱 SMS
  - 💌 Any messaging app

#### 3️⃣ Track Responses
- View guest list to see status:
  - 🟢 **Confirmed** - Guest is coming
  - 🔴 **Declined** - Guest can't make it
  - 🟡 **Pending** - No response yet
- Click "View Details" to see messages
- Check summary at bottom for totals

### For Guests:

#### 1️⃣ Receive Link
Host sends you a unique link like:
```
http://127.0.0.1:5000/rsvp/abc123xyz...
```

#### 2️⃣ Open & Fill Form
- Open link on any device (phone/tablet/computer)
- See wedding details
- Choose: "Yes, I'll be there!" or "Sorry, can't make it"
- Add plus one if bringing someone
- Write message to couple (optional)

#### 3️⃣ Submit
- Click "Submit RSVP"
- Done! ✓
- Can update anytime using same link

## 📊 RSVP Dashboard Features

### Guest List View
```
┌─────────────────────────────────────────────────────────┐
│ Name      │ Email  │ Category │ Status    │ Plus One   │
├─────────────────────────────────────────────────────────┤
│ John Doe  │ john@  │ Friend   │ Confirmed │ +1 (Jane)  │
│ 💬 Has message                                          │
├─────────────────────────────────────────────────────────┤
│ [View Details] [📋 Copy Link] [Edit] [Delete]          │
└─────────────────────────────────────────────────────────┘
```

### Summary Statistics
```
┌──────────────────────────────────────┐
│  Confirmed: 45  │  Declined: 5  │  Pending: 10  │
└──────────────────────────────────────┘
```

## 🔗 Important URLs

| Purpose | URL |
|---------|-----|
| Host Login | `http://127.0.0.1:5000/host/login` |
| Host Dashboard | `http://127.0.0.1:5000/host/` |
| RSVP Form | `http://127.0.0.1:5000/rsvp/<token>` |
| Invitation | `http://127.0.0.1:5000/invite/<token>` |

## 💡 Tips & Tricks

### For Hosts:

1. **Bulk Sharing**
   - Copy all RSVP links
   - Create email template
   - Send personalized emails

2. **Follow Up**
   - Check pending responses weekly
   - Send reminders to pending guests
   - Update deadline in invitation

3. **Track Plus Ones**
   - Monitor plus one count
   - Plan seating accordingly
   - Update catering numbers

4. **Read Messages**
   - Check for dietary restrictions
   - Note special requests
   - Respond to questions

### For Guests:

1. **Save the Link**
   - Bookmark RSVP link
   - Can update response anytime
   - No need to ask host for new link

2. **Be Specific**
   - Mention dietary restrictions
   - Note accessibility needs
   - Ask questions in message

3. **Update Promptly**
   - Plans changed? Update RSVP
   - Host appreciates early notice
   - Helps with planning

## 🎨 Customization

### Change Theme Colors
Edit `templates/rsvp_form.html`:
```css
/* Line ~15 */
background: linear-gradient(135deg, #fdf8f3 0%, #f5e6d3 100%);

/* Line ~40 */
color: #c9a227; /* Gold color */
```

### Add Custom Fields
1. Update database schema
2. Modify `templates/rsvp_form.html`
3. Update `blueprints/rsvp.py`

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Link doesn't work | Check XAMPP MySQL is running |
| Can't copy link | Right-click → Copy, or use View Details |
| Status not updating | Refresh page, check database |
| Form won't submit | Check browser console, try different browser |
| No RSVP token | Run `setup_rsvp.py` or edit guest to regenerate |

## 📞 Support Checklist

Before asking for help:
- ✓ XAMPP MySQL is running
- ✓ Database migration completed
- ✓ Flask app is running
- ✓ No errors in console
- ✓ Tried different browser
- ✓ Checked database directly

## 🎯 Best Practices

### Timing
- Send RSVP links 6-8 weeks before wedding
- Set RSVP deadline 2-3 weeks before
- Send reminders 1 week before deadline

### Communication
- Include RSVP deadline in message
- Provide contact info for questions
- Thank guests for responding

### Planning
- Track responses daily
- Update vendor counts weekly
- Finalize numbers 1 week before

## 📈 Sample Workflow

```
Week 1: Add all guests → Generate RSVP links
Week 2: Send RSVP links via email/WhatsApp
Week 3-4: Monitor responses
Week 5: Send reminders to pending guests
Week 6: Follow up with non-responders
Week 7: Finalize count, update vendors
Week 8: Wedding day! 🎉
```

## 🔐 Security Notes

- Each guest has unique token
- Tokens are cryptographically secure
- Can't guess other guests' links
- No login required (token is key)
- Deactivate invitation to block all RSVPs

## 📱 Mobile Compatibility

RSVP form works on:
- ✓ iPhone (Safari, Chrome)
- ✓ Android (Chrome, Firefox)
- ✓ iPad/Tablets
- ✓ Desktop browsers
- ✓ All screen sizes

## 🎉 Success!

You're all set! Your guests can now RSVP easily from any device.

**Questions?** Check `RSVP_SYSTEM_GUIDE.md` for detailed documentation.

**Testing?** See `test_rsvp.md` for testing guide.

---

Made with ❤️ for your special day!
