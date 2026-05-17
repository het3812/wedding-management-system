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
