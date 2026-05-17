# RSVP System Testing Guide

## Quick Test Steps

### 1. Setup Database
```bash
# Option A: Run setup script (recommended)
python setup_rsvp.py

# Option B: Manual SQL in phpMyAdmin
# Open phpMyAdmin → wedding_db → SQL tab
# Copy and paste contents of database_rsvp_migration.sql
# Click "Go"
```

### 2. Start Application
```bash
python app.py
```

### 3. Test as Host

1. **Login**
   - Go to: `http://127.0.0.1:5000/host/login`
   - Use your host credentials (or register new account)

2. **Create/Select Invitation**
   - Create a new wedding invitation if needed
   - Or select existing invitation from dashboard

3. **Add Test Guest**
   - Click "Guests" for your invitation
   - Click "+ Add Guest"
   - Fill in:
     - Name: "John Doe"
     - Email: "john@example.com"
     - Phone: "1234567890"
     - Category: "Friend"
   - Click "Add Guest"

4. **Copy RSVP Link**
   - In guest list, find "John Doe"
   - Click "📋 Copy Link" button
   - Link should be copied to clipboard
   - Format: `http://127.0.0.1:5000/rsvp/[unique-token]`

### 4. Test as Guest

1. **Open RSVP Link**
   - Open new incognito/private browser window
   - Paste the RSVP link
   - You should see the RSVP form

2. **Fill RSVP Form**
   - See wedding details and event schedule
   - Click "Yes, I'll be there!" or "Sorry, can't make it"
   - Select plus one option (Yes/No)
   - If yes, enter plus one name
   - Add optional message: "Looking forward to it!"
   - Click "Submit RSVP"

3. **Verify Success**
   - Should see success page
   - Message confirms submission

### 5. Verify as Host

1. **Check Guest List**
   - Go back to host dashboard
   - Navigate to Guests page
   - Find "John Doe"
   - Status should show "Confirmed" or "Declined"
   - Should see "💬 Has message" if message was added
   - Plus one indicator should show if selected

2. **View RSVP Details**
   - Click "View Details" button
   - See full RSVP response
   - See submission timestamp
   - See guest message
   - See plus one information

3. **Check Summary**
   - Scroll to bottom of guest list
   - See RSVP Summary card with counts:
     - Confirmed: X
     - Declined: Y
     - Pending: Z

### 6. Test RSVP Update

1. **Reopen RSVP Link**
   - Use same RSVP link again
   - Should show previous response
   - Alert shows "You have already responded"

2. **Update Response**
   - Change selection (Confirmed ↔ Declined)
   - Update message
   - Submit again

3. **Verify Update**
   - Check host dashboard
   - Status should be updated
   - Timestamp should be updated

## Test Scenarios

### Scenario 1: Mobile Device
- Open RSVP link on smartphone
- Verify responsive design
- Test form submission
- Check all buttons work

### Scenario 2: Multiple Guests
- Add 5-10 test guests
- Copy each RSVP link
- Submit different responses:
  - Some confirmed
  - Some declined
  - Some pending (don't submit)
- Verify summary statistics

### Scenario 3: Plus One
- Submit RSVP with plus one
- Verify plus one name appears in host view
- Check badge shows "+1"

### Scenario 4: Guest Messages
- Submit RSVP with long message
- Verify message displays correctly
- Check special characters work

### Scenario 5: Invalid Token
- Try accessing: `http://127.0.0.1:5000/rsvp/invalid-token-123`
- Should show error page
- Message: "This RSVP link is invalid or has expired"

### Scenario 6: Inactive Invitation
- As admin/host, deactivate invitation
- Try accessing RSVP link
- Should show error: "This invitation has been deactivated"

## Expected Results

✓ RSVP form loads on all devices
✓ Form is mobile-responsive
✓ Can submit confirmation
✓ Can submit decline
✓ Can add plus one
✓ Can add message
✓ Can update RSVP
✓ Host sees all responses
✓ Summary statistics are correct
✓ Copy link button works
✓ Invalid tokens show error
✓ Inactive invitations blocked

## Common Issues

### Issue: "Database connection failed"
**Solution**: Start XAMPP MySQL

### Issue: "RSVP link is invalid"
**Solution**: 
- Check if guest has rsvp_token in database
- Run setup_rsvp.py to generate tokens

### Issue: "Copy Link" button doesn't work
**Solution**: 
- Use manual copy (right-click)
- Or use "View Details" to see full link

### Issue: Form doesn't submit
**Solution**:
- Check browser console for errors
- Ensure JavaScript is enabled
- Try different browser

### Issue: Status not updating
**Solution**:
- Refresh page
- Check database directly
- Verify form submission succeeded

## Database Verification

Check data directly in phpMyAdmin:

```sql
-- View all guests with RSVP tokens
SELECT id, name, email, rsvp_status, rsvp_token, rsvp_submitted_at, plus_one, plus_one_name
FROM guests;

-- View RSVP responses
SELECT name, rsvp_status, rsvp_response, rsvp_submitted_at
FROM guests
WHERE rsvp_submitted_at IS NOT NULL;

-- Count by status
SELECT rsvp_status, COUNT(*) as count
FROM guests
GROUP BY rsvp_status;
```

## Performance Test

For large guest lists:
1. Add 100+ guests
2. Check page load time
3. Test search/filter (if implemented)
4. Verify all RSVP links work

## Security Test

1. Try accessing another guest's RSVP with wrong token
2. Try SQL injection in form fields
3. Try XSS in message field
4. Verify tokens are unique and random

## Success Criteria

- [ ] Database migration successful
- [ ] RSVP links generated for all guests
- [ ] RSVP form accessible and responsive
- [ ] Form submission works
- [ ] Host can view responses
- [ ] Summary statistics accurate
- [ ] Copy link functionality works
- [ ] Error handling works
- [ ] Can update RSVP
- [ ] Plus one feature works
- [ ] Messages display correctly

## Next Steps After Testing

1. Customize colors/styling
2. Add email notifications
3. Add SMS integration
4. Export guest list to CSV
5. Print guest list
6. Add dietary restrictions field
7. Add attendance tracking for multiple events
