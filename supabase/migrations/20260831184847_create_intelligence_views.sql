-- Module 4: Labour Market Intelligence Views

-- 1. Demand by Skill
CREATE OR REPLACE VIEW view_demand_by_skill AS
SELECT s.id as skill_id, s.name as skill_name, s.category, COUNT(jps.job_posting_id) as demand_count
FROM skills s
JOIN job_posting_skills jps ON s.id = jps.skill_id
GROUP BY s.id, s.name, s.category;

-- 2. Demand by Role
CREATE OR REPLACE VIEW view_demand_by_role AS
SELECT r.id as role_id, r.name as role_name, COUNT(jp.id) as demand_count
FROM job_roles r
JOIN job_postings jp ON r.id = jp.job_role_id
GROUP BY r.id, r.name;

-- 3. Demand by Sector
CREATE OR REPLACE VIEW view_demand_by_sector AS
SELECT sec.id as sector_id, sec.name as sector_name, COUNT(jp.id) as demand_count
FROM sectors sec
JOIN job_postings jp ON sec.id = jp.sector_id
GROUP BY sec.id, sec.name;

-- 4. Demand by District
CREATE OR REPLACE VIEW view_demand_by_district AS
SELECT d.id as district_id, d.name as district_name, st.name as state_name, COUNT(jp.id) as demand_count
FROM districts d
JOIN states st ON d.state_id = st.id
JOIN job_postings jp ON d.id = jp.district_id
GROUP BY d.id, d.name, st.name;

-- 5. Skill Trends (Time-Series)
CREATE OR REPLACE VIEW view_skill_trends AS
SELECT s.id as skill_id, s.name as skill_name, date_trunc('month', jp.posted_at) as month, COUNT(jp.id) as demand_count
FROM skills s
JOIN job_posting_skills jps ON s.id = jps.skill_id
JOIN job_postings jp ON jps.job_posting_id = jp.id
WHERE jp.posted_at IS NOT NULL
GROUP BY s.id, s.name, date_trunc('month', jp.posted_at);

-- 6. Role Trends (Time-Series)
CREATE OR REPLACE VIEW view_role_trends AS
SELECT r.id as role_id, r.name as role_name, date_trunc('month', jp.posted_at) as month, COUNT(jp.id) as demand_count
FROM job_roles r
JOIN job_postings jp ON r.id = jp.job_role_id
WHERE jp.posted_at IS NOT NULL
GROUP BY r.id, r.name, date_trunc('month', jp.posted_at);
