-- Student Domain Migration

CREATE TABLE student_profiles (
    id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    institution_id UUID REFERENCES users(id) ON DELETE SET NULL,
    program VARCHAR(255),
    graduation_year INT,
    district_id UUID REFERENCES districts(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TYPE evidence_type_enum AS ENUM (
    'RESUME',
    'PROJECT',
    'ASSESSMENT',
    'INTERVIEW',
    'CERTIFICATE',
    'MANUAL_VERIFICATION'
);

CREATE TABLE student_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proficiency INT CHECK (proficiency >= 1 AND proficiency <= 5),
    confidence DECIMAL(5,2),
    source VARCHAR(255),
    verified_status BOOLEAN DEFAULT FALSE,
    last_assessed TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(student_id, skill_id)
);

CREATE TABLE student_skill_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_skill_id UUID NOT NULL REFERENCES student_skills(id) ON DELETE CASCADE,
    evidence_type evidence_type_enum NOT NULL,
    evidence_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE student_target_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    job_role_id UUID NOT NULL REFERENCES job_roles(id) ON DELETE CASCADE,
    priority INT DEFAULT 1,
    target_date DATE,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(student_id, job_role_id)
);

CREATE TABLE skill_gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    target_role_id UUID NOT NULL REFERENCES job_roles(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    required_proficiency INT,
    current_proficiency INT,
    gap_severity VARCHAR(50),
    status VARCHAR(50) DEFAULT 'OPEN',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Indexes
CREATE INDEX idx_student_profiles_inst_id ON student_profiles(institution_id);
CREATE INDEX idx_student_profiles_dist_id ON student_profiles(district_id);
CREATE INDEX idx_student_skills_student_id ON student_skills(student_id);
CREATE INDEX idx_student_skills_skill_id ON student_skills(skill_id);
CREATE INDEX idx_student_skill_evidence_sk_id ON student_skill_evidence(student_skill_id);
CREATE INDEX idx_student_target_roles_student_id ON student_target_roles(student_id);
CREATE INDEX idx_student_target_roles_role_id ON student_target_roles(job_role_id);
CREATE INDEX idx_skill_gaps_student_id ON skill_gaps(student_id);

-- RLS
ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_skill_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_target_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_gaps ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Students can read own profile" ON student_profiles FOR SELECT USING (
    id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
CREATE POLICY "Students can read own skills" ON student_skills FOR SELECT USING (
    student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
CREATE POLICY "Students can read own evidence" ON student_skill_evidence FOR SELECT USING (
    student_skill_id IN (SELECT id FROM student_skills WHERE student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub'))
);
CREATE POLICY "Students can read own target roles" ON student_target_roles FOR SELECT USING (
    student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
CREATE POLICY "Students can read own skill gaps" ON skill_gaps FOR SELECT USING (
    student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
