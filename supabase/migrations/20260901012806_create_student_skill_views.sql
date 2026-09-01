-- View: view_student_skill_profile
-- Aggregates a student's skills along with their maximum proficiency and latest evidence.
CREATE OR REPLACE VIEW view_student_skill_profile AS
SELECT 
    ss.student_id,
    ss.skill_id,
    s.name AS skill_name,
    s.category AS skill_category,
    ss.proficiency,
    ss.confidence,
    ss.verified_status,
    ss.last_assessed,
    (
        SELECT COUNT(*)
        FROM student_skill_evidence e
        WHERE e.student_skill_id = ss.id
    ) AS evidence_count
FROM student_skills ss
JOIN skills s ON s.id = ss.skill_id;

-- View: view_student_skill_gaps
-- Deterministically compares a student's skills against their active target role.
-- Also left-joins the curriculum_gap_intelligence to provide immediate learning context.
CREATE OR REPLACE VIEW view_student_skill_gaps AS
SELECT 
    tr.student_id,
    tr.job_role_id AS target_role_id,
    jr.title AS target_role_title,
    jrs.skill_id,
    s.name AS skill_name,
    jrs.importance_level AS required_importance,
    COALESCE(sp.proficiency, 0) AS current_proficiency,
    CASE 
        WHEN sp.proficiency IS NULL OR sp.proficiency = 0 THEN 'GAP'
        WHEN sp.proficiency < 3 AND jrs.importance_level > 50 THEN 'PARTIAL'
        ELSE 'MATCHED'
    END AS gap_status,
    cgi.alignment_status AS curriculum_coverage_status
FROM student_target_roles tr
JOIN job_roles jr ON jr.id = tr.job_role_id
JOIN job_role_skills jrs ON jrs.job_role_id = tr.job_role_id
JOIN skills s ON s.id = jrs.skill_id
LEFT JOIN view_student_skill_profile sp 
    ON sp.student_id = tr.student_id AND sp.skill_id = jrs.skill_id
LEFT JOIN view_curriculum_gap_intelligence cgi
    ON cgi.skill_id = jrs.skill_id
WHERE tr.status = 'ACTIVE';

-- Set up RLS/grants if needed
GRANT SELECT ON view_student_skill_profile TO authenticated;
GRANT SELECT ON view_student_skill_gaps TO authenticated;
GRANT SELECT ON view_student_skill_profile TO anon;
GRANT SELECT ON view_student_skill_gaps TO anon;
