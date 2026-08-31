# NEXORA Core Database Architecture

## Entity Relationships

The NEXORA data model is built on Supabase PostgreSQL and is divided into several domains:

1. **Identity (`users`, `roles`)**
   - Managed via Firebase Authentication (identity provider).
   - Synced to Supabase for application-level RBAC and foreign-key linking.

2. **Geography (`states`, `districts`)**
   - Hierarchical geographic reference data. Used extensively for regional labour market intelligence and student demographics.

3. **Industry & Labour Market (`sectors`, `job_roles`, `job_postings`)**
   - Forms the demand side of the equation.
   - `job_postings` will eventually ingest live scraping data.

4. **Skills Taxonomy (`skills`, `skill_aliases`, `skill_relationships`, `job_role_skills`)**
   - The central ontology mapping roles to the granular competencies required.

5. **Education & Supply (`courses`, `curricula`, `training_capacity`)**
   - Forms the supply side, tracking where skills are taught and the systemic capacity.

6. **Student Domain (`student_profiles`, `student_skills`, `student_skill_evidence`, `skill_gaps`)**
   - The user-centric view tracking a student's journey, verified skills, and identified deficiencies against their target job roles.

7. **Learning & Interventions (`learning_paths`, `projects`, `student_projects`)**
   - Actuation layers to help students bridge their skill gaps through tailored interventions.

8. **Assessments, Readiness & Outcomes (`assessments`, `interviews`, `readiness_scores`, `placement_outcomes`)**
   - The feedback loop. Measures student readiness and validates the entire pipeline through actual placement success.

## System Responsibilities

- **Firebase**: Sole responsibility for Authentication (passwords, OAuth, session management).
- **Supabase**: Source of truth for relational application data and business rules via Postgres RLS.
- **Cloudflare R2**: Object storage for unstructured binary data (Resumes, certificates). Postgres tables will store the URLs referencing these objects.
- **Qdrant**: Vector database for semantic search (e.g., skill similarity, resume matching).
- **Redis**: Caching layer for fast reads (e.g., dashboard stats) and realtime Pub/Sub.

## Security and Row-Level Security (RLS) Strategy

NEXORA uses strict RLS on all tables within the `public` schema.
- **Public Reference Data**: Tables like `skills`, `sectors`, and `geography` are globally readable (`FOR SELECT USING (true)`).
- **User Private Data**: Tables like `student_profiles`, `skill_gaps`, and `learning_paths` are strictly locked down to the owner using their `firebase_uid`.
- **Backend Elevation**: The FastAPI backend communicates with Supabase using the `SERVICE_ROLE_KEY`, bypassing RLS for complex cross-tenant aggregations and administrative operations.

## Migration Strategy

Migrations are purely declarative and imperative via SQL. They are managed in `supabase/migrations/` and must be applied linearly. We do not use the Supabase Dashboard UI to alter schemas in production.
