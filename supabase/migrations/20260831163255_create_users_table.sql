-- Create user role enum
CREATE TYPE user_role AS ENUM (
  'ADMIN',
  'GOVERNMENT',
  'INSTITUTION',
  'TRAINER',
  'EMPLOYER',
  'STUDENT'
);

-- Create users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  firebase_uid VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) NOT NULL,
  display_name VARCHAR(255),
  role user_role NOT NULL DEFAULT 'STUDENT',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create index on firebase_uid for fast lookups
CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own profile
CREATE POLICY "Users can read own profile" ON users
  FOR SELECT
  USING (firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub');

-- We won't use Supabase Auth JWTs natively since we use Firebase, 
-- but the backend API will use a service role key to bypass RLS,
-- so the backend handles actual authorization and data access.
-- Therefore, we don't strictly need more complex RLS policies if the frontend 
-- doesn't access Supabase directly.
