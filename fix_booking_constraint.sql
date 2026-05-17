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
