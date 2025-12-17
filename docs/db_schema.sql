-- =============================================
-- Community Registration System - DB Schema
-- PostgreSQL
-- =============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- ENUM TYPES
-- =============================================

-- Verification type (Mobile or Email)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'verification_type_enum') THEN
        CREATE TYPE verification_type_enum AS ENUM ('mobile', 'email');
    END IF;
END$$;

-- User status
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_status_enum') THEN
        CREATE TYPE user_status_enum AS ENUM ('pending', 'hold', 'rejected');
    END IF;
END$$;

-- Admin roles
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'admin_role_enum') THEN
        CREATE TYPE admin_role_enum AS ENUM ('super_admin', 'verifier', 'readonly');
    END IF;
END$$;

-- =============================================
-- OTP VERIFICATIONS
-- =============================================

CREATE TABLE IF NOT EXISTS otp_verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identifier VARCHAR(150) NOT NULL, -- mobile number or email
    verification_type verification_type_enum NOT NULL,
    otp VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    attempts INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_otp_identifier
ON otp_verifications(identifier);

-- =============================================
-- USERS - PENDING REGISTRATIONS
-- =============================================

CREATE TABLE IF NOT EXISTS users_pending (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    verification_type verification_type_enum NOT NULL,
    mobile_number VARCHAR(10) UNIQUE,
    email VARCHAR(150) UNIQUE,
    is_verified BOOLEAN DEFAULT FALSE,

    full_name VARCHAR(150) NOT NULL,
    surname VARCHAR(80) NOT NULL,
    desired_name VARCHAR(150) NOT NULL,
    father_or_husband_name VARCHAR(150) NOT NULL,
    mother_name VARCHAR(150) NOT NULL,
    date_of_birth DATE,

    gender VARCHAR(20),
    blood_group VARCHAR(5),

    gothram VARCHAR(120) NOT NULL,
    aaradhya_daiva VARCHAR(120),
    kula_devata VARCHAR(120),

    education VARCHAR(120) NOT NULL,
    occupation VARCHAR(120) NOT NULL,

    house_number VARCHAR(60),
    village_city VARCHAR(120) NOT NULL,
    mandal VARCHAR(120) NOT NULL,
    district VARCHAR(120) NOT NULL,
    state VARCHAR(120) NOT NULL,
    country VARCHAR(120) DEFAULT 'India',
    pin_code VARCHAR(10) NOT NULL,

    photo_url TEXT NOT NULL,
    pdf_url TEXT NOT NULL,

    referred_by_name VARCHAR(150) NOT NULL,
    referred_mobile VARCHAR(10) NOT NULL,
    feedback TEXT,

    status user_status_enum DEFAULT 'pending',
    hold_reason TEXT,
    reject_reason TEXT,
    possible_duplicate BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pending_status
ON users_pending(status);

CREATE INDEX IF NOT EXISTS idx_pending_location
ON users_pending(state, district, mandal);

-- =============================================
-- USERS - VERIFIED MEMBERS
-- =============================================

CREATE TABLE IF NOT EXISTS users_verified (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    membership_id VARCHAR(30) UNIQUE NOT NULL,

    verification_type verification_type_enum NOT NULL,
    mobile_number VARCHAR(10) UNIQUE,
    email VARCHAR(150) UNIQUE,

    full_name VARCHAR(150) NOT NULL,
    surname VARCHAR(80) NOT NULL,
    desired_name VARCHAR(150) NOT NULL,
    father_or_husband_name VARCHAR(150) NOT NULL,
    mother_name VARCHAR(150) NOT NULL,
    date_of_birth DATE,

    gender VARCHAR(20),
    blood_group VARCHAR(5),

    gothram VARCHAR(120) NOT NULL,
    aaradhya_daiva VARCHAR(120),
    kula_devata VARCHAR(120),

    education VARCHAR(120) NOT NULL,
    occupation VARCHAR(120) NOT NULL,

    house_number VARCHAR(60),
    village_city VARCHAR(120) NOT NULL,
    mandal VARCHAR(120) NOT NULL,
    district VARCHAR(120) NOT NULL,
    state VARCHAR(120) NOT NULL,
    country VARCHAR(120) DEFAULT 'India',
    pin_code VARCHAR(10) NOT NULL,

    photo_url TEXT NOT NULL,
    pdf_url TEXT NOT NULL,

    referred_by_name VARCHAR(150) NOT NULL,
    referred_mobile VARCHAR(10) NOT NULL,
    feedback TEXT,

    approved_by UUID,
    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_verified_membership
ON users_verified(membership_id);

CREATE INDEX IF NOT EXISTS idx_verified_location
ON users_verified(state, district, mandal);

-- =============================================
-- ADMIN USERS
-- =============================================

CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role admin_role_enum NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- AUDIT LOGS
-- =============================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    performed_by UUID,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_entity
ON audit_logs(entity_type, entity_id);

-- =============================================
-- END OF SCHEMA
-- =============================================
