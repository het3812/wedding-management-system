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
