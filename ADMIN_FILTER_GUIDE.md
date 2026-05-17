# Admin Dashboard Filter System - Guide

## Overview
Advanced filtering system for the admin dashboard to easily find and manage wedding invitations by date, status, host, and search terms.

## Features Added

### 1. Date Range Filter
- **From Date**: Filter invitations from a specific wedding date
- **To Date**: Filter invitations up to a specific wedding date
- Useful for finding upcoming weddings or past events

### 2. Status Filter
- **All Status**: Show all invitations
- **Active**: Show only active invitations
- **Inactive**: Show only inactive invitations

### 3. Host Filter
- Filter invitations by specific host
- Dropdown shows all registered hosts
- Useful for tracking specific host's events

### 4. Search Functionality
- Search across multiple fields:
  - Bride name
  - Groom name
  - Venue
  - Host name
- Real-time search with partial matching

### 5. Filter Results Summary
- Shows count of filtered results
- Displays active invitations count
- Shows upcoming invitations count
- Quick "Clear all filters" link

## How to Use

### Filter by Date Range

1. Go to Admin Dashboard
2. In the "Filter Invitations" section:
   - Select **From Date** (e.g., 2024-01-01)
   - Select **To Date** (e.g., 2024-12-31)
3. Click **Filter** button
4. View invitations within that date range

**Example Use Cases:**
- Find all weddings in March 2024
- Find upcoming weddings (from today onwards)
- Find past weddings for archiving

### Filter by Status

1. Select status from dropdown:
   - **All Status** - Show everything
   - **Active** - Only active invitations
   - **Inactive** - Only inactive invitations
2. Click **Filter**

**Use Cases:**
- Review only active invitations
- Find inactive invitations to reactivate
- Audit invitation status

### Filter by Host

1. Select host from dropdown
2. Click **Filter**
3. View all invitations for that specific host

**Use Cases:**
- Track specific host's events
- Review host's invitation history
- Manage host-specific issues

### Search Invitations

1. Enter search term in search box
2. Click **Search** button
3. Results show matches in:
   - Bride name
   - Groom name
   - Venue name
   - Host name

**Example Searches:**
- "John" - Find all invitations with John
- "Grand Hotel" - Find all weddings at Grand Hotel
- "Smith" - Find host or couple with Smith

### Combine Filters

You can combine multiple filters:

**Example 1: Upcoming Active Weddings**
- From Date: Today's date
- Status: Active
- Click Filter

**Example 2: Specific Host's March Weddings**
- From Date: 2024-03-01
- To Date: 2024-03-31
- Host: Select specific host
- Click Filter

**Example 3: Search Active Invitations**
- Status: Active
- Search: "Mumbai"
- Click Filter

### Clear Filters

**Method 1:** Click the **X** button next to Filter button

**Method 2:** Click "Clear all filters" link in results summary

**Method 3:** Click "Admin Dashboard" in navigation

## Filter Results Display

### Summary Bar
When filters are active, you'll see:
```
ℹ️ Filtered Results: Showing 15 invitation(s) | 12 active | 8 upcoming
```

### Statistics Cards
The dashboard cards update to show:
- Total invitations (filtered count)
- Active invitations count
- Upcoming invitations count

## Technical Details

### Backend Implementation

**File**: `blueprints/admin.py`

**Query Parameters:**
- `date_from` - Start date (YYYY-MM-DD)
- `date_to` - End date (YYYY-MM-DD)
- `status` - all/active/inactive
- `host` - Host user ID or 'all'
- `search` - Search term

**SQL Filtering:**
```python
# Date range
WHERE wedding_date >= date_from AND wedding_date <= date_to

# Status
WHERE is_active = 1  # or 0 for inactive

# Host
WHERE user_id = host_id

# Search
WHERE (bride_name LIKE '%term%' OR groom_name LIKE '%term%' 
       OR venue LIKE '%term%' OR host_name LIKE '%term%')
```

### Frontend Implementation

**File**: `templates/admin_dashboard.html`

**Filter Form:**
- Bootstrap 5 form layout
- Responsive grid (col-md-*)
- Preserves filter values after submit
- Clear filters button

## Performance Optimization

### Indexed Columns
The following columns are indexed for fast filtering:
- `invitations.wedding_date`
- `invitations.is_active`
- `invitations.user_id`
- `invitations.created_at`

### Query Optimization
- Uses parameterized queries (SQL injection safe)
- Only fetches required columns
- Efficient JOIN with users table
- ORDER BY optimized for date sorting

## Use Cases

### 1. Event Planning
**Scenario**: Find all weddings in next 3 months
- From Date: Today
- To Date: 3 months from today
- Status: Active

### 2. Host Management
**Scenario**: Review specific host's invitations
- Host: Select host name
- Status: All

### 3. Venue Analysis
**Scenario**: Find all weddings at specific venue
- Search: "Venue name"

### 4. Archive Management
**Scenario**: Find past inactive invitations
- To Date: Yesterday
- Status: Inactive

### 5. Upcoming Events
**Scenario**: Prepare for upcoming weddings
- From Date: Today
- To Date: Next month
- Status: Active

## Tips & Best Practices

1. **Use Date Ranges for Better Results**
   - Narrow down to specific months
   - Find seasonal patterns

2. **Combine Filters for Precision**
   - Date + Status for upcoming active events
   - Host + Date for host-specific timeline

3. **Use Search for Quick Lookup**
   - Faster than scrolling through list
   - Works across multiple fields

4. **Clear Filters Regularly**
   - Avoid confusion with old filters
   - Start fresh for new searches

5. **Bookmark Common Filters**
   - Save URLs with filter parameters
   - Quick access to frequent searches

## Troubleshooting

### No Results Shown

**Issue**: Filter returns no invitations

**Solutions:**
1. Check date range is correct
2. Verify status filter setting
3. Try clearing all filters
4. Check if invitations exist in database

### Wrong Results

**Issue**: Unexpected invitations in results

**Solutions:**
1. Review all active filters
2. Check date format (YYYY-MM-DD)
3. Clear filters and try again
4. Verify host selection

### Filter Not Working

**Issue**: Filter button doesn't work

**Solutions:**
1. Check browser console for errors
2. Verify Flask app is running
3. Check database connection
4. Review admin.py for errors

## Future Enhancements

Potential additions:
- Export filtered results to CSV
- Save filter presets
- Advanced date filters (this week, this month, etc.)
- Multiple host selection
- Venue filter dropdown
- Guest count filter
- Budget range filter

## API Endpoints

### Dashboard with Filters
```
GET /admin/?date_from=2024-01-01&date_to=2024-12-31&status=active&host=5&search=Mumbai
```

**Parameters:**
- `date_from` (optional): Start date
- `date_to` (optional): End date
- `status` (optional): all/active/inactive
- `host` (optional): Host ID or 'all'
- `search` (optional): Search term

## Examples

### Example 1: March 2024 Weddings
```
URL: /admin/?date_from=2024-03-01&date_to=2024-03-31
```

### Example 2: Active Invitations for Host #5
```
URL: /admin/?status=active&host=5
```

### Example 3: Search "Mumbai" in Active Invitations
```
URL: /admin/?status=active&search=Mumbai
```

### Example 4: Upcoming Weddings (Next 30 Days)
```
URL: /admin/?date_from=2024-03-05&date_to=2024-04-05&status=active
```

## Summary

The admin dashboard filter system provides:
- ✅ Date range filtering
- ✅ Status filtering (active/inactive)
- ✅ Host-specific filtering
- ✅ Full-text search
- ✅ Combined filter support
- ✅ Results summary
- ✅ Easy filter clearing
- ✅ Optimized performance

This makes managing wedding invitations efficient and organized!

---

**Version**: 1.0  
**Date**: March 2026  
**Status**: ✅ COMPLETE AND READY TO USE
