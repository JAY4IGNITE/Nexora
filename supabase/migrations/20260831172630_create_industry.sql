-- Industry Migration

CREATE TABLE sectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE job_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    sector_id UUID REFERENCES sectors(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE job_postings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    job_role_id UUID REFERENCES job_roles(id) ON DELETE RESTRICT,
    employer_id UUID REFERENCES users(id) ON DELETE CASCADE,
    sector_id UUID REFERENCES sectors(id) ON DELETE RESTRICT,
    district_id UUID REFERENCES districts(id) ON DELETE SET NULL,
    description TEXT,
    experience_requirements TEXT,
    education_requirements TEXT,
    source VARCHAR(255),
    source_url TEXT,
    posted_at TIMESTAMP WITH TIME ZONE,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Indexes
CREATE INDEX idx_job_roles_sector_id ON job_roles(sector_id);
CREATE INDEX idx_job_postings_role_id ON job_postings(job_role_id);
CREATE INDEX idx_job_postings_employer_id ON job_postings(employer_id);
CREATE INDEX idx_job_postings_district_id ON job_postings(district_id);
CREATE INDEX idx_job_postings_sector_id ON job_postings(sector_id);

-- RLS
ALTER TABLE sectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_postings ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Sectors are globally readable" ON sectors FOR SELECT USING (true);
CREATE POLICY "Job Roles are globally readable" ON job_roles FOR SELECT USING (true);
CREATE POLICY "Job Postings are globally readable" ON job_postings FOR SELECT USING (true);
