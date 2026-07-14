-- Migration: Add users table (authentication foundation)
-- Date: 2026-07-09
-- PRD: PRD-001 (Auth foundation — FastAPI JWT)
-- Description: Introduces the users table required before any authentication or
--              tenant scoping can exist. Passwords are stored as argon2id hashes
--              (never plaintext); email is unique per user.

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- argon2id hash, never plaintext
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Unique index on email doubles as the lookup index for login/verify flows.
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);

COMMENT ON TABLE users IS 'Authenticated users (PRD-001 auth foundation)';
COMMENT ON COLUMN users.email IS 'Unique login identifier';
COMMENT ON COLUMN users.password_hash IS 'argon2id password hash — never store plaintext';
COMMENT ON COLUMN users.is_verified IS 'True once the user has confirmed their email via verification token';
