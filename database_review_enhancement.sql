-- ============================================
-- RATING & REVIEW SYSTEM ENHANCEMENT
-- Run this to enhance the existing review system
-- ============================================

USE wedding_db;

-- Add new columns to vendor_reviews table
ALTER TABLE vendor_reviews 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS helpful_count INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS unhelpful_count INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS vendor_response TEXT,
ADD COLUMN IF NOT EXISTS vendor_response_date TIMESTAMP NULL,
ADD COLUMN IF NOT EXISTS is_verified_booking BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS images TEXT COMMENT 'JSON array of image paths';

-- Create review helpfulness tracking table
CREATE TABLE IF NOT EXISTS review_helpfulness (
    id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    user_id INT NOT NULL,
    is_helpful BOOLEAN NOT NULL COMMENT '1 = helpful, 0 = unhelpful',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES vendor_reviews(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_review (user_id, review_id)
);

-- Create review report table (for flagging inappropriate reviews)
CREATE TABLE IF NOT EXISTS review_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    reporter_user_id INT NOT NULL,
    reason ENUM('Spam', 'Offensive', 'Fake', 'Irrelevant', 'Other') NOT NULL,
    description TEXT,
    status ENUM('Pending', 'Reviewed', 'Resolved', 'Dismissed') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES vendor_reviews(id) ON DELETE CASCADE,
    FOREIGN KEY (reporter_user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_review_rating ON vendor_reviews(rating);
CREATE INDEX IF NOT EXISTS idx_review_created ON vendor_reviews(created_at);
CREATE INDEX IF NOT EXISTS idx_review_helpful ON vendor_reviews(helpful_count);
CREATE INDEX IF NOT EXISTS idx_helpfulness_review ON review_helpfulness(review_id);
CREATE INDEX IF NOT EXISTS idx_report_status ON review_reports(status);

-- Update existing reviews to mark verified bookings
UPDATE vendor_reviews vr
SET is_verified_booking = TRUE
WHERE EXISTS (
    SELECT 1 FROM vendor_bookings vb
    WHERE vb.vendor_id = vr.vendor_id 
    AND vb.user_id = vr.user_id 
    AND vb.status = 'Completed'
);

-- ============================================
-- Sample data for testing (optional)
-- ============================================

-- Uncomment below to add sample reviews for testing
/*
-- Get first vendor and host
SET @vendor_id = (SELECT id FROM vendors LIMIT 1);
SET @host_id = (SELECT id FROM users WHERE role = 'host' LIMIT 1);

-- Add sample reviews if vendor and host exist
INSERT IGNORE INTO vendor_reviews (vendor_id, user_id, rating, review_text, is_verified_booking)
VALUES 
(@vendor_id, @host_id, 5, 'Excellent service! Very professional and delivered exactly what we wanted for our wedding.', TRUE),
(@vendor_id, @host_id, 4, 'Good experience overall. Minor delays but quality was great.', TRUE);
*/

-- ============================================
-- Verification Queries
-- ============================================

-- Check if enhancement was successful
SELECT 'vendor_reviews table structure:' as info;
DESCRIBE vendor_reviews;

SELECT 'review_helpfulness table structure:' as info;
DESCRIBE review_helpfulness;

SELECT 'review_reports table structure:' as info;
DESCRIBE review_reports;

SELECT CONCAT('Total reviews: ', COUNT(*)) as info FROM vendor_reviews;
SELECT CONCAT('Total vendors with reviews: ', COUNT(DISTINCT vendor_id)) as info FROM vendor_reviews;

-- ============================================
-- ENHANCEMENT COMPLETE
-- ============================================
