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
