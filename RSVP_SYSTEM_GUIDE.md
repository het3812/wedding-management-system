# RSVP System Implementation Guide

## Overview
This RSVP system allows wedding hosts to send personalized RSVP links to guests. Guests can access these links from any device to confirm or decline their attendance, add a plus one, and send messages to the couple.

## Features

### For Hosts:
- Generate unique RSVP links for each guest
- View RSVP status (Confirmed/Declined/Pending)
- See guest messages and dietary requirements
- Track plus-one responses
- Copy RSVP links with one click
- View RSVP summary statistics
- Access detailed RSVP responses

### For Guests:
- Mobile-friendly RSVP form
- Confirm or decline attendance
- Add plus-one information
- Send messages to the couple
- View event schedule
- Update RSVP anytime using the same link

## Installation Steps

### 1. Database Migration
Run the SQL migration to add RSVP functionality:

```sql
-- Open phpMyAdmin (XAMPP)
-- Select wedding_db database
-- Run the following SQL:

USE wedding_db;

ALTER TABLE guests 
ADD COLUMN rsvp_token VARCHAR(64) UNIQUE AFTER phone,
ADD COLUMN rsvp_response TEXT AFTER rsvp_status,
ADD COLUMN rsvp_submitted_at TIMESTAMP NULL AFTER rsvp_response,
ADD COLUMN plus_one BOOLEAN DEFAULT FALSE AFTER category,
ADD COLUMN plus_one_name VARCHAR(100) AFTER plus_one;

CREATE INDEX idx_rsvp_token ON guests(rsvp_token);

-- Optional: Generate tokens for existing guests
UPDATE guests SET rsvp_token = CONCAT(MD5(CONCAT(id, email, RAND())), SUBSTRING(MD5(RAND()), 1, 8)) 
WHERE rsvp_token IS NULL;
```

Or simply run the file `database_rsvp_migration.sql` in phpMyAdmin.

### 2. Start the Application
```bash
# Make sure XAMPP MySQL is running
# Start Flask application
python app.py
```

The application will run on `http://127.0.0.1:5000`

## How to Use

### For Hosts:

1. **Login as Host**
   - Go to `http://127.0.0.1:5000/host/login`
   - Login with your host credentials

2. **Add Guests**
   - Navigate to your invitation dashboard
   - Click on "Guests" for your wedding
   - Click "+ Add Guest"
   - Fill in guest details (name, email, phone, category)
   - RSVP token is automatically generated

3. **Share RSVP Links**
   - In the guest list, click "📋 Copy Link" button
   - Share the link via email, WhatsApp, SMS, etc.
   - Each guest has a unique link

4. **Monitor Responses**
   - View RSVP status in the guest list
   - See summary statistics (Confirmed/Declined/Pending)
   - Click "View Details" to see guest messages

### For Guests:

1. **Receive RSVP Link**
   - Host sends you a unique link like:
   - `http://127.0.0.1:5000/rsvp/abc123xyz...`

2. **Fill RSVP Form**
   - Open the link on any device (phone, tablet, computer)
   - See wedding details and event schedule
   - Choose "Yes, I'll be there!" or "Sorry, can't make it"
   - Indicate if bringing a plus one
   - Add optional message to the couple

3. **Submit Response**
   - Click "Submit RSVP"
   - See confirmation message
   - Can update response anytime using same link

## URL Structure

- **RSVP Form**: `/rsvp/<unique_token>`
- **Invitation View**: `/invite/<invitation_token>`
- **Gallery**: `/gallery/<invitation_token>`
- **Host Dashboard**: `/host/`

## Database Schema

### guests table (updated):
```sql
- id (INT, PRIMARY KEY)
- invitation_id (INT, FOREIGN KEY)
- name (VARCHAR)
- email (VARCHAR)
- phone (VARCHAR)
- category (ENUM: Family/Friend/VIP)
- rsvp_status (ENUM: Pending/Confirmed/Declined)
- rsvp_token (VARCHAR, UNIQUE) -- NEW
- rsvp_response (TEXT) -- NEW
- rsvp_submitted_at (TIMESTAMP) -- NEW
- plus_one (BOOLEAN) -- NEW
- plus_one_name (VARCHAR) -- NEW
```

## Security Features

- Unique cryptographic tokens (32 bytes, URL-safe)
- Token validation on every request
- No authentication required (token is the key)
- Tokens are non-guessable
- Can only access own RSVP form

## Mobile Responsive

The RSVP form is fully responsive and works on:
- Smartphones (iOS, Android)
- Tablets
- Desktop browsers
- All modern browsers

## Customization

### Change Colors:
Edit `templates/rsvp_form.html` and modify the CSS:
```css
--wedding-gold: #c9a227;  /* Change to your theme color */
```

### Add More Fields:
1. Update database schema
2. Add fields to `templates/rsvp_form.html`
3. Update `blueprints/rsvp.py` to handle new fields

### Email Notifications:
To send RSVP links via email, integrate with:
- Flask-Mail
- SendGrid
- Mailgun
- SMTP

## Troubleshooting

### RSVP Link Shows Error:
- Check if MySQL is running in XAMPP
- Verify database migration was successful
- Ensure invitation is active (`is_active = 1`)

### Token Not Generated:
- Check if guest was added after migration
- Manually update guest: Edit guest and save again

### Can't Copy Link:
- Use manual copy: Right-click → Copy
- Or use "View Details" to see full link

## Testing

### Test RSVP Flow:
1. Login as host
2. Add a test guest
3. Copy RSVP link
4. Open in incognito/private window
5. Fill and submit RSVP
6. Check host dashboard for response

## Production Deployment

For production use:
1. Use HTTPS (SSL certificate)
2. Change `SECRET_KEY` in config.py
3. Use production database (not XAMPP)
4. Set `debug=False` in app.py
5. Use proper web server (Gunicorn, uWSGI)

## Support

For issues or questions:
- Check database connection
- Verify all files are in place
- Check Flask console for errors
- Ensure XAMPP MySQL is running

## Files Added/Modified

### New Files:
- `blueprints/rsvp.py` - RSVP blueprint
- `templates/rsvp_form.html` - RSVP form
- `templates/rsvp_success.html` - Success page
- `templates/rsvp_error.html` - Error page
- `templates/host_guest_rsvp_detail.html` - RSVP details view
- `database_rsvp_migration.sql` - Database migration

### Modified Files:
- `app.py` - Register RSVP blueprint
- `blueprints/host.py` - Generate RSVP tokens
- `templates/host_guests.html` - Show RSVP links and stats
- `templates/invitation.html` - Add RSVP note

## License
Part of Wedding Management System
