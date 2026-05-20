# AI-Powered Recruitment Assistant

Python/Flask prototype featuring dual dashboards (recruiter and candidate), resume parsing, AI scoring/ranking, chatbot-style feedback, and CSV export. Database via SQLAlchemy (MySQL/PostgreSQL ready; SQLite defaults for quick starts).

## Quickstart
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables (optional):
   ```bash
   set FLASK_APP=app.py
   set SECRET_KEY=change-me
   set DATABASE_URL=sqlite:///instance/app.db   # or postgres://user:pass@host/db
   ```
4. Run:
   ```bash
   flask run
   ```
5. Demo users: recruiter@demo.com / demo123, candidate@demo.com / demo123.

## Features
- Recruiter dashboard: job creation, ranked candidate list, CSV export.
- Candidate dashboard: resume upload (PDF/DOCX), instant AI scoring + feedback.
- AI/NLP: parsing, semantic scoring (SentenceTransformers fallback to heuristic), skill-gap feedback, rationale traces.
- Charts: Chart.js bar chart for ranking visualization.
- Database: SQLAlchemy models for users, jobs, submissions; ready for migrations.

## File Map
- `app.py` — Flask app, routes, session-based auth, role checks.
- `config.py` — configuration and instance folder setup.
- `models.py` — SQLAlchemy models + demo seed users.
- `ai/` — parsing (`parser.py`), scoring (`scorer.py`), chatbot feedback (`chatbot.py`).
- `services/resume_service.py` — upload, parse, score orchestration.
- `templates/` — HTML pages (Bootstrap).
- `static/` — CSS/JS assets.
- `requirements.txt` — dependencies.
- `report.md` — academic-style project report template (fill names/registration numbers).

## Data & Deployment Notes
- Uploads stored in `instance/uploads`. Adjust via `UPLOAD_FOLDER`.
- Use `Flask-Migrate` for production DB migrations.
- For PostgreSQL/MySQL, update `DATABASE_URL` and create the database before running.
- GPU recommended if enabling full SentenceTransformer embeddings; CPU fallback included.

## Tests / Checks
- Not included; add unit tests for AI scoring, parsing, and route access as next steps.

#
