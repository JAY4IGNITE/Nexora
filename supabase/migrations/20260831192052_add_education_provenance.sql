-- Migration: Add Education Provenance & Raw Extractions

ALTER TABLE curricula 
ADD COLUMN source VARCHAR(100),
ADD COLUMN source_document VARCHAR(255),
ADD COLUMN source_url TEXT,
ADD COLUMN source_page INT;

ALTER TABLE courses 
ADD COLUMN source VARCHAR(100),
ADD COLUMN source_document VARCHAR(255),
ADD COLUMN source_url TEXT,
ADD COLUMN source_page INT;

ALTER TABLE course_modules 
ADD COLUMN source VARCHAR(100),
ADD COLUMN source_document VARCHAR(255),
ADD COLUMN source_url TEXT,
ADD COLUMN source_page INT;

-- Table to store raw JSON outputs from the LLM pipeline
CREATE TABLE raw_curriculum_extractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(100) NOT NULL,
    source_document VARCHAR(255) NOT NULL,
    extracted_page INT,
    raw_json JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE raw_curriculum_extractions ENABLE ROW LEVEL SECURITY;
