# Nexora AI Development Rules

## Architecture

- Frontend: React + Vite + TypeScript
- Backend: FastAPI
- Database: Supabase PostgreSQL
- Object storage: Cloudflare R2
- Use REST/WebSockets where appropriate.

## Documentation

Before implementing unfamiliar or changing libraries:
- Use Context7 to retrieve current documentation.
- Prefer official documentation.

## Database

- Use Supabase for PostgreSQL.
- Never modify production data directly.
- Use migrations for schema changes.
- Apply RLS to user-owned data.
- Never expose service-role credentials to the frontend.

## UI

- Maintain a consistent design system.
- Use the established project components.
- Use SkillUI when reverse-engineering a reference design.
- Use Playwright to verify important UI flows.

## Testing

Every completed module should have:
- Unit/API tests where appropriate.
- Playwright end-to-end testing for critical flows.
- Console/network error checks.

## Security

Before declaring a major module complete:
- Run Strix.
- Fix critical/high vulnerabilities.
- Re-run the security scan.

## Git

- Work in small modules.
- Keep commits focused.
- Create a PR after verification.
- Never commit API keys, tokens, passwords, or `.env` files.