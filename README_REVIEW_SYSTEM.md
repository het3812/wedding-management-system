# ⭐ Rating & Review System

## 🎯 Overview

A complete rating and review system for the wedding management marketplace that enables customers to rate vendors, write detailed reviews, and help other customers make informed decisions.

---

## ✨ Features

### Customer Features
- ⭐ **Star Ratings** - Rate vendors from 1-5 stars
- 📝 **Text Reviews** - Write detailed feedback
- ✏️ **Edit Reviews** - Update your reviews anytime
- 🗑️ **Delete Reviews** - Remove your reviews
- 👍 **Helpful Voting** - Mark reviews as helpful/unhelpful
- 🚩 **Report Reviews** - Flag inappropriate content
- ✅ **Verified Badges** - See verified booking badges
- 🔍 **Filter & Sort** - Find relevant reviews easily

### Vendor Features
- 📊 **View Reviews** - See all customer feedback
- 💬 **Respond to Reviews** - Engage with customers
- ✏️ **Edit Responses** - Update your responses
- 🗑️ **Delete Responses** - Remove responses
- 📈 **Rating Analytics** - Track your performance
- 🎯 **Filter Reviews** - Find specific feedback

---

## 🚀 Quick Start

### Installation (3 Steps)

#### Option A: Automated (Recommended)
```bash
python install_review_system.py
```

#### Option B: Manual
```bash
# 1. Open phpMyAdmin
# 2. Select 'wedding_db' database
# 3. Import 'database_review_enhancement.sql'
# 4. Restart application: python app.py
```

### First Review (5 Steps)
1. Login as host
2. Book a vendor
3. Vendor marks booking as "Completed"
4. Host writes review
5. Done! ✅

---

## 📖 User Guide

### Writing a Review

1. **Visit Vendor Profile**
   - Browse marketplace
   - Click on vendor

2. **Click "Write Review"**
   - Button appears if you have a completed booking

3. **Rate the Vendor**
   - Select 1-5 stars
   - 5 stars = Excellent
   - 1 star = Poor

4. **Write Your Review** (Optional)
   - Share your experience
   - Be honest and helpful
   - Include specific details

5. **Submit**
   - Review appears instantly
   - Verified booking badge shown

### Editing Your Review

1. Find your review on vendor profile
2. Click three-dot menu (⋮)
3. Select "Edit"
4. Update rating or text
5. Click "Update Review"

### Marking Reviews Helpful

1. Read a review
2. Click "Helpful" if it helped you
3. Click "Not Helpful" if it didn't
4. Counts update in real-time

### Reporting a Review

1. Click "Report" button
2. Select reason:
   - Spam
   - Offensive Language
   - Fake Review
   - Irrelevant Content
   - Other
3. Add description (optional)
4. Submit report

---

## 🏪 Vendor Guide

### Viewing Reviews

1. **Login to Dashboard**
   - Click "Reviews" button

2. **See All Reviews**
   - Rating distribution
   - Individual reviews
   - Helpful counts

3. **Filter Reviews**
   - By rating (1-5 stars)
   - By sort (recent, helpful, rating)

### Responding to Reviews

1. **Find Review**
   - Go to Reviews page
   - Locate review to respond to

2. **Click "Respond"**
   - Write professional response
   - Thank customer for feedback
   - Address any concerns

3. **Submit Response**
   - Response appears on public profile
   - Customers see your engagement

### Best Practices

✅ **Do:**
- Respond to all reviews
- Thank customers for feedback
- Address concerns professionally
- Keep responses brief
- Be courteous and helpful

❌ **Don't:**
- Argue with customers
- Ask for review removal
- Post defensive responses
- Use offensive language
- Ignore negative feedback

---

## 🎨 UI Preview

### Vendor Profile - Reviews Section
```
┌──────────────────────────────────────────────┐
│ ⭐ Customer Reviews                          │
│                                              │
│ 4.8 ★★★★★ (24 reviews)                      │
│                                              │
│ Rating Distribution:                         │
│ 5 ★ ████████████████████ 18                 │
│ 4 ★ ████████             5                  │
│ 3 ★ ██                   1                  │
│ 2 ★                      0                  │
│ 1 ★                      0                  │
│                                              │
│ Filter: [All Ratings ▼]  Sort: [Recent ▼]  │
│                                              │
│ ┌────────────────────────────────────────┐  │
│ │ John Doe ✓ Verified Booking            │  │
│ │ ★★★★★ December 15, 2025                │  │
│ │                                         │  │
│ │ Excellent service! Very professional... │  │
│ │                                         │  │
│ │ 🏪 Vendor Response:                     │  │
│ │ Thank you for your feedback!            │  │
│ │ December 16, 2025                       │  │
│ │                                         │  │
│ │ Was this helpful?                       │  │
│ │ 👍 Helpful (12)  👎 Not Helpful (1)    │  │
│ │                          🚩 Report      │  │
│ └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

### Tables

**vendor_reviews** - Main review table
- rating (1-5 stars)
- review_text
- helpful_count
- unhelpful_count
- vendor_response
- is_verified_booking

**review_helpfulness** - Helpful voting
- review_id
- user_id
- is_helpful (true/false)

**review_reports** - Review reporting
- review_id
- reporter_user_id
- reason
- status

---

## 🔧 Technical Details

### API Endpoints

**Customer:**
- `POST /marketplace/vendor/<id>/review` - Add/update review
- `POST /marketplace/review/<id>/helpful` - Vote helpful
- `POST /marketplace/review/<id>/report` - Report review
- `POST /marketplace/review/<id>/delete` - Delete review

**Vendor:**
- `GET /vendor/reviews` - View all reviews
- `POST /vendor/reviews/<id>/respond` - Respond to review
- `POST /vendor/reviews/<id>/delete-response` - Delete response

### Rating Calculation
```python
average_rating = SUM(rating) / COUNT(reviews)
```

### Verified Booking Logic
```python
is_verified = EXISTS(
    SELECT 1 FROM vendor_bookings 
    WHERE vendor_id = X 
    AND user_id = Y 
    AND status = 'Completed'
)
```

---

## 🧪 Testing

### Test Checklist

- [ ] Write review (5 stars)
- [ ] Edit review (change to 4 stars)
- [ ] Delete review
- [ ] Mark review helpful
- [ ] Mark review unhelpful
- [ ] Toggle helpful vote
- [ ] Report review
- [ ] Vendor responds to review
- [ ] Vendor edits response
- [ ] Vendor deletes response
- [ ] Filter by rating
- [ ] Sort by recent
- [ ] Sort by helpful
- [ ] Sort by rating

### Test Scenarios

**Scenario 1: Happy Path**
1. Host books vendor ✅
2. Vendor completes booking ✅
3. Host writes 5-star review ✅
4. Vendor responds professionally ✅
5. Other users mark helpful ✅

**Scenario 2: Negative Review**
1. Host writes 2-star review ✅
2. Vendor responds constructively ✅
3. Host updates to 3 stars ✅
4. Issue resolved ✅

**Scenario 3: Spam Detection**
1. User writes spam review ✅
2. Other users report it ✅
3. Admin reviews report ✅
4. Review removed ✅

---

## 🔒 Security

### Input Validation
- Rating: 1-5 integer only
- Review text: Max 5000 characters
- SQL injection protection
- XSS protection

### Authorization
- Users can only edit own reviews
- Vendors can only respond to their reviews
- One review per user per vendor
- Verified booking checks

---

## 📊 Analytics

### Metrics Tracked
- Average rating per vendor
- Total review count
- Rating distribution
- Helpful vote counts
- Response rate
- Report count

### Insights
- Vendor performance trends
- Customer satisfaction levels
- Review engagement rates
- Common feedback themes

---

## 🐛 Troubleshooting

### Common Issues

**Q: Can't write review**
- Ensure you have a completed booking
- Check if you're logged in
- Verify vendor is approved

**Q: Review not showing**
- Refresh the page
- Check database for review
- Verify vendor_id is correct

**Q: Helpful button not working**
- Check JavaScript console
- Verify you're logged in
- Test with different browser

**Q: Vendor can't respond**
- Verify vendor is logged in
- Check review belongs to vendor
- Ensure response text is not empty

### Debug Commands

```sql
-- Check reviews
SELECT * FROM vendor_reviews WHERE vendor_id = X;

-- Check helpful votes
SELECT * FROM review_helpfulness WHERE review_id = X;

-- Check vendor rating
SELECT AVG(rating), COUNT(*) 
FROM vendor_reviews 
WHERE vendor_id = X;
```

---

## 📚 Documentation

### Files
- `RATING_REVIEW_SYSTEM_GUIDE.md` - Complete technical guide
- `REVIEW_SYSTEM_QUICK_START.md` - Quick start guide
- `REVIEW_IMPLEMENTATION_SUMMARY.md` - Implementation summary
- `README_REVIEW_SYSTEM.md` - This file

### Installation Scripts
- `install_review_system.py` - Python installer
- `install_review_system.bat` - Windows batch installer
- `database_review_enhancement.sql` - Database schema

---

## 🎉 Success!

Your rating and review system is now ready to use!

### What You Can Do Now
✅ Collect customer feedback  
✅ Build vendor reputation  
✅ Help customers make decisions  
✅ Engage with customers  
✅ Track performance  
✅ Improve services  

### Next Steps
1. Test all features thoroughly
2. Customize styling to match your brand
3. Add email notifications (optional)
4. Monitor reviews regularly
5. Encourage customers to leave reviews

---

## 💡 Tips

### For Customers
- Write detailed, honest reviews
- Include specific examples
- Update reviews if experience changes
- Help others by voting helpful

### For Vendors
- Respond to all reviews promptly
- Thank customers for feedback
- Address concerns professionally
- Use feedback to improve

---

## 📞 Support

### Need Help?
- Check documentation files
- Review troubleshooting section
- Test with sample data
- Check browser console for errors

### Report Issues
- Describe the problem
- Include error messages
- Provide steps to reproduce
- Share screenshots if possible

---

## 🏆 Best Practices

### Review Quality
✅ Honest and constructive  
✅ Specific and detailed  
✅ Relevant to service  
✅ Professional tone  

### Vendor Responses
✅ Timely (within 24-48 hours)  
✅ Professional and courteous  
✅ Address concerns directly  
✅ Thank customers for feedback  

---

**Version:** 1.0  
**Status:** ✅ Production Ready  
**Last Updated:** March 2, 2026  

🎊 **Enjoy your new rating and review system!** 🎊
