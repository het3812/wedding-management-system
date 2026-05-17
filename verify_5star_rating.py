"""
5-Star Rating System Verification
Quick test to verify all ratings (1-5 stars) work correctly
"""
from db import execute_query, execute_update

def print_header(text):
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60 + "\n")

def verify_rating_system():
    """Verify that all 5 star ratings work correctly"""
    print_header("5-STAR RATING SYSTEM VERIFICATION")
    
    # Get test vendor and user
    vendor = execute_query("SELECT id, business_name FROM vendors LIMIT 1", fetch_one=True)
    user = execute_query("SELECT id, name FROM users WHERE role = 'host' LIMIT 1", fetch_one=True)
    
    if not vendor:
        print("❌ No vendor found. Please create a vendor first.")
        return False
    
    if not user:
        print("❌ No host user found. Please create a host user first.")
        return False
    
    print(f"ℹ️  Testing with:")
    print(f"   Vendor: {vendor['business_name']} (ID: {vendor['id']})")
    print(f"   User: {user['name']} (ID: {user['id']})")
    print()
    
    # Test each rating from 1 to 5
    print("Testing all star ratings (1-5)...")
    print("-" * 60)
    
    for rating in range(1, 6):
        try:
            # Insert or update review with current rating
            execute_update("""
                INSERT INTO vendor_reviews (vendor_id, user_id, rating, review_text, is_verified_booking)
                VALUES (%s, %s, %s, %s, TRUE)
                ON DUPLICATE KEY UPDATE rating = %s, review_text = %s
            """, (
                vendor['id'], 
                user['id'], 
                rating, 
                f"Test review with {rating} star{'s' if rating != 1 else ''}",
                rating,
                f"Test review with {rating} star{'s' if rating != 1 else ''}"
            ))
            
            # Verify the rating was saved
            saved_review = execute_query("""
                SELECT rating, review_text FROM vendor_reviews 
                WHERE vendor_id = %s AND user_id = %s
            """, (vendor['id'], user['id']), fetch_one=True)
            
            if saved_review and saved_review['rating'] == rating:
                stars = "★" * rating + "☆" * (5 - rating)
                print(f"✅ {rating} Star: {stars} - Saved successfully")
            else:
                print(f"❌ {rating} Star: Failed to save")
                return False
                
        except Exception as e:
            print(f"❌ {rating} Star: Error - {e}")
            return False
    
    print("-" * 60)
    
    # Test rating calculation
    print("\nTesting rating calculation...")
    
    # Update vendor's average rating
    stats = execute_query("""
        SELECT AVG(rating) as avg_rating, COUNT(*) as total
        FROM vendor_reviews
        WHERE vendor_id = %s
    """, (vendor['id'],), fetch_one=True)
    
    execute_update("""
        UPDATE vendors 
        SET average_rating = %s, total_reviews = %s
        WHERE id = %s
    """, (stats['avg_rating'], stats['total'], vendor['id']))
    
    # Verify vendor rating
    vendor_rating = execute_query("""
        SELECT average_rating, total_reviews 
        FROM vendors 
        WHERE id = %s
    """, (vendor['id'],), fetch_one=True)
    
    print(f"✅ Average Rating: {vendor_rating['average_rating']:.2f}/5.0")
    print(f"✅ Total Reviews: {vendor_rating['total_reviews']}")
    
    # Test rating distribution
    print("\nTesting rating distribution...")
    distribution = execute_query("""
        SELECT rating, COUNT(*) as count
        FROM vendor_reviews
        WHERE vendor_id = %s
        GROUP BY rating
        ORDER BY rating DESC
    """, (vendor['id'],))
    
    if distribution:
        for row in distribution:
            stars = "★" * row['rating']
            bar = "█" * (row['count'] * 5)
            print(f"{row['rating']} {stars}: {bar} {row['count']}")
    
    # Clean up test review
    print("\nCleaning up test data...")
    execute_update("""
        DELETE FROM vendor_reviews 
        WHERE vendor_id = %s AND user_id = %s AND review_text LIKE 'Test review%'
    """, (vendor['id'], user['id']))
    
    # Reset vendor rating
    stats = execute_query("""
        SELECT AVG(rating) as avg_rating, COUNT(*) as total
        FROM vendor_reviews
        WHERE vendor_id = %s
    """, (vendor['id'],), fetch_one=True)
    
    execute_update("""
        UPDATE vendors 
        SET average_rating = %s, total_reviews = %s
        WHERE id = %s
    """, (stats['avg_rating'] or 0, stats['total'], vendor['id']))
    
    print("✅ Test data cleaned up")
    
    print_header("✅ 5-STAR RATING SYSTEM VERIFIED!")
    print("All ratings (1-5 stars) are working correctly.")
    print("\nYou can now:")
    print("1. Login as host")
    print("2. Book a vendor")
    print("3. Vendor marks booking as completed")
    print("4. Host writes review with any rating (1-5 stars)")
    print("5. Rating will be saved and displayed correctly")
    print()
    
    return True

def show_current_reviews():
    """Show all current reviews in the database"""
    print_header("CURRENT REVIEWS IN DATABASE")
    
    reviews = execute_query("""
        SELECT vr.id, vr.rating, vr.review_text, vr.created_at,
               v.business_name as vendor_name,
               u.name as reviewer_name,
               vr.is_verified_booking
        FROM vendor_reviews vr
        JOIN vendors v ON vr.vendor_id = v.id
        JOIN users u ON vr.user_id = u.id
        ORDER BY vr.created_at DESC
        LIMIT 10
    """)
    
    if not reviews:
        print("No reviews found in database.")
        print("\nTo create a review:")
        print("1. Login as host")
        print("2. Book a vendor")
        print("3. Vendor marks booking as completed")
        print("4. Host writes review")
        return
    
    print(f"Showing {len(reviews)} most recent reviews:\n")
    
    for review in reviews:
        stars = "★" * review['rating'] + "☆" * (5 - review['rating'])
        verified = "✓ Verified" if review['is_verified_booking'] else ""
        
        print(f"Review #{review['id']}")
        print(f"  Vendor: {review['vendor_name']}")
        print(f"  Reviewer: {review['reviewer_name']} {verified}")
        print(f"  Rating: {stars} ({review['rating']}/5)")
        print(f"  Review: {review['review_text'][:60]}...")
        print(f"  Date: {review['created_at']}")
        print()

if __name__ == '__main__':
    try:
        print_header("RATING & REVIEW SYSTEM - 5-STAR VERIFICATION")
        print("This script verifies that all 5 star ratings work correctly.")
        print()
        
        # Show current reviews first
        show_current_reviews()
        
        # Ask user if they want to run verification test
        response = input("Run 5-star rating verification test? (y/n): ")
        
        if response.lower() == 'y':
            verify_rating_system()
        else:
            print("\nTest cancelled. Your existing reviews are shown above.")
        
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
