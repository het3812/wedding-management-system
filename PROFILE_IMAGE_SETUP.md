# Invitation Profile Image - Setup Guide

## Issue: Profile Image Not Showing

If you uploaded a profile image but it's not showing, the database column needs to be added first.

---

## Quick Fix - Run Installation

### Option 1: Double-click the batch file
```
install_invitation_profile_image.bat
```

### Option 2: Run Python script
```bash
python install_invitation_profile_image.py
```

---

## What This Does

Adds `profile_image` column to the `invitations` table in your database.

---

## After Installation

1. **Restart your Flask app** (if running)
2. Go to Host Dashboard
3. Click "Edit" on your invitation
4. Upload a profile image
5. Save
6. **Refresh the dashboard** - image will now appear!

---

## Where Profile Images Appear

✅ **Host Dashboard** - On invitation cards
✅ **Invitation Page** - At the top (circular image)
✅ **RSVP Form** - At the top (circular image)
✅ **Admin Dashboard** - On invitation cards

---

## Troubleshooting

### Image still not showing after upload?

1. **Check database column exists:**
   ```sql
   DESCRIBE invitations;
   ```
   Look for `profile_image` column

2. **Check file was uploaded:**
   - Look in `static/uploads/{invitation_id}/profile/`
   - File should be there

3. **Check database has path:**
   ```sql
   SELECT id, bride_name, groom_name, profile_image FROM invitations;
   ```
   Should show path like `uploads/1/profile/profile_xxxx_image.jpg`

4. **Restart Flask app:**
   ```bash
   # Stop the app (Ctrl+C)
   python app.py
   ```

### Installation fails?

**Error: "Duplicate column"**
- Column already exists, you're good!

**Error: "Can't connect to database"**
- Make sure XAMPP MySQL is running
- Check database name is `wedding_db`

---

## Manual Installation (if script fails)

Run this SQL in phpMyAdmin:

```sql
ALTER TABLE invitations 
ADD COLUMN profile_image VARCHAR(255) DEFAULT NULL;
```

---

## File Upload Specifications

- **Formats**: PNG, JPG, JPEG, GIF, WEBP
- **Max Size**: 16MB
- **Recommended**: 800x600px or larger
- **Storage**: `static/uploads/{invitation_id}/profile/`

---

## Complete!

Once installed, profile images will:
- Help identify invitations visually
- Appear on invitation and RSVP pages
- Make the system more personal and recognizable

**Status**: ✅ Feature Ready (after database migration)
