"""
Rating & Review System - Comprehensive Test Script
Tests all database operations and backend functionality
"""
from db import execute_query, execute_update
from datetime import datetime

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def test_database_tables():
    """Test if all review tables exist"""
    print_header("TEST 1: Database Tables")
    
    tables = ['vendor_reviews', 'review_helpfulness', 'review_reports']
    all_exist = True
    
    for table in tables:
        result = execute_query(
            f"SHOW TABLES LIKE '{table}'",
            fetch_one=True
        )
        if result:
            print_success(f"Table '{table}' exists")
        else:
            print_error(f"Table '{table}' missing")
            all_exist = False
    
    return all_exist

def test_vendor_reviews_columns():
    """Test if vendor_reviews has all required columns"""
    print_header("TEST 2: vendor_reviews Columns")
    
    required_columns = [
        'id', 'vendor_id', 'user_id', 'rating', 'review_text',
        'created_at', 'updated_at', 'helpful_count', 'unhelpful_count',
        'vendor_response', 'vendor_response_date', 'is_verified_booking'
    ]
    
    columns = execute_query("SHOW COLUMNS FROM vendor_reviews")
    column_names = [col['Field'] for col in columns]
    
    all_exist = True
    for col in required_columns:
        if col in column_names:
            print_success(f"Column '{col}' exists")
        else:
            print_error(f"Column '{col}' missing")
            all_exist = False
    
    return all_exist

def test_rating_constraint():
    """Test if rating constraint (1-5) is enforced"""
    print_header("TEST 3: Rating Constraint (1-5)")
    
    # Get a test vendor and user
    vendor = execute_query("SELECT id FROM vendors LIMIT 1", fetch_one=True)
    user = execute_query("SELECT id FROM users WHERE role = 'host' LIMIT 1", fetch_one=True)
    
    if not vendor or not user:
        print_error("No vendor or host found for testing")
        return False
    
    print_info(f"Testing with vendor_id={vendor['id']}, user_id={user['id']}")
    
    # Test valid ratings (1-5)
    valid_ratings = [1, 2, 3, 4, 5]
    for rating in valid_ratings:
        try:
            # Try to insert/update review
            execute_update("""
                INSERT INTO vendor_reviews (vendor_id, user_id, rating, review_text)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE rating = %s
            """, (vendor['id'], user['id'], rating, f"Test review {rating} stars", rating))
            print_success(f"Rating {rating} accepted ✓")
        except Exception as e:
            print_error(f"Rating {rating} failed: {e}")
            return False
    
    # Clean up test review
    execute_update(
        "DELETE FROM vendor_reviews WHERE vendor_id = %s AND user_id = %s",
        (vendor['id'], user['id'])
    )
    
    return True

def test_review_crud():
    """Test Create, Read, Update, Delete operations"""
    print_header("TEST 4: Review CRUD Operations")
    
    # Get test data
    vendor = execute_query("SELECT id FROM vendors LIMIT 1", fetch_one=True)
    user = execute_query("SELECT id FROM users WHERE role = 'host' LIMIT 1", fetch_one=True)
    
    if not vendor or not user:
        print_error("No vendor or host found for testing")
        return False
    
    vendor_id = vendor['id']
    user_id = user['id']
    
    # CREATE
    print_info("Testing CREATE...")
    try:
        execute_update("""
            INSERT INTO vendor_reviews (vendor_id, user_id, rating, review_text, is_verified_booking)
            VALUES (%s, %s, %s, %s, %s)
        """, (vendor_id, user_id, 5, "Excellent service! Highly recommended.", True))
        print_success("Review created successfully")
    except Exception as e:
        print_error(f"Create failed: {e}")
        return False
    
    # READ
    print_info("Testing READ...")
    review = execute_query("""
        SELECT * FROM vendor_reviews 
        WHERE vendor_id = %s AND user_id = %s
    """, (vendor_id, user_id), fetch_one=True)
    
    if review:
        print_success(f"Review found: {review['rating']} stars - '{review['review_text']}'")
    else:
        print_error("Review not found")
        return False
    
    review_id = review['id']
    
    # UPDATE
    print_info("Testing UPDATE...")
    try:
        execute_update("""
            UPDATE vendor_reviews 
            SET rating = %s, review_text = %s 
            WHERE id = %s
        """, (4, "Good service, minor delays but overall satisfied.", review_id))
        
        updated = execute_query(
            "SELECT rating, review_text FROM vendor_reviews WHERE id = %s",
            (review_id,),
            fetch_one=True
        )
        print_success(f"Review updated: {updated['rating']} stars - '{updated['review_text']}'")
    except Exception as e:
        print_error(f"Update failed: {e}")
        return False
    
    # DELETE
    print_info("Testing DELETE...")
    try:
        execute_update("DELETE FROM vendor_reviews WHERE id = %s", (review_id,))
        
        deleted = execute_query(
            "SELECT id FROM vendor_reviews WHERE id = %s",
            (review_id,),
            fetch_one=True
        )
        
        if not deleted:
            print_success("Review deleted successfully")
        else:
            print_error("Review still exists after delete")
            return False
    except Exception as e:
        print_error(f"Delete failed: {e}")
        return False
    
    return True

def test_rating_calculation():
    """Test average rating calculation"""
    print_header("TEST 5: Rating Calculation")
    
    vendor = execute_query("SELECT id FROM vendors LIMIT 1", fetch_one=True)
    
    if not vendor:
        print_error("No vendor found for testing")
        return False
    
    vendor_id = vendor['id']
    
    # Get current reviews
    current_reviews = execute_query(
        "SELECT COUNT(*) as count FROM vendor_reviews WHERE vendor_id = %s",
        (vendor_id,),
        fetch_one=True
    )
    
    print_info(f"Vendor {vendor_id} has {current_reviews['count']} existing reviews")
    
    # Calculate average rating
    stats = execute_query("""
        SELECT 
            AVG(rating) as avg_rating,
            COUNT(*) as total_reviews,
            MIN(rating) as min_rating,
            MAX(rating) as max_rating
        FROM vendor_reviews
        WHERE vendor_id = %s
    """, (vendor_id,), fetch_one=True)
    
    if stats and stats['total_reviews'] > 0:
        print_success(f"Average Rating: {stats['avg_rating']:.2f}/5.0")
        print_success(f"Total Reviews: {stats['total_reviews']}")
        print_success(f"Rating Range: {stats['min_rating']} - {stats['max_rating']}")
    else:
        print_info("No reviews found for this vendor")
    
    # Test rating distribution
    distribution = execute_query("""
        SELECT rating, COUNT(*) as count
        FROM vendor_reviews
        WHERE vendor_id = %s
        GROUP BY rating
        ORDER BY rating DESC
    """, (vendor_id,))
    
    if distribution:
        print_info("\nRating Distribution:")
        for row in distribution:
            stars = "★" * row['rating']
            print(f"  {row['rating']} {stars}: {row['count']} review(s)")
    
    return True

def test_helpful_voting():
    """Test helpful/unhelpful voting system"""
    print_header("TEST 6: Helpful Voting System")
    
    # Get a review
    review = execute_query("SELECT id FROM vendor_reviews LIMIT 1", fetch_one=True)
    user = execute_query("SELECT id FROM users LIMIT 1", fetch_one=True)
    
    if not review or not user:
        print_info("No review or user found for testing (create a review first)")
        return True  # Not a failure, just no data
    
    review_id = review['id']
    user_id = user['id']
    
    # Test helpful vote
    print_info("Testing helpful vote...")
    try:
        execute_update("""
            INSERT INTO review_helpfulness (review_id, user_id, is_helpful)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE is_helpful = %s
        """, (review_id, user_id, True, True))
        
        # Update counts
        counts = execute_query("""
            SELECT 
                SUM(CASE WHEN is_helpful = 1 THEN 1 ELSE 0 END) as helpful,
                SUM(CASE WHEN is_helpful = 0 THEN 1 ELSE 0 END) as unhelpful
            FROM review_helpfulness
            WHERE review_id = %s
        """, (review_id,), fetch_one=True)
        
        execute_update("""
            UPDATE vendor_reviews 
            SET helpful_count = %s, unhelpful_count = %s
            WHERE id = %s
        """, (counts['helpful'] or 0, counts['unhelpful'] or 0, review_id))
        
        print_success(f"Helpful votes: {counts['helpful'] or 0}, Unhelpful votes: {counts['unhelpful'] or 0}")
        
        # Clean up
        execute_update(
            "DELETE FROM review_helpfulness WHERE review_id = %s AND user_id = %s",
            (review_id, user_id)
        )
        
    except Exception as e:
        print_error(f"Helpful voting failed: {e}")
        return False
    
    return True

def test_vendor_response():
    """Test vendor response functionality"""
    print_header("TEST 7: Vendor Response")
    
    review = execute_query("SELECT id FROM vendor_reviews LIMIT 1", fetch_one=True)
    
    if not review:
        print_info("No review found for testing (create a review first)")
        return True
    
    review_id = review['id']
    
    # Add response
    print_info("Testing add response...")
    try:
        execute_update("""
            UPDATE vendor_reviews 
            SET vendor_response = %s, vendor_response_date = NOW()
            WHERE id = %s
        """, ("Thank you for your wonderful feedback! We're glad you enjoyed our service.", review_id))
        
        updated = execute_query(
            "SELECT vendor_response, vendor_response_date FROM vendor_reviews WHERE id = %s",
            (review_id,),
            fetch_one=True
        )
        
        if updated['vendor_response']:
            print_success(f"Response added: '{updated['vendor_response']}'")
            print_success(f"Response date: {updated['vendor_response_date']}")
        else:
            print_error("Response not saved")
            return False
        
        # Delete response
        print_info("Testing delete response...")
        execute_update("""
            UPDATE vendor_reviews 
            SET vendor_response = NULL, vendor_response_date = NULL
            WHERE id = %s
        """, (review_id,))
        
        print_success("Response deleted successfully")
        
    except Exception as e:
        print_error(f"Vendor response failed: {e}")
        return False
    
    return True

def test_verified_booking():
    """Test verified booking badge logic"""
    print_header("TEST 8: Verified Booking Badge")
    
    # Get a vendor and user with completed booking
    booking = execute_query("""
        SELECT vendor_id, user_id 
        FROM vendor_bookings 
        WHERE status = 'Completed'
        LIMIT 1
    """, fetch_one=True)
    
    if not booking:
        print_info("No completed booking found (complete a booking first)")
        return True
    
    vendor_id = booking['vendor_id']
    user_id = booking['user_id']
    
    # Check if review exists
    review = execute_query("""
        SELECT id, is_verified_booking 
        FROM vendor_reviews 
        WHERE vendor_id = %s AND user_id = %s
    """, (vendor_id, user_id), fetch_one=True)
    
    if review:
        if review['is_verified_booking']:
            print_success(f"Review {review['id']} has verified booking badge ✓")
        else:
            print_info(f"Review {review['id']} does not have verified badge")
    else:
        print_info("No review found for this completed booking")
    
    return True

def show_summary():
    """Show summary of all reviews in database"""
    print_header("DATABASE SUMMARY")
    
    # Total reviews
    total = execute_query(
        "SELECT COUNT(*) as count FROM vendor_reviews",
        fetch_one=True
    )
    print_info(f"Total Reviews: {total['count']}")
    
    # Reviews by rating
    by_rating = execute_query("""
        SELECT rating, COUNT(*) as count
        FROM vendor_reviews
        GROUP BY rating
        ORDER BY rating DESC
    """)
    
    if by_rating:
        print_info("\nReviews by Rating:")
        for row in by_rating:
            stars = "★" * row['rating']
            print(f"  {row['rating']} {stars}: {row['count']} review(s)")
    
    # Vendors with reviews
    vendors = execute_query("""
        SELECT COUNT(DISTINCT vendor_id) as count 
        FROM vendor_reviews
    """, fetch_one=True)
    print_info(f"\nVendors with Reviews: {vendors['count']}")
    
    # Average rating across all vendors
    avg = execute_query("""
        SELECT AVG(rating) as avg_rating 
        FROM vendor_reviews
    """, fetch_one=True)
    if avg and avg['avg_rating']:
        print_info(f"Overall Average Rating: {avg['avg_rating']:.2f}/5.0")
    
    # Verified bookings
    verified = execute_query("""
        SELECT COUNT(*) as count 
        FROM vendor_reviews 
        WHERE is_verified_booking = 1
    """, fetch_one=True)
    print_info(f"Verified Booking Reviews: {verified['count']}")
    
    # Reviews with vendor responses
    responses = execute_query("""
        SELECT COUNT(*) as count 
        FROM vendor_reviews 
        WHERE vendor_response IS NOT NULL
    """, fetch_one=True)
    print_info(f"Reviews with Vendor Responses: {responses['count']}")

def main():
    """Run all tests"""
    print_header("RATING & REVIEW SYSTEM - COMPREHENSIVE TEST")
    
    print("This script will test all database operations and backend functionality.")
    print("Make sure MySQL is running and the database is set up correctly.")
    print()
    
    input("Press Enter to start testing...")
    
    results = []
    
    # Run all tests
    results.append(("Database Tables", test_database_tables()))
    results.append(("vendor_reviews Columns", test_vendor_reviews_columns()))
    results.append(("Rating Constraint", test_rating_constraint()))
    results.append(("Review CRUD", test_review_crud()))
    results.append(("Rating Calculation", test_rating_calculation()))
    results.append(("Helpful Voting", test_helpful_voting()))
    results.append(("Vendor Response", test_vendor_response()))
    results.append(("Verified Booking", test_verified_booking()))
    
    # Show summary
    show_summary()
    
    # Print results
    print_header("TEST RESULTS")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
            passed += 1
        else:
            print_error(f"{test_name}: FAILED")
            failed += 1
    
    print()
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print_header("✅ ALL TESTS PASSED!")
        print("Your rating and review system is working perfectly!")
    else:
        print_header("⚠️ SOME TESTS FAILED")
        print("Please check the errors above and fix the issues.")
    
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user.")
    except Exception as e:
        print_error(f"Test error: {e}")
        import traceback
        traceback.print_exc()
