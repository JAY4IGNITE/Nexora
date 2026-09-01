-- Migration: Create Topic Skill Mappings

CREATE TYPE mapping_status_enum AS ENUM ('CONFIRMED', 'PROPOSED', 'AMBIGUOUS', 'UNMAPPED');

CREATE TABLE course_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_module_id UUID NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    source VARCHAR(100),
    source_document VARCHAR(255),
    source_url TEXT,
    source_page INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE topic_skill_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID NOT NULL REFERENCES course_topics(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    mapping_status mapping_status_enum NOT NULL DEFAULT 'UNMAPPED',
    mapping_method VARCHAR(100),
    confidence FLOAT,
    source VARCHAR(100),
    source_page INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Policies
ALTER TABLE course_topics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Course topics are globally readable" ON course_topics FOR SELECT USING (true);

ALTER TABLE topic_skill_mappings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Topic skill mappings are globally readable" ON topic_skill_mappings FOR SELECT USING (true);
