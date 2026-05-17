# Guest Count Feature - Implementation Complete

## Overview
Replaced "Plus One" option with "How many people are coming with you?" feature, allowing guests to specify the exact number of attendees (1-10 people).

## What Changed

### 1. Updated RSVP Form UI
**File**: `templates/invitation_unified.html`

**Old Feature**: Plus One (Yes/No with name field)
**New Feature**: Guest Count Selector (1-10 people)

**UI Components**:
- Number input field (center display)
- Plus (+) and Minus (-) buttons
- Range slider (1-10)
- Visual feedback with gold theme

### 2. Updated Backend Routes

**Files Modified**:
- `blueprints/invitation.py` - General RSVP submission
- `blueprints/rsvp.py` - Personal RSVP submission

**Changes**:
- Replaced `plus_one` (boolean) with `guest_count` (integer)
- Removed `plus_one_name` field
- Added validation for guest_count (1-10 range)
- Updated database queries

### 3. Database Migration
**File**: `database_guest_count_migration.sql`

**New Column**:
```sql
guest_count INT DEFAULT 1
```

**Migration Steps**:
1. Adds `guest_count` column to `guests` table
2. Migrates existing `plus_one` data (TRUE = 2, FALSE = 1)
3. Optional: Remove old `plus_one` columns

## Features

### Guest Count Selector

**Three Ways to Select**:
1. **Plus/Minus Buttons**: Click to increment/decrement
2. **Range Slider**: Drag to select number
3. **Direct Input**: Number field (read-only for consistency)

**Range**: 1 to 10 people (including the guest themselves)

**Visual Design**:
- Gold circular buttons with hover effects
- Large, centered number display
- Smooth animations
- Mobile-friendly touch targets

### Form Behavior

**Personalized RSVP** (`/rsvp/<token>`):
- Pre-filled with existing guest_count if available
- Defaults to 1 if new submission
- Updates guest record on submission

**General RSVP** (`/invite/<token>`):
- Starts at 1 person
- Creates new guest record with count
- Validates range (1-10)

## User Experience

### Desktop
- Large, easy-to-click buttons
- Smooth hover effects
- Visual feedback on interaction
- Slider for quick selection

### Mobile
- Touch-friendly button size (45px circles)
- Responsive layout
- Slider works with touch
- Clear visual hierarchy

## Technical Details

### JavaScript Functions

**For Personalized RSVP**:
- `updateGuestCount(value)` - Updates from slider
- `incrementGuests()` - Increases count
- `decrementGuests()` - Decreases count

**For General RSVP**:
- `updateGuestCountGeneral(value)` - Updates from slider
- `incrementGuestsGeneral()` - Increases count
- `decrementGuestsGeneral()` - Decreases count

### Validation
- Minimum: 1 person
- Maximum: 10 people
- Server-side validation
- Client-side range enforcement

### Database Schema

**New Field**:
```sql
guest_count INT DEFAULT 1
```

**Stored Values**:
- 1 = Just the guest
- 2 = Guest + 1 person
- 3 = Guest + 2 people
- ... up to 10

## Benefits

✅ **More Accurate**: Exact headcount instead of just +1
✅ **Flexible**: Supports families and groups
✅ **User Friendly**: Multiple input methods
✅ **Visual**: Clear, intuitive interface
✅ **Mobile Optimized**: Works great on phones
✅ **Better Planning**: Hosts get exact numbers

## Admin Benefits

### For Wedding Hosts
- Accurate guest count for planning
- Better catering estimates
- Seating arrangement planning
- Venue capacity management
- Budget calculations

### Reporting
- Total confirmed guests
- Total declined guests
- Total expected attendees (sum of guest_count)
- Per-guest breakdown

## Migration Guide

### Step 1: Run Database Migration
```sql
-- Run database_guest_count_migration.sql in phpMyAdmin
USE wedding_db;
ALTER TABLE guests ADD COLUMN guest_count INT DEFAULT 1 AFTER rsvp_submitted_at;
```

### Step 2: Migrate Existing Data (Optional)
```sql
-- Convert plus_one to guest_count
UPDATE guests 
SET guest_count = CASE WHEN plus_one = TRUE THEN 2 ELSE 1 END
WHERE guest_count IS NULL;
```

### Step 3: Test
- Submit new RSVP via invitation link
- Submit RSVP via personal link
- Verify guest_count is saved
- Check admin panel shows correct counts

## Backward Compatibility

**Old Columns Preserved**:
- `plus_one` (boolean)
- `plus_one_name` (varchar)

**Why Keep Them**:
- Existing data preserved
- No data loss
- Can reference old RSVPs
- Easy rollback if needed

**Can Be Removed**:
```sql
ALTER TABLE guests DROP COLUMN plus_one;
ALTER TABLE guests DROP COLUMN plus_one_name;
```

## Example Use Cases

### Scenario 1: Single Guest
- Guest selects: 1 person
- Meaning: Just themselves
- Database: guest_count = 1

### Scenario 2: Couple
- Guest selects: 2 people
- Meaning: Themselves + partner
- Database: guest_count = 2

### Scenario 3: Family
- Guest selects: 5 people
- Meaning: Themselves + 4 family members
- Database: guest_count = 5

### Scenario 4: Large Group
- Guest selects: 10 people
- Meaning: Maximum allowed
- Database: guest_count = 10

## Admin Panel Integration

### Guest List View
Display guest_count for each guest:
```
John Doe - Confirmed - 3 people
Jane Smith - Confirmed - 2 people
Bob Johnson - Declined - 1 person
```

### Total Count Calculation
```sql
SELECT SUM(guest_count) as total_attendees 
FROM guests 
WHERE rsvp_status = 'Confirmed';
```

## Future Enhancements (Optional)

- Individual names for each guest in party
- Age groups (adults/children)
- Meal preferences per person
- Special requirements per guest
- Seating preferences
- Transportation needs
- Accommodation requirements

## Testing Checklist

- [ ] Submit RSVP with 1 person
- [ ] Submit RSVP with 5 people
- [ ] Submit RSVP with 10 people (max)
- [ ] Try to exceed 10 (should cap at 10)
- [ ] Try to go below 1 (should stay at 1)
- [ ] Test slider functionality
- [ ] Test +/- buttons
- [ ] Test on mobile device
- [ ] Verify database saves correctly
- [ ] Check admin panel displays count
- [ ] Test both personalized and general RSVP

## CSS Styling

**Colors**:
- Primary: #c9a227 (gold)
- Background: white
- Hover: gold background with white text

**Sizes**:
- Buttons: 45px × 45px circles
- Input: 80px width, 1.5rem font
- Slider: Full width with gold accent

**Effects**:
- Hover: Scale 1.1
- Active: Scale 0.95
- Transitions: 0.3s smooth

## Notes

- Maximum set to 10 to prevent unrealistic numbers
- Can be adjusted in code if needed
- Slider provides visual feedback
- Buttons provide precise control
- Read-only input prevents manual typing errors
- All three methods sync automatically

## Support

If issues occur:
1. Run database migration first
2. Clear browser cache
3. Check console for JavaScript errors
4. Verify database column exists
5. Test with different browsers
6. Check mobile responsiveness
