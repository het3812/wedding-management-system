# 🏪 Comprehensive Vendor Management System

A complete, production-ready vendor management system for wedding services with advanced features including profiles, chat, gallery, ratings, filtering, and auto-blocking policy.

## 🌟 Features

### For Vendors
- ✅ Complete profile management (contact, location, social links)
- ✅ Portfolio gallery with multiple images
- ✅ Service listings with prices
- ✅ Booking management
- ✅ Real-time chat with customers
- ✅ Rating and review system
- ✅ Activity tracking

### For Users/Hosts
- ✅ Browse vendors by category
- ✅ Advanced filtering (location, rating, price)
- ✅ Search functionality
- ✅ View detailed vendor profiles
- ✅ Book services
- ✅ Chat with vendors
- ✅ Leave reviews and ratings

### For Admins
- ✅ Vendor approval system
- ✅ Activity monitoring
- ✅ Auto-blocking policy management
- ✅ Block history tracking
- ✅ Reactivation fee management

## 🚀 Quick Start

### Installation (5 Minutes)

#### Option 1: Automated (Windows)
```bash
install_vendor_system.bat
```

#### Option 2: Manual
```bash
# 1. Setup database
python setup_vendor_enhancement.py

# 2. Start application
python app.py
```

### Access Points
- **Marketplace**: http://127.0.0.1:5000/marketplace
- **Vendor Dashboard**: http://127.0.0.1:5000/vendor/
- **Chat**: http://127.0.0.1:5000/chat/

## 📦 What's Included

### Backend (Python/Flask)
- `blueprints/marketplace.py` - Public vendor discovery
- `blueprints/chat.py` - Real-time chat system
- `blueprints/vendor.py` - Enhanced vendor features
- `database_vendor_enhancement.sql` - Database schema
- `setup_vendor_enhancement.py` - Setup automation

### Frontend (HTML/CSS/JS)
- 11 responsive templates
- Mobile-friendly design
- Bootstrap 5.3.2
- Real-time chat interface
- Advanced filtering UI

### Database
- 6 new tables
- 20+ new columns
- Optimized indexes
- Relationship management

## 🎯 Key Features

### 1. Enhanced Vendor Profiles
```
- Business name & description
- Category selection (9 categories)
- Contact info (email, phone)
- Website & Instagram links
- Location (city, state, area)
- Google Maps ready
```

### 2. Real-Time Chat System
```
- In-website messaging
- No external redirects
- Chat history
- Unread tracking
- 3-second polling
```

### 3. Vendor Gallery
```
- Multiple photo uploads
- Image captions
- Portfolio showcase
- Easy management
```

### 4. Rating & Reviews
```
- 5-star rating system
- Written reviews
- Average calculation
- Review restrictions
```

### 5. Advanced Filtering
```
- Category filter
- Location filter
- Rating filter (4+, 3+)
- Price sorting
- Search
- Combined filters
```

### 6. Booking System
```
- Service booking
- Event date selection
- Status tracking
- Booking history
- Price management
```

### 7. Auto-Blocking Policy
```
- 90-day inactivity tracking
- Automatic blocking
- Reactivation fee (₹4,989)
- Fee doubling system
- 3-month validity
- 3 orders requirement
```

## 📊 Vendor Categories

1. Photographer
2. Clothes/Boutique
3. Party Plot
4. Car Booking
5. Makeup Artist
6. Mehendi Artist
7. Pandit
8. Catering
9. Decoration

## 🔧 Configuration

### Required
- Python 3.7+
- Flask
- MySQL (XAMPP)
- Bootstrap 5.3.2 (CDN)

### Optional
- Google Maps API (for maps)
- Flask-Mail (for emails)
- Twilio (for SMS)
- Payment gateway (for fees)

## 📚 Documentation

| File | Description |
|------|-------------|
| [VENDOR_SYSTEM_IMPLEMENTATION.md](VENDOR_SYSTEM_IMPLEMENTATION.md) | Complete technical guide |
| [VENDOR_QUICK_START.md](VENDOR_QUICK_START.md) | Quick reference |
| [VENDOR_CHECKLIST.md](VENDOR_CHECKLIST.md) | Testing checklist |
| [VENDOR_IMPLEMENTATION_COMPLETE.md](VENDOR_IMPLEMENTATION_COMPLETE.md) | Implementation summary |

## 🎨 Screenshots

### Marketplace
```
┌─────────────────────────────────────┐
│ Find Wedding Vendors                │
├─────────────────────────────────────┤
│ [Search] [Category▼] [City▼] [Sort▼]│
├─────────────────────────────────────┤
│ ┌──────┐  ┌──────┐  ┌──────┐       │
│ │Photo │  │Photo │  │Photo │       │
│ │★★★★★│  │★★★★☆│  │★★★☆☆│       │
│ │Vendor│  │Vendor│  │Vendor│       │
│ └──────┘  └──────┘  └──────┘       │
└─────────────────────────────────────┘
```

### Vendor Profile
```
┌─────────────────────────────────────┐
│ Business Name                       │
│ ★★★★★ (25 reviews)                 │
│ 📍 Mumbai, Maharashtra              │
│ 📧 contact@vendor.com               │
│ 🌐 Website | 📷 Instagram           │
├─────────────────────────────────────┤
│ [Book Now] [Chat]                   │
├─────────────────────────────────────┤
│ Services | Gallery | Reviews        │
└─────────────────────────────────────┘
```

### Chat Interface
```
┌─────────────────────────────────────┐
│ Chat with Vendor Name               │
├─────────────────────────────────────┤
│     Hello! I'm interested     ┌─────┤
│                                     │
│ ┌───── Thank you for reaching out! │
│                                     │
│     What's your pricing?      ┌─────┤
│                                     │
│ ┌───── Starting from ₹10,000       │
├─────────────────────────────────────┤
│ [Type message...] [Send]            │
└─────────────────────────────────────┘
```

## 🔒 Security

- SQL injection prevention
- XSS prevention
- Access control
- File upload validation
- Chat access restrictions
- Booking access restrictions
- Review access restrictions

## 📈 Performance

- Database indexes
- Efficient queries
- Image optimization ready
- Pagination ready
- Caching ready

## 🐛 Troubleshooting

### Database Error
```bash
# Check MySQL is running
# Verify database exists
# Run setup script again
python setup_vendor_enhancement.py
```

### Chat Not Working
```bash
# Check JavaScript console
# Verify polling endpoint
# Clear browser cache
```

### Images Not Showing
```bash
# Check upload folder permissions
# Verify image paths
# Check file size limits
```

## 🧪 Testing

### Quick Test
```bash
# 1. Register as vendor
# 2. Admin approves vendor
# 3. Vendor completes profile
# 4. User browses marketplace
# 5. User books vendor
# 6. Chat between user and vendor
# 7. User leaves review
```

### Full Test
See [VENDOR_CHECKLIST.md](VENDOR_CHECKLIST.md) for complete testing guide.

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production
```bash
# Use Gunicorn or uWSGI
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Cron Job (Auto-Blocking)
```bash
# Add to crontab
0 0 * * * /usr/bin/python /path/to/check_inactive_vendors.py
```

## 📞 Support

### Getting Help
1. Check documentation files
2. Review template files
3. Check Flask console
4. Verify database schema
5. Test step by step

### Common Issues
- MySQL not running → Start XAMPP
- Database not found → Run setup script
- Import errors → Check file paths
- Template errors → Check syntax

## 🎉 Success Metrics

Your system is working when:
- ✅ Vendors can register and manage profiles
- ✅ Users can discover and book vendors
- ✅ Chat facilitates communication
- ✅ Bookings are tracked properly
- ✅ Reviews build credibility
- ✅ Inactive vendors are managed
- ✅ No critical errors

## 🔄 Updates & Maintenance

### Regular Tasks
- Daily: Check error logs
- Weekly: Review vendors
- Monthly: Database backup
- Quarterly: Security audit

### Future Enhancements
- WebSocket for real-time chat
- Email notifications
- Payment gateway
- SMS notifications
- Mobile app

## 📄 License

Part of Wedding Management System

## 🤝 Contributing

1. Test thoroughly
2. Document changes
3. Follow code style
4. Submit feedback

## 🎊 Acknowledgments

Built with:
- Flask (Python web framework)
- Bootstrap 5 (UI framework)
- MySQL (Database)
- JavaScript (Frontend interactivity)

---

## 📝 Quick Reference

### URLs
```
/marketplace                    - Browse vendors
/marketplace/vendor/<id>        - Vendor profile
/marketplace/vendor/<id>/book   - Book vendor
/marketplace/my-bookings        - My bookings
/chat/                          - Chat list
/chat/<id>                      - Chat view
/vendor/                        - Vendor dashboard
/vendor/profile/edit            - Edit profile
/vendor/gallery                 - Manage gallery
/vendor/bookings                - Vendor bookings
```

### Database Tables
```
vendors                 - Vendor profiles
vendor_gallery          - Portfolio images
vendor_services         - Service listings
vendor_bookings         - Bookings/orders
vendor_reviews          - Ratings & reviews
vendor_chats            - Chat conversations
chat_messages           - Chat messages
vendor_block_history    - Block tracking
```

### Key Files
```
blueprints/marketplace.py       - Public discovery
blueprints/chat.py              - Chat system
blueprints/vendor.py            - Vendor features
database_vendor_enhancement.sql - Database schema
setup_vendor_enhancement.py     - Setup script
```

---

**Ready to launch!** 🚀

For detailed information, see the documentation files in the project root.
