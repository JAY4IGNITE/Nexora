-- Module 3: Pipeline Infrastructure and Module 2 Audit Fixes

-- 1. Create ingestion run tracking
CREATE TABLE job_ingestion_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR(255) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'RUNNING',
    records_received INT DEFAULT 0,
    records_valid INT DEFAULT 0,
    records_rejected INT DEFAULT 0,
    records_duplicate INT DEFAULT 0,
    records_inserted INT DEFAULT 0,
    records_updated INT DEFAULT 0,
    records_failed INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Create job posting skills (extracted skills per posting)
CREATE TABLE job_posting_skills (
    job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    extraction_method VARCHAR(100),
    confidence DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (job_posting_id, skill_id)
);

CREATE INDEX idx_job_posting_skills_posting ON job_posting_skills(job_posting_id);
CREATE INDEX idx_job_posting_skills_skill ON job_posting_skills(skill_id);

-- RLS for new tables
ALTER TABLE job_ingestion_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_posting_skills ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Ingestion runs globally readable" ON job_ingestion_runs FOR SELECT USING (true);
CREATE POLICY "Job posting skills globally readable" ON job_posting_skills FOR SELECT USING (true);
-- Service role handles inserts, no public insert policies needed for ingestion

-- 3. Module 2 Audit Fixes

-- A. Timestamp Triggers
CREATE EXTENSION IF NOT EXISTS moddatetime schema extensions;

CREATE TRIGGER handle_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON states FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON districts FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON sectors FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON job_roles FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON job_postings FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON skills FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON courses FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON course_modules FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON curricula FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON training_capacity FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON student_profiles FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON student_skills FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON student_target_roles FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON skill_gaps FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON learning_paths FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON learning_path_items FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON student_projects FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON assessments FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON assessment_attempts FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON interviews FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON readiness_assessments FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON placement_outcomes FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON job_ingestion_runs FOR EACH ROW EXECUTE PROCEDURE extensions.moddatetime(updated_at);

-- B. Normalize Readiness Scores
-- Move from JSONB to relational dimensions
ALTER TABLE readiness_scores DROP COLUMN score_breakdown;

CREATE TABLE readiness_score_dimensions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    readiness_score_id UUID NOT NULL REFERENCES readiness_scores(id) ON DELETE CASCADE,
    dimension_name VARCHAR(100) NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX idx_readiness_dims_score_id ON readiness_score_dimensions(readiness_score_id);
ALTER TABLE readiness_score_dimensions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Students can read own readiness dims" ON readiness_score_dimensions FOR SELECT USING (
    readiness_score_id IN (
        SELECT rs.id FROM readiness_scores rs 
        JOIN readiness_assessments ra ON rs.assessment_id = ra.id 
        WHERE ra.student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
    )
);

-- C. CUD Policies for Student Domain
CREATE POLICY "Students can insert own profile" ON student_profiles FOR INSERT WITH CHECK (
    id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
CREATE POLICY "Students can update own profile" ON student_profiles FOR UPDATE USING (
    id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
CREATE POLICY "Students can insert own skills" ON student_skills FOR INSERT WITH CHECK (
    student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
CREATE POLICY "Students can update own skills" ON student_skills FOR UPDATE USING (
    student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
CREATE POLICY "Students can delete own skills" ON student_skills FOR DELETE USING (
    student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
