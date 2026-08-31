-- Learning and Projects Migration

CREATE TABLE learning_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    target_role_id UUID REFERENCES job_roles(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE learning_path_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learning_path_id UUID NOT NULL REFERENCES learning_paths(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE SET NULL,
    sequence INT NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING',
    progress DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty VARCHAR(50),
    estimated_duration VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE project_skills (
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (project_id, skill_id)
);

CREATE TABLE student_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'IN_PROGRESS',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    evidence_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Indexes
CREATE INDEX idx_learning_paths_student_id ON learning_paths(student_id);
CREATE INDEX idx_learning_path_items_path_id ON learning_path_items(learning_path_id);
CREATE INDEX idx_student_projects_student_id ON student_projects(student_id);
CREATE INDEX idx_student_projects_project_id ON student_projects(project_id);

-- RLS
ALTER TABLE learning_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_path_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_projects ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Students can read own learning paths" ON learning_paths FOR SELECT USING (
    student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
CREATE POLICY "Students can read own learning path items" ON learning_path_items FOR SELECT USING (
    learning_path_id IN (SELECT id FROM learning_paths WHERE student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub'))
);
CREATE POLICY "Projects are globally readable" ON projects FOR SELECT USING (true);
CREATE POLICY "Project skills are globally readable" ON project_skills FOR SELECT USING (true);
CREATE POLICY "Students can read own student projects" ON student_projects FOR SELECT USING (
    student_id IN (SELECT id FROM users WHERE firebase_uid = current_setting('request.jwt.claims', true)::json->>'sub')
);
