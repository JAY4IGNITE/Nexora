-- Migration: Create Curriculum Gap Engine

CREATE TYPE demand_priority_enum AS ENUM ('HIGH', 'MEDIUM', 'LOW', 'NONE');
CREATE TYPE coverage_status_enum AS ENUM ('HIGH', 'LOW', 'UNKNOWN', 'NOT_COVERED');
CREATE TYPE gap_alignment_enum AS ENUM ('ALIGNED', 'PARTIALLY_ALIGNED', 'UNDER_COVERED', 'NOT_COVERED', 'UNKNOWN');

-- Global Gap Intelligence View
CREATE OR REPLACE VIEW view_curriculum_gap_intelligence AS
WITH industry_demand AS (
    SELECT skill_id, count(job_posting_id) as demand_count
    FROM job_posting_skills
    GROUP BY skill_id
),
curriculum_coverage AS (
    SELECT skill_id, count(course_id) as course_count
    FROM course_skills
    GROUP BY skill_id
)
SELECT 
    s.id as skill_id,
    s.name as skill_name,
    s.category as skill_category,
    
    COALESCE(d.demand_count, 0) as demand_count,
    CASE 
        WHEN COALESCE(d.demand_count, 0) > 50 THEN 'HIGH'::demand_priority_enum
        WHEN COALESCE(d.demand_count, 0) >= 10 THEN 'MEDIUM'::demand_priority_enum
        WHEN COALESCE(d.demand_count, 0) > 0 THEN 'LOW'::demand_priority_enum
        ELSE 'NONE'::demand_priority_enum
    END as demand_priority,

    COALESCE(cc.course_count, 0) as coverage_count,
    CASE 
        WHEN COALESCE(cc.course_count, 0) >= 3 THEN 'HIGH'::coverage_status_enum
        WHEN COALESCE(cc.course_count, 0) > 0 THEN 'LOW'::coverage_status_enum
        ELSE 'UNKNOWN'::coverage_status_enum
    END as coverage_status,

    CASE 
        -- ALIGNED: Demand is HIGH/MEDIUM + Coverage is HIGH
        WHEN COALESCE(d.demand_count, 0) >= 10 AND COALESCE(cc.course_count, 0) >= 3 THEN 'ALIGNED'::gap_alignment_enum
        
        -- PARTIALLY_ALIGNED: Demand is HIGH/MEDIUM + Coverage is LOW
        WHEN COALESCE(d.demand_count, 0) >= 10 AND COALESCE(cc.course_count, 0) > 0 THEN 'PARTIALLY_ALIGNED'::gap_alignment_enum
        
        -- UNDER_COVERED: Demand is HIGH + Coverage is UNKNOWN
        WHEN COALESCE(d.demand_count, 0) > 50 AND COALESCE(cc.course_count, 0) = 0 THEN 'UNDER_COVERED'::gap_alignment_enum
        
        -- NOT_COVERED: Demand is MEDIUM + Coverage is UNKNOWN
        WHEN COALESCE(d.demand_count, 0) >= 10 AND COALESCE(cc.course_count, 0) = 0 THEN 'NOT_COVERED'::gap_alignment_enum
        
        -- UNKNOWN: Demand is LOW/NONE + Coverage is UNKNOWN
        ELSE 'UNKNOWN'::gap_alignment_enum
    END as alignment_status

FROM skills s
LEFT JOIN industry_demand d ON s.id = d.skill_id
LEFT JOIN curriculum_coverage cc ON s.id = cc.skill_id
WHERE COALESCE(d.demand_count, 0) > 0 OR COALESCE(cc.course_count, 0) > 0;

-- Role-Level Gap Intelligence View
CREATE OR REPLACE VIEW view_role_curriculum_alignment AS
WITH role_demand AS (
    SELECT jps.skill_id, jp.job_role_id, count(jp.id) as demand_count
    FROM job_posting_skills jps
    JOIN job_postings jp ON jps.job_posting_id = jp.id
    WHERE jp.job_role_id IS NOT NULL
    GROUP BY jps.skill_id, jp.job_role_id
),
curriculum_coverage AS (
    SELECT skill_id, count(course_id) as course_count
    FROM course_skills
    GROUP BY skill_id
)
SELECT 
    jr.id as job_role_id,
    jr.name as job_role_name,
    s.id as skill_id,
    s.name as skill_name,
    
    COALESCE(rd.demand_count, 0) as role_demand_count,
    CASE 
        WHEN COALESCE(rd.demand_count, 0) > 10 THEN 'HIGH'::demand_priority_enum
        WHEN COALESCE(rd.demand_count, 0) >= 5 THEN 'MEDIUM'::demand_priority_enum
        WHEN COALESCE(rd.demand_count, 0) > 0 THEN 'LOW'::demand_priority_enum
        ELSE 'NONE'::demand_priority_enum
    END as demand_priority,

    COALESCE(cc.course_count, 0) as coverage_count,
    CASE 
        WHEN COALESCE(cc.course_count, 0) >= 3 THEN 'HIGH'::coverage_status_enum
        WHEN COALESCE(cc.course_count, 0) > 0 THEN 'LOW'::coverage_status_enum
        ELSE 'UNKNOWN'::coverage_status_enum
    END as coverage_status,

    CASE 
        WHEN COALESCE(rd.demand_count, 0) >= 5 AND COALESCE(cc.course_count, 0) >= 3 THEN 'ALIGNED'::gap_alignment_enum
        WHEN COALESCE(rd.demand_count, 0) >= 5 AND COALESCE(cc.course_count, 0) > 0 THEN 'PARTIALLY_ALIGNED'::gap_alignment_enum
        WHEN COALESCE(rd.demand_count, 0) > 10 AND COALESCE(cc.course_count, 0) = 0 THEN 'UNDER_COVERED'::gap_alignment_enum
        WHEN COALESCE(rd.demand_count, 0) >= 5 AND COALESCE(cc.course_count, 0) = 0 THEN 'NOT_COVERED'::gap_alignment_enum
        ELSE 'UNKNOWN'::gap_alignment_enum
    END as alignment_status

FROM job_roles jr
JOIN role_demand rd ON jr.id = rd.job_role_id
JOIN skills s ON rd.skill_id = s.id
LEFT JOIN curriculum_coverage cc ON s.id = cc.skill_id;
