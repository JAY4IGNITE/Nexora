-- Module 5: Demand-Supply Gap Engine

CREATE OR REPLACE VIEW view_demand_supply_gap AS
WITH skill_demand AS (
    SELECT skill_id, count(job_posting_id) as demand_count
    FROM job_posting_skills
    GROUP BY skill_id
),
skill_workforce_supply AS (
    SELECT skill_id, count(student_id) as student_count
    FROM student_skills
    WHERE proficiency >= 3 -- Only count students with working proficiency
    GROUP BY skill_id
),
skill_training_supply AS (
    SELECT cs.skill_id, COALESCE(sum(tc.capacity), 0) as training_capacity
    FROM curriculum_skills cs
    JOIN curricula c ON cs.curriculum_id = c.id
    JOIN courses crs ON c.institution_id = crs.provider_id
    JOIN training_capacity tc ON crs.id = tc.course_id
    GROUP BY cs.skill_id
)
SELECT 
    s.id as skill_id,
    s.name as skill_name,
    s.category,
    COALESCE(d.demand_count, 0) as demand,
    COALESCE(ws.student_count, 0) as workforce_supply,
    COALESCE(ts.training_capacity, 0) as training_supply,
    (COALESCE(ws.student_count, 0) + COALESCE(ts.training_capacity, 0)) as total_supply,
    -- Net Gap: Negative means Deficit (Demand > Supply), Positive means Surplus (Supply > Demand)
    (COALESCE(ws.student_count, 0) + COALESCE(ts.training_capacity, 0)) - COALESCE(d.demand_count, 0) as net_gap
FROM skills s
LEFT JOIN skill_demand d ON s.id = d.skill_id
LEFT JOIN skill_workforce_supply ws ON s.id = ws.skill_id
LEFT JOIN skill_training_supply ts ON s.id = ts.skill_id
-- We only want to evaluate skills that actually have some demand or supply
WHERE COALESCE(d.demand_count, 0) > 0 OR COALESCE(ws.student_count, 0) > 0 OR COALESCE(ts.training_capacity, 0) > 0;
