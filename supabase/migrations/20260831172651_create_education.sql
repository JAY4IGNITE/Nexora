-- Education and Training Migration

CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    provider_id UUID REFERENCES users(id) ON DELETE SET NULL,
    level VARCHAR(100),
    duration VARCHAR(100),
    mode VARCHAR(100),
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE course_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sequence INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE curricula (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    program_name VARCHAR(255) NOT NULL,
    department VARCHAR(255),
    version VARCHAR(50),
    effective_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE curriculum_skills (
    curriculum_id UUID NOT NULL REFERENCES curricula(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (curriculum_id, skill_id)
);

CREATE TABLE training_provider_courses (
    provider_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (provider_id, course_id)
);

CREATE TABLE training_capacity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    district_id UUID NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
    capacity INT NOT NULL,
    period VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Indexes
CREATE INDEX idx_courses_provider_id ON courses(provider_id);
CREATE INDEX idx_course_modules_course_id ON course_modules(course_id);
CREATE INDEX idx_curricula_institution_id ON curricula(institution_id);
CREATE INDEX idx_training_capacity_course_id ON training_capacity(course_id);
CREATE INDEX idx_training_capacity_district_id ON training_capacity(district_id);

-- RLS
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE curricula ENABLE ROW LEVEL SECURITY;
ALTER TABLE curriculum_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_provider_courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_capacity ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Courses are globally readable" ON courses FOR SELECT USING (true);
CREATE POLICY "Course modules are globally readable" ON course_modules FOR SELECT USING (true);
CREATE POLICY "Curricula are readable by their institutions" ON curricula FOR SELECT USING (
    institution_id IN (
        SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub'
    )
);
CREATE POLICY "Curriculum skills are globally readable" ON curriculum_skills FOR SELECT USING (true);
CREATE POLICY "Training provider courses are globally readable" ON training_provider_courses FOR SELECT USING (true);
CREATE POLICY "Training capacity is globally readable" ON training_capacity FOR SELECT USING (true);
