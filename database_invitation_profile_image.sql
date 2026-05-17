-- Add profile/cover image to invitations table
-- This allows hosts to set a featured couple photo for their invitation

ALTER TABLE invitations 
ADD COLUMN profile_image VARCHAR(255) DEFAULT NULL COMMENT 'Featured couple/profile photo for invitation card';

-- Note: If you get "Duplicate column" error, the column already exists. You can skip this migration.
