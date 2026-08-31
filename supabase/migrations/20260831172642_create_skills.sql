-- Skills Migration

CREATE TYPE skill_relationship_type AS ENUM (
    'PREREQUISITE',
    'RELATED_TO',
    'USED_WITH',
    'COMPLEMENTARY',
    'SUBSKILL'
);

CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(255),
    description TEXT,
    skill_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE skill_aliases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    alias_name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE skill_relationships (
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    related_skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    relationship_type skill_relationship_type NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (skill_id, related_skill_id, relationship_type)
);

CREATE TABLE job_role_skills (
    job_role_id UUID NOT NULL REFERENCES job_roles(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    importance INT CHECK (importance >= 1 AND importance <= 5),
    proficiency_level VARCHAR(100),
    evidence_source VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (job_role_id, skill_id)
);

-- Indexes
CREATE INDEX idx_skills_normalized ON skills(normalized_name);
CREATE INDEX idx_skill_aliases_skill_id ON skill_aliases(skill_id);
CREATE INDEX idx_skill_rels_skill_id ON skill_relationships(skill_id);
CREATE INDEX idx_skill_rels_related_id ON skill_relationships(related_skill_id);
CREATE INDEX idx_job_role_skills_role_id ON job_role_skills(job_role_id);
CREATE INDEX idx_job_role_skills_skill_id ON job_role_skills(skill_id);

-- RLS
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_aliases ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_role_skills ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Skills are globally readable" ON skills FOR SELECT USING (true);
CREATE POLICY "Skill aliases are globally readable" ON skill_aliases FOR SELECT USING (true);
CREATE POLICY "Skill relationships are globally readable" ON skill_relationships FOR SELECT USING (true);
CREATE POLICY "Job role skills are globally readable" ON job_role_skills FOR SELECT USING (true);
