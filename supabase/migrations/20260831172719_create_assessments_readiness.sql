-- Assessments, Readiness, and Outcomes Migration

CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    target_role_id UUID REFERENCES job_roles(id) ON DELETE CASCADE,
    difficulty VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE assessment_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE assessment_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'IN_PROGRESS',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE assessment_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID NOT NULL REFERENCES assessment_attempts(id) ON DELETE CASCADE,
    score DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    target_role_id UUID NOT NULL REFERENCES job_roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE interview_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_id UUID NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE interview_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES interview_questions(id) ON DELETE CASCADE,
    response TEXT,
    evaluation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE readiness_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    target_role_id UUID NOT NULL REFERENCES job_roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE readiness_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES readiness_assessments(id) ON DELETE CASCADE,
    score_breakdown JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE placement_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    employer_id UUID REFERENCES users(id) ON DELETE SET NULL,
    job_role_id UUID REFERENCES job_roles(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL,
    placement_date DATE,
    source VARCHAR(255),
    relevant_outcome_information TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Indexes
CREATE INDEX idx_assessments_target_skill ON assessments(target_skill_id);
CREATE INDEX idx_assessment_attempts_student ON assessment_attempts(student_id);
CREATE INDEX idx_interviews_student ON interviews(student_id);
CREATE INDEX idx_readiness_assessments_student ON readiness_assessments(student_id);
CREATE INDEX idx_placement_outcomes_student ON placement_outcomes(student_id);

-- RLS
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE readiness_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE readiness_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE placement_outcomes ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Assessments are globally readable" ON assessments FOR SELECT USING (true);
CREATE POLICY "Assessment questions are globally readable" ON assessment_questions FOR SELECT USING (true);

CREATE POLICY "Students can read own assessment attempts" ON assessment_attempts FOR SELECT USING (
    student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
CREATE POLICY "Students can read own assessment results" ON assessment_results FOR SELECT USING (
    attempt_id IN (SELECT id FROM assessment_attempts WHERE student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub'))
);

CREATE POLICY "Students can read own interviews" ON interviews FOR SELECT USING (
    student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
CREATE POLICY "Students can read own interview questions" ON interview_questions FOR SELECT USING (
    interview_id IN (SELECT id FROM interviews WHERE student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub'))
);
CREATE POLICY "Students can read own interview responses" ON interview_responses FOR SELECT USING (
    question_id IN (SELECT id FROM interview_questions WHERE interview_id IN (SELECT id FROM interviews WHERE student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')))
);

CREATE POLICY "Students can read own readiness assessments" ON readiness_assessments FOR SELECT USING (
    student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
CREATE POLICY "Students can read own readiness scores" ON readiness_scores FOR SELECT USING (
    assessment_id IN (SELECT id FROM readiness_assessments WHERE student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub'))
);

CREATE POLICY "Students can read own placement outcomes" ON placement_outcomes FOR SELECT USING (
    student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
