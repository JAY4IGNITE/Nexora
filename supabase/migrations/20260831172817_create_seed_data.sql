-- Safe foundational seed data

-- 1. States
INSERT INTO states (name, code) VALUES 
('Maharashtra', 'MH'),
('Karnataka', 'KA'),
('Delhi', 'DL')
ON CONFLICT (name) DO NOTHING;

-- 2. Districts (Assuming Maharashtra for sample)
DO $$ 
DECLARE
    mh_id UUID;
BEGIN
    SELECT id INTO mh_id FROM states WHERE code = 'MH';
    IF FOUND THEN
        INSERT INTO districts (state_id, name, code) VALUES 
        (mh_id, 'Mumbai City', 'MUM'),
        (mh_id, 'Pune', 'PUN'),
        (mh_id, 'Nagpur', 'NAG')
        ON CONFLICT (state_id, name) DO NOTHING;
    END IF;
END $$;

-- 3. Sectors
INSERT INTO sectors (name, description) VALUES
('Information Technology', 'Software development, IT services, and infrastructure'),
('Healthcare', 'Medical services, hospitals, and pharmaceuticals'),
('Finance', 'Banking, financial services, and insurance (BFSI)'),
('Manufacturing', 'Industrial production and engineering'),
('Education', 'Schools, universities, and ed-tech')
ON CONFLICT (name) DO NOTHING;

-- 4. Job Roles
DO $$ 
DECLARE
    it_id UUID;
    finance_id UUID;
BEGIN
    SELECT id INTO it_id FROM sectors WHERE name = 'Information Technology';
    IF FOUND THEN
        INSERT INTO job_roles (name, description, sector_id) VALUES 
        ('Software Engineer', 'Develops and maintains software applications', it_id),
        ('Cloud Engineer', 'Manages cloud infrastructure and deployments', it_id),
        ('Data Analyst', 'Analyzes data to extract actionable insights', it_id),
        ('Cybersecurity Analyst', 'Protects systems and networks from cyber threats', it_id)
        ON CONFLICT (name) DO NOTHING;
    END IF;

    SELECT id INTO finance_id FROM sectors WHERE name = 'Finance';
    IF FOUND THEN
        INSERT INTO job_roles (name, description, sector_id) VALUES 
        ('Financial Analyst', 'Analyzes financial data and market trends', finance_id)
        ON CONFLICT (name) DO NOTHING;
    END IF;
END $$;

-- 5. Canonical Skills
INSERT INTO skills (name, normalized_name, category, skill_type) VALUES
('Python', 'python', 'Programming', 'Hard Skill'),
('JavaScript', 'javascript', 'Programming', 'Hard Skill'),
('SQL', 'sql', 'Database', 'Hard Skill'),
('React', 'react', 'Frontend Framework', 'Hard Skill'),
('Communication', 'communication', 'Soft Skill', 'Soft Skill'),
('Problem Solving', 'problem solving', 'Soft Skill', 'Soft Skill')
ON CONFLICT (normalized_name) DO NOTHING;

-- Skill Aliases
DO $$
DECLARE
    python_id UUID;
    js_id UUID;
BEGIN
    SELECT id INTO python_id FROM skills WHERE normalized_name = 'python';
    IF FOUND THEN
        INSERT INTO skill_aliases (skill_id, alias_name) VALUES
        (python_id, 'Python 3'),
        (python_id, 'Py')
        ON CONFLICT (alias_name) DO NOTHING;
    END IF;

    SELECT id INTO js_id FROM skills WHERE normalized_name = 'javascript';
    IF FOUND THEN
        INSERT INTO skill_aliases (skill_id, alias_name) VALUES
        (js_id, 'JS'),
        (js_id, 'ECMAScript')
        ON CONFLICT (alias_name) DO NOTHING;
    END IF;
END $$;
