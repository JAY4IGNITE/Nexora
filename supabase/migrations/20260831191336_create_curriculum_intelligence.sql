-- Module 6: Curriculum & Training Intelligence

CREATE TYPE coverage_level_enum AS ENUM ('NOT_COVERED', 'INTRODUCTORY', 'INTERMEDIATE', 'ADVANCED', 'COVERED');

ALTER TABLE curriculum_skills 
ADD COLUMN coverage_level coverage_level_enum DEFAULT 'COVERED',
ADD COLUMN source_url TEXT,
ADD COLUMN last_verified_at TIMESTAMP WITH TIME ZONE;

CREATE TABLE course_skills (
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    coverage_level coverage_level_enum DEFAULT 'COVERED',
    source_url TEXT,
    last_verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (course_id, skill_id)
);

CREATE INDEX idx_course_skills_skill_id ON course_skills(skill_id);
ALTER TABLE course_skills ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Course skills are globally readable" ON course_skills FOR SELECT USING (true);

-- Curriculum Intelligence View
CREATE OR REPLACE VIEW view_curriculum_alignment AS
WITH industry_demand AS (
    SELECT skill_id, count(job_posting_id) as demand_count
    FROM job_posting_skills
    GROUP BY skill_id
),
curriculum_coverage AS (
    SELECT skill_id, count(curriculum_id) as program_count
    FROM curriculum_skills
    GROUP BY skill_id
),
training_coverage AS (
    SELECT skill_id, count(course_id) as program_count
    FROM course_skills
    GROUP BY skill_id
)
SELECT 
    s.id as skill_id,
    s.name as skill_name,
    s.category as skill_category,
    COALESCE(d.demand_count, 0) as industry_demand_count,
    COALESCE(cc.program_count, 0) as curriculum_program_count,
    COALESCE(tc.program_count, 0) as training_program_count,
    (COALESCE(cc.program_count, 0) + COALESCE(tc.program_count, 0)) as total_coverage_count,
    
    -- Priority Score (Demand / (1 + Coverage))
    COALESCE(d.demand_count, 0)::float / GREATEST(1, COALESCE(cc.program_count, 0) + COALESCE(tc.program_count, 0)) as gap_priority,
    
    -- Gap Classification based on evidence
    CASE 
        WHEN COALESCE(d.demand_count, 0) = 0 THEN 'NO_DEMAND'
        WHEN (COALESCE(cc.program_count, 0) + COALESCE(tc.program_count, 0)) = 0 THEN 'NOT_COVERED'
        WHEN (COALESCE(cc.program_count, 0) + COALESCE(tc.program_count, 0)) < COALESCE(d.demand_count, 0) / 2 THEN 'UNDER_COVERED'
        ELSE 'ALIGNED'
    END as classification
FROM skills s
JOIN industry_demand d ON s.id = d.skill_id -- Only evaluate skills with SOME industry demand
LEFT JOIN curriculum_coverage cc ON s.id = cc.skill_id
LEFT JOIN training_coverage tc ON s.id = tc.skill_id;
