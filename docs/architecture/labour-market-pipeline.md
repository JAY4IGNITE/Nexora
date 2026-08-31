# NEXORA Labour Market Intelligence Pipeline

## 1. Architecture
The labour market pipeline transforms raw job data from external providers into the structured `job_postings` table in Supabase. It uses a scalable `PipelineEngine` to perform ETL (Extract, Transform, Load) operations within atomic transactions.

## 2. Data Flow
External Provider -> RawJobRecord -> Validation -> Cleaning -> Location/Role Normalization -> Skill Extraction -> Deduplication -> Supabase Insert -> Ingestion Stats Update.

## 3. Provider Abstraction
Providers inherit from `JobDataProvider`.
- `MockJobProvider`: Deterministic synthetic dataset for testing.
- `AdzunaProvider`: Live integration fetching from the Adzuna API targeting the IN region.

## 4. Raw Record Model
Data is normalized into the Pydantic `RawJobRecord` ensuring required fields (like `title`, `employer`, `source_job_id`) are present before proceeding. We preserve salary boundaries (`salary_min`, `salary_max`) and contract types.

## 5. Normalization
- **Job Roles**: Falls back to the LLMExtractionService (Gemini) for semantic similarity if an exact canonical match isn't found.
- **Location**: Matched directly against canonical `districts` and `states` tables.

## 6. Deduplication
Idempotency is maintained by hashing `source` and `source_url` (or `source_job_id`). The pipeline queries Supabase before inserting to prevent duplicate records on repeated ingestion runs.

## 7. Skill Extraction
Uses a hybrid approach:
1. Exact string matching against the canonical `skills` dictionary.
2. Semantic extraction via LLM to capture implicit requirements.

## 8. Provider Setup: Adzuna API
To ingest real data from Adzuna:
1. Obtain an App ID and App Key from [Adzuna Developer Portal](https://developer.adzuna.com/).
2. Add the credentials to the backend `.env` file:
   ```env
   ADZUNA_APP_ID=your_id
   ADZUNA_APP_KEY=your_key
   ```
3. Trigger ingestion via the admin dashboard or the API endpoint by passing `?provider=adzuna`.

## 9. Error Handling
- Errors at the individual job level skip that record, increment `records_failed`, and continue processing.
- Failed HTTP requests to external APIs gracefully terminate the run.

## 10. Security
- The ingestion API is protected by role-based access control (`UserRole.ADMIN`).
- Supabase connections rely on the backend `SERVICE_ROLE_KEY` to securely bypass public RLS restrictions.
