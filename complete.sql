-- ============================================
-- QUICK FIX: Add guest_count column
-- Copy and paste this into phpMyAdmin SQL tab
-- ============================================

USE wedding_db;

-- Add guest_count column to guests table
ALTER TABLE guests 
ADD COLUMN guest_count INT DEFAULT 1 AFTER rsvp_submitted_at;

-- Set default value for existing records
UPDATE guests 
SET guest_count = CASE 
    WHEN plus_one = TRUE THEN 2 
    ELSE 1 
END
WHERE guest_count IS NULL OR guest_count = 0;

-- Verify the column was added
SELECT * FROM guests LIMIT 1;


-- ============================================
-- Wedding Management System - MySQL Schema
-- Run this in phpMyAdmin (XAMPP) for fresh install
-- For existing DB, use database_migration.sql instead
-- ============================================

CREATE DATABASE IF NOT EXISTS wedding_db;
USE wedding_db;

-- Users: admin, host, vendor
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'host', 'vendor') DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invitations
CREATE TABLE IF NOT EXISTS invitations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    bride_name VARCHAR(100) NOT NULL,
    groom_name VARCHAR(100) NOT NULL,
    wedding_date DATE NOT NULL,
    venue VARCHAR(255) NOT NULL,
    message TEXT,
    invite_token VARCHAR(64) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Wedding images (with album support)
CREATE TABLE IF NOT EXISTS wedding_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invitation_id INT NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    album_name VARCHAR(100) DEFAULT 'Main',
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invitation_id) REFERENCES invitations(id) ON DELETE CASCADE
);

-- Guests (per invitation)
CREATE TABLE IF NOT EXISTS guests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invitation_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(20),
    category ENUM('Family', 'Friend', 'VIP') DEFAULT 'Friend',
    rsvp_status ENUM('Pending', 'Confirmed', 'Declined') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invitation_id) REFERENCES invitations(id) ON DELETE CASCADE
);

-- Wedding events (Haldi, Mehndi, Wedding, Reception)
CREATE TABLE IF NOT EXISTS wedding_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invitation_id INT NOT NULL,
    event_name VARCHAR(100) NOT NULL,
    event_date DATE NOT NULL,
    event_time TIME,
    venue VARCHAR(255) NOT NULL,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invitation_id) REFERENCES invitations(id) ON DELETE CASCADE
);

-- Vendors
CREATE TABLE IF NOT EXISTS vendors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    business_name VARCHAR(150) NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    contact_email VARCHAR(150) NOT NULL,
    contact_phone VARCHAR(20),
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Vendor services
CREATE TABLE IF NOT EXISTS vendor_services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(12,2),
    image_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
);

CREATE INDEX idx_invite_token ON invitations(invite_token);


-- ============================================
-- COMMISSION TRACKING SYSTEM (2.5%)
-- Admin commission tracking for vendor transactions
-- ============================================

USE wedding_db;

-- Add commission tracking columns to payment_transactions
ALTER TABLE payment_transactions
ADD COLUMN IF NOT EXISTS commission_rate DECIMAL(5, 2) DEFAULT 2.50 COMMENT 'Commission percentage (default 2.5%)',
ADD COLUMN IF NOT EXISTS commission_amount DECIMAL(12, 2) COMMENT 'Calculated commission amount',
ADD COLUMN IF NOT EXISTS commission_status ENUM('Pending', 'Collected', 'Waived') DEFAULT 'Pending',
ADD COLUMN IF NOT EXISTS commission_collected_date TIMESTAMP NULL,
ADD COLUMN IF NOT EXISTS commission_notes TEXT;

-- Create commission_records table for detailed tracking
CREATE TABLE IF NOT EXISTS commission_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    booking_id INT NOT NULL,
    vendor_id INT NOT NULL,
    transaction_amount DECIMAL(12, 2) NOT NULL,
    commission_rate DECIMAL(5, 2) NOT NULL DEFAULT 2.50,
    commission_amount DECIMAL(12, 2) NOT NULL,
    status ENUM('Pending', 'Collected', 'Waived') DEFAULT 'Pending',
    collected_date TIMESTAMP NULL,
    collected_by INT COMMENT 'Admin user_id who collected',
    payment_method ENUM('Cash', 'Bank Transfer', 'UPI', 'Other') NULL,
    reference_number VARCHAR(100) COMMENT 'Payment reference for commission collection',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES payment_transactions(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES vendor_bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE,
    FOREIGN KEY (collected_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Create commission_summary table for monthly aggregates
CREATE TABLE IF NOT EXISTS commission_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    month INT NOT NULL COMMENT 'Month (1-12)',
    year INT NOT NULL COMMENT 'Year',
    total_transactions DECIMAL(12, 2) DEFAULT 0,
    total_commission DECIMAL(12, 2) DEFAULT 0,
    collected_commission DECIMAL(12, 2) DEFAULT 0,
    pending_commission DECIMAL(12, 2) DEFAULT 0,
    transaction_count INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_vendor_month (vendor_id, month, year),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_commission_status ON commission_records(status);
CREATE INDEX IF NOT EXISTS idx_commission_vendor ON commission_records(vendor_id);
CREATE INDEX IF NOT EXISTS idx_commission_date ON commission_records(created_at);
CREATE INDEX IF NOT EXISTS idx_commission_collected ON commission_records(collected_date);
CREATE INDEX IF NOT EXISTS idx_summary_vendor_date ON commission_summary(vendor_id, year, month);

-- Trigger to automatically calculate commission when transaction is verified
DELIMITER //

CREATE TRIGGER IF NOT EXISTS calculate_commission_after_verification
BEFORE UPDATE ON payment_transactions
FOR EACH ROW
BEGIN
    -- Only calculate commission when status changes to 'Verified' and commission not already calculated
    IF NEW.status = 'Verified' AND OLD.status != 'Verified' AND NEW.commission_amount IS NULL THEN
        -- Set default commission rate if not set
        IF NEW.commission_rate IS NULL THEN
            SET NEW.commission_rate = 2.50;
        END IF;
        
        -- Calculate commission amount (2.5% by default)
        SET NEW.commission_amount = NEW.amount * (NEW.commission_rate / 100);
        SET NEW.commission_status = 'Pending';
    END IF;
END//

DELIMITER ;

-- Trigger to create commission record after transaction is verified
DELIMITER //

CREATE TRIGGER IF NOT EXISTS create_commission_record_after_verification
AFTER UPDATE ON payment_transactions
FOR EACH ROW
BEGIN
    -- Only create commission record when status changes to 'Verified' and record doesn't exist
    IF NEW.status = 'Verified' AND OLD.status != 'Verified' THEN
        -- Check if commission record already exists
        IF NOT EXISTS (SELECT 1 FROM commission_records WHERE transaction_id = NEW.id) THEN
            -- Insert into commission_records
            INSERT INTO commission_records (
                transaction_id, booking_id, vendor_id, 
                transaction_amount, commission_rate, commission_amount,
                status
            ) VALUES (
                NEW.id, NEW.booking_id, NEW.vendor_id,
                NEW.amount, NEW.commission_rate, NEW.commission_amount,
                'Pending'
            );
        END IF;
    END IF;
END//

DELIMITER ;

-- Stored procedure to update commission summary
DELIMITER //

CREATE PROCEDURE IF NOT EXISTS update_commission_summary(
    IN p_vendor_id INT,
    IN p_month INT,
    IN p_year INT
)
BEGIN
    -- Calculate totals for the vendor in the given month/year
    INSERT INTO commission_summary (
        vendor_id, month, year,
        total_transactions, total_commission,
        collected_commission, pending_commission,
        transaction_count
    )
    SELECT 
        p_vendor_id,
        p_month,
        p_year,
        COALESCE(SUM(transaction_amount), 0),
        COALESCE(SUM(commission_amount), 0),
        COALESCE(SUM(CASE WHEN status = 'Collected' THEN commission_amount ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN status = 'Pending' THEN commission_amount ELSE 0 END), 0),
        COUNT(*)
    FROM commission_records
    WHERE vendor_id = p_vendor_id
        AND MONTH(created_at) = p_month
        AND YEAR(created_at) = p_year
    ON DUPLICATE KEY UPDATE
        total_transactions = VALUES(total_transactions),
        total_commission = VALUES(total_commission),
        collected_commission = VALUES(collected_commission),
        pending_commission = VALUES(pending_commission),
        transaction_count = VALUES(transaction_count);
END//

DELIMITER ;

-- ============================================
-- Sample Data for Testing (Optional)
-- ============================================

-- Uncomment to add sample commission records for testing
/*
-- Update existing verified transactions with commission
UPDATE payment_transactions 
SET commission_rate = 2.50,
    commission_amount = amount * 0.025,
    commission_status = 'Pending'
WHERE status = 'Verified' AND commission_amount IS NULL;

-- Insert commission records for existing verified transactions
INSERT INTO commission_records (
    transaction_id, booking_id, vendor_id,
    transaction_amount, commission_rate, commission_amount,
    status
)
SELECT 
    pt.id, pt.booking_id, pt.vendor_id,
    pt.amount, 2.50, pt.amount * 0.025,
    'Pending'
FROM payment_transactions pt
WHERE pt.status = 'Verified' 
    AND NOT EXISTS (
        SELECT 1 FROM commission_records cr 
        WHERE cr.transaction_id = pt.id
    );
*/

-- ============================================
-- Verification Queries
-- ============================================

-- Check commission columns in payment_transactions
SELECT 'payment_transactions - commission columns:' as info;
DESCRIBE payment_transactions;

-- Check commission_records table
SELECT 'commission_records table structure:' as info;
DESCRIBE commission_records;

-- Check commission_summary table
SELECT 'commission_summary table structure:' as info;
DESCRIBE commission_summary;

-- Count commission records
SELECT CONCAT('Total commission records: ', COUNT(*)) as info 
FROM commission_records;

-- Total pending commission
SELECT CONCAT('Total pending commission: ₹', COALESCE(SUM(commission_amount), 0)) as info 
FROM commission_records 
WHERE status = 'Pending';

-- Total collected commission
SELECT CONCAT('Total collected commission: ₹', COALESCE(SUM(commission_amount), 0)) as info 
FROM commission_records 
WHERE status = 'Collected';

-- ============================================
-- COMMISSION TRACKING SYSTEM COMPLETE
-- ============================================




-- ============================================
-- Guest Count Migration
-- Replace plus_one with guest_count field
-- Run this in phpMyAdmin to update the guests table
-- ============================================

USE wedding_db;

-- Add guest_count column to guests table
ALTER TABLE guests 
ADD COLUMN guest_count INT DEFAULT 1 AFTER rsvp_submitted_at;

-- Optional: Migrate existing plus_one data to guest_count
-- If plus_one is TRUE, set guest_count to 2, otherwise 1
UPDATE guests 
SET guest_count = CASE 
    WHEN plus_one = TRUE THEN 2 
    ELSE 1 
END
WHERE guest_count IS NULL OR guest_count = 0;

-- Optional: You can keep plus_one and plus_one_name columns for backward compatibility
-- Or remove them if you want to clean up:
-- ALTER TABLE guests DROP COLUMN plus_one;
-- ALTER TABLE guests DROP COLUMN plus_one_name;

-- Note: Keeping the old columns won't cause any issues
-- The new system will use guest_count instead




-- Add profile/cover image to invitations table
-- This allows hosts to set a featured couple photo for their invitation

ALTER TABLE invitations 
ADD COLUMN profile_image VARCHAR(255) DEFAULT NULL COMMENT 'Featured couple/profile photo for invitation card';

-- Note: If you get "Duplicate column" error, the column already exists. You can skip this migration.



-- ============================================
-- Migration: Add Vendor, Guest, Events features
-- Run this if you already have wedding_db from previous setup
-- ============================================
USE wedding_db;

-- Add 'host' role, update enum: admin, host, vendor
-- Step 1: Add host to enum
ALTER TABLE users MODIFY COLUMN role ENUM('admin', 'guest', 'vendor', 'host') DEFAULT 'admin';
-- Step 2: Convert guest to host
UPDATE users SET role = 'host' WHERE role = 'guest';
-- Step 3: Remove guest from enum
ALTER TABLE users MODIFY COLUMN role ENUM('admin', 'host', 'vendor') DEFAULT 'admin';

-- Guests table: per invitation, with category and RSVP
CREATE TABLE IF NOT EXISTS guests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invitation_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(20),
    category ENUM('Family', 'Friend', 'VIP') DEFAULT 'Friend',
    rsvp_status ENUM('Pending', 'Confirmed', 'Declined') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invitation_id) REFERENCES invitations(id) ON DELETE CASCADE
);

-- Wedding events: per invitation (Haldi, Mehndi, Wedding, Reception)
CREATE TABLE IF NOT EXISTS wedding_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invitation_id INT NOT NULL,
    event_name VARCHAR(100) NOT NULL,
    event_date DATE NOT NULL,
    event_time TIME,
    venue VARCHAR(255) NOT NULL,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invitation_id) REFERENCES invitations(id) ON DELETE CASCADE
);

-- Vendors: linked to user account
CREATE TABLE IF NOT EXISTS vendors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    business_name VARCHAR(150) NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    contact_email VARCHAR(150) NOT NULL,
    contact_phone VARCHAR(20),
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Vendor services: title, description, price, image
CREATE TABLE IF NOT EXISTS vendor_services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(12,2),
    image_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
);

-- Add album_name to wedding_images for album-wise gallery view
-- (Skip if you get "duplicate column" error)
ALTER TABLE wedding_images ADD COLUMN album_name VARCHAR(100) DEFAULT 'Main';



-- ============================================
-- PAYMENT SYSTEM WITH UPI QR CODE SUPPORT
-- Run this to add payment functionality
-- ============================================

USE wedding_db;

-- Add payment-related columns to vendors table
ALTER TABLE vendors
ADD COLUMN IF NOT EXISTS upi_id VARCHAR(100) COMMENT 'UPI ID for payments',
ADD COLUMN IF NOT EXISTS upi_qr_code VARCHAR(255) COMMENT 'Path to UPI QR code image',
ADD COLUMN IF NOT EXISTS bank_account_name VARCHAR(150),
ADD COLUMN IF NOT EXISTS bank_account_number VARCHAR(50),
ADD COLUMN IF NOT EXISTS bank_ifsc_code VARCHAR(20),
ADD COLUMN IF NOT EXISTS bank_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS accepts_online_payment BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS payment_terms TEXT COMMENT 'Payment terms and conditions';

-- Add payment-related columns to vendor_bookings table
ALTER TABLE vendor_bookings
ADD COLUMN IF NOT EXISTS advance_amount DECIMAL(12, 2) COMMENT 'Advance payment amount',
ADD COLUMN IF NOT EXISTS advance_paid BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS advance_paid_date TIMESTAMP NULL,
ADD COLUMN IF NOT EXISTS advance_payment_proof VARCHAR(255) COMMENT 'Path to payment proof image',
ADD COLUMN IF NOT EXISTS final_amount DECIMAL(12, 2) COMMENT 'Final payment amount',
ADD COLUMN IF NOT EXISTS final_paid BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS final_paid_date TIMESTAMP NULL,
ADD COLUMN IF NOT EXISTS final_payment_proof VARCHAR(255) COMMENT 'Path to payment proof image',
ADD COLUMN IF NOT EXISTS payment_status ENUM('Pending', 'Advance Paid', 'Fully Paid', 'Refunded') DEFAULT 'Pending',
ADD COLUMN IF NOT EXISTS payment_method ENUM('UPI', 'Bank Transfer', 'Cash', 'Card', 'Other') DEFAULT 'UPI',
ADD COLUMN IF NOT EXISTS payment_notes TEXT COMMENT 'Payment-related notes';

-- Create payment transactions table for detailed tracking
CREATE TABLE IF NOT EXISTS payment_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    vendor_id INT NOT NULL,
    user_id INT NOT NULL,
    transaction_type ENUM('Advance', 'Final', 'Refund') NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method ENUM('UPI', 'Bank Transfer', 'Cash', 'Card', 'Other') NOT NULL,
    payment_proof VARCHAR(255) COMMENT 'Path to payment proof image',
    transaction_id VARCHAR(100) COMMENT 'UPI/Bank transaction ID',
    upi_ref_number VARCHAR(100) COMMENT 'UPI reference number',
    status ENUM('Pending', 'Verified', 'Rejected') DEFAULT 'Pending',
    verified_by INT COMMENT 'Vendor user_id who verified',
    verified_at TIMESTAMP NULL,
    rejection_reason TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES vendor_bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create payment reminders table
CREATE TABLE IF NOT EXISTS payment_reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    reminder_type ENUM('Advance', 'Final') NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_by ENUM('System', 'Vendor') DEFAULT 'System',
    FOREIGN KEY (booking_id) REFERENCES vendor_bookings(id) ON DELETE CASCADE
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_booking_payment_status ON vendor_bookings(payment_status);
CREATE INDEX IF NOT EXISTS idx_transaction_booking ON payment_transactions(booking_id);
CREATE INDEX IF NOT EXISTS idx_transaction_status ON payment_transactions(status);
CREATE INDEX IF NOT EXISTS idx_transaction_created ON payment_transactions(created_at);

-- ============================================
-- Sample UPI IDs for testing (optional)
-- ============================================

-- Uncomment to add sample UPI data for testing
/*
UPDATE vendors 
SET upi_id = CONCAT(LOWER(REPLACE(business_name, ' ', '')), '@paytm'),
    accepts_online_payment = TRUE,
    payment_terms = 'Advance payment: 30% of total amount. Final payment: Before event date.'
WHERE upi_id IS NULL
LIMIT 5;
*/

-- ============================================
-- Verification Queries
-- ============================================

-- Check vendors table structure
SELECT 'vendors table - payment columns:' as info;
DESCRIBE vendors;

-- Check vendor_bookings table structure
SELECT 'vendor_bookings table - payment columns:' as info;
DESCRIBE vendor_bookings;

-- Check payment_transactions table
SELECT 'payment_transactions table structure:' as info;
DESCRIBE payment_transactions;

-- Count vendors with UPI setup
SELECT CONCAT('Vendors with UPI ID: ', COUNT(*)) as info 
FROM vendors 
WHERE upi_id IS NOT NULL;

-- Count bookings with payments
SELECT CONCAT('Bookings with payments: ', COUNT(*)) as info 
FROM vendor_bookings 
WHERE payment_status != 'Pending';

-- ============================================
-- PAYMENT SYSTEM ENHANCEMENT COMPLETE
-- ============================================




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



    -- ============================================
    -- RSVP System Migration
    -- Add RSVP functionality to existing wedding_db
    -- Run this in phpMyAdmin after database.sql
    -- ============================================

    USE wedding_db;

    -- Add RSVP token to guests table
    ALTER TABLE guests 
    ADD COLUMN rsvp_token VARCHAR(64) UNIQUE AFTER phone,
    ADD COLUMN rsvp_response TEXT AFTER rsvp_status,
    ADD COLUMN rsvp_submitted_at TIMESTAMP NULL AFTER rsvp_response,
    ADD COLUMN plus_one BOOLEAN DEFAULT FALSE AFTER category,
    ADD COLUMN plus_one_name VARCHAR(100) AFTER plus_one;

    -- Create index for faster token lookups
    CREATE INDEX idx_rsvp_token ON guests(rsvp_token);

    -- Update existing guests with unique tokens (optional - for existing data)
    -- You can skip this if starting fresh
    UPDATE guests SET rsvp_token = CONCAT(MD5(CONCAT(id, email, RAND())), SUBSTRING(MD5(RAND()), 1, 8)) WHERE rsvp_token IS NULL;




-- ============================================
-- Vendor Management System Enhancement
-- Run this in phpMyAdmin after database.sql
-- ============================================

USE wedding_db;

-- ============================================
-- 1. Enhanced Vendors Table
-- ============================================
ALTER TABLE vendors 
ADD COLUMN website_url VARCHAR(255) AFTER contact_phone,
ADD COLUMN instagram_url VARCHAR(255) AFTER website_url,
ADD COLUMN city VARCHAR(100) AFTER instagram_url,
ADD COLUMN state VARCHAR(100) AFTER city,
ADD COLUMN area VARCHAR(100) AFTER state,
ADD COLUMN latitude DECIMAL(10, 8) AFTER area,
ADD COLUMN longitude DECIMAL(11, 8) AFTER latitude,
ADD COLUMN description TEXT AFTER longitude,
ADD COLUMN average_rating DECIMAL(3, 2) DEFAULT 0.00 AFTER description,
ADD COLUMN total_reviews INT DEFAULT 0 AFTER average_rating,
ADD COLUMN category VARCHAR(100) AFTER service_type,
ADD COLUMN is_blocked BOOLEAN DEFAULT FALSE AFTER is_approved,
ADD COLUMN block_reason VARCHAR(255) AFTER is_blocked,
ADD COLUMN last_order_date TIMESTAMP NULL AFTER block_reason,
ADD COLUMN block_count INT DEFAULT 0 AFTER last_order_date,
ADD COLUMN reactivation_fee DECIMAL(10, 2) DEFAULT 4989.00 AFTER block_count,
ADD COLUMN validity_until TIMESTAMP NULL AFTER reactivation_fee,
ADD COLUMN orders_in_validity INT DEFAULT 0 AFTER validity_until;

-- ============================================
-- 2. Vendor Gallery (Multiple Photos)
-- ============================================
CREATE TABLE IF NOT EXISTS vendor_gallery (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    caption VARCHAR(255),
    display_order INT DEFAULT 0,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
);

-- ============================================
-- 3. Vendor Reviews & Ratings
-- ============================================
CREATE TABLE IF NOT EXISTS vendor_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_vendor_review (user_id, vendor_id)
);

-- ============================================
-- 4. Vendor Bookings/Orders
-- ============================================
CREATE TABLE IF NOT EXISTS vendor_bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    user_id INT NOT NULL,
    service_id INT NULL,
    booking_date DATE NOT NULL,
    event_date DATE,
    status ENUM('Pending', 'Confirmed', 'Completed', 'Cancelled') DEFAULT 'Pending',
    total_amount DECIMAL(12, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES vendor_services(id) ON DELETE SET NULL
);

-- ============================================
-- 5. Chat System
-- ============================================
CREATE TABLE IF NOT EXISTS vendor_chats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    user_id INT NOT NULL,
    last_message TEXT,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unread_vendor INT DEFAULT 0,
    unread_user INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_vendor_user_chat (vendor_id, user_id)
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_id INT NOT NULL,
    sender_id INT NOT NULL,
    sender_type ENUM('vendor', 'user') NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES vendor_chats(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- 6. Vendor Block History
-- ============================================
CREATE TABLE IF NOT EXISTS vendor_block_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    block_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unblock_date TIMESTAMP NULL,
    reason VARCHAR(255),
    reactivation_fee DECIMAL(10, 2),
    payment_status ENUM('Pending', 'Paid', 'Waived') DEFAULT 'Pending',
    payment_date TIMESTAMP NULL,
    block_number INT DEFAULT 1,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
);

-- ============================================
-- 7. Indexes for Performance
-- ============================================
CREATE INDEX idx_vendor_category ON vendors(category);
CREATE INDEX idx_vendor_city ON vendors(city);
CREATE INDEX idx_vendor_rating ON vendors(average_rating);
CREATE INDEX idx_vendor_blocked ON vendors(is_blocked);
CREATE INDEX idx_vendor_approved ON vendors(is_approved);
CREATE INDEX idx_booking_vendor ON vendor_bookings(vendor_id);
CREATE INDEX idx_booking_status ON vendor_bookings(status);
CREATE INDEX idx_chat_vendor_user ON vendor_chats(vendor_id, user_id);
CREATE INDEX idx_message_chat ON chat_messages(chat_id);
CREATE INDEX idx_review_vendor ON vendor_reviews(vendor_id);

-- ============================================
-- 8. Update Existing Data (Optional)
-- ============================================
-- Set default category based on service_type
UPDATE vendors SET category = service_type WHERE category IS NULL;

-- Set default reactivation fee
UPDATE vendors SET reactivation_fee = 4989.00 WHERE reactivation_fee IS NULL;

-- ============================================
-- 9. Vendor Categories Reference
-- ============================================
-- Categories to use:
-- 'Photographer', 'Clothes/Boutique', 'Party Plot', 'Car Booking', 
-- 'Makeup Artist', 'Mehendi Artist', 'Pandit', 'Catering', 'Decoration'



-- ============================================
-- Fix vendor_bookings foreign key constraint
-- Run this to fix the service_id NULL issue
-- ============================================

USE wedding_db;

-- Drop the existing foreign key constraint
ALTER TABLE vendor_bookings 
DROP FOREIGN KEY vendor_bookings_ibfk_3;

-- Recreate the foreign key constraint with proper NULL handling
ALTER TABLE vendor_bookings
ADD CONSTRAINT vendor_bookings_ibfk_3 
FOREIGN KEY (service_id) REFERENCES vendor_services(id) 
ON DELETE SET NULL;

-- Verify the change
SHOW CREATE TABLE vendor_bookings;
