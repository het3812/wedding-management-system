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
