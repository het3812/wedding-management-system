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
