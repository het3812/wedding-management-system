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
