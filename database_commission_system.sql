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
