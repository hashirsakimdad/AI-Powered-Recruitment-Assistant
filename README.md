# AI-Powered Recruitment Assistant

Production-ready Flask application for AI-assisted hiring: recruiters post jobs and review ranked candidates; candidates upload resumes and receive instant scoring, feedback, and application tracking.

## Tech Stack

- **Flask** — web framework with Blueprints
- **SQLAlchemy** + **Flask-Migrate** — ORM and migrations
- **Flask-WTF** — CSRF protection
- **Flask-Limiter** — rate limiting
- **Flask-Mail** — status-change email notifications
- **SentenceTransformers** (optional) — semantic resume scoring
- **Bootstrap 5** — UI
- **pytest** — automated tests
- **gunicorn** — production WSGI server

## Setup

1. Clone the repository and create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment template and edit values:
   ```bash
   copy .env.example .env
   ```
4. Initialize the database:
   ```bash
   flask db upgrade
   ```
   If migrations are not set up yet, the app also runs `db.create_all()` on startup for SQLite.
5. Run the development server:
   ```bash
   flask run
   ```

### Demo accounts (development only)

When `FLASK_ENV=development` or `SEED_DEMO_USERS=true`:

| Role      | Email                   | Password      |
|-----------|-------------------------|---------------|
| Recruiter | recruiter@example.com   | recruiter123  |
| Candidate | candidate@example.com   | candidate123  |
| Admin     | admin@example.com       | admin123      |

Demo users are **not** seeded in production unless explicitly enabled.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_APP` | Application entry point | `app.py` |
| `FLASK_ENV` | `development` enables debug + demo seed | `production` |
| `SECRET_KEY` | Session/CSRF secret | (required in prod) |
| `DATABASE_URL` | SQLAlchemy URI | `sqlite:///instance/app.db` |
| `UPLOAD_FOLDER` | Resume upload directory | `instance/uploads` |
| `SEED_DEMO_USERS` | Seed demo accounts | `false` |
| `PORT` | Dev server port | `5000` |
| `MAIL_SERVER` | SMTP host | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USERNAME` | SMTP user | — |
| `MAIL_PASSWORD` | SMTP password | — |
| `MAIL_DEFAULT_SENDER` | From address | `noreply@recruitment.app` |

## Architecture

```
app.py                 # Application factory
config.py              # Configuration
extensions.py          # CSRF, Limiter, Mail
models.py              # User, JobPosting, ResumeSubmission
app_helpers.py         # Shared helpers
blueprints/
  auth.py              # Login, signup, logout
  recruiter.py         # Recruiter dashboard, jobs, reports
  candidate.py         # Candidate dashboard, upload, profile
  api.py               # JSON API endpoints
  admin.py             # Admin panel
  auth_utils.py        # login_required, role_required
ai/                    # Parser, scorer, chatbot
services/              # Resume upload/scoring, email
templates/             # Jinja2 HTML
static/                # CSS/JS
tests/                 # pytest suite
```

## Running Tests

```bash
pytest tests/ -v
```

## Deployment

Use the included `Procfile` with gunicorn:

```bash
gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT
```

Set `FLASK_ENV=production`, a strong `SECRET_KEY`, and a production database URL.

## Features

- Role-based dashboards (recruiter, candidate, admin)
- CSRF-protected forms and AJAX
- Rate-limited login, signup, and uploads
- Background resume scoring with live status polling
- Paginated job and submission lists
- Duplicate application prevention
- Job expiry and close-job controls
- Password policy with live checklist on signup
- Email notifications on shortlisted/selected/rejected
- Candidate profile with score breakdown
- Admin user/job management
- CSV/PDF recruiter reports

## API Reference

### `GET /api/job/<job_id>/submissions`

Returns JSON list of submissions for a job (recruiter only, must own the job).

### `GET /api/submission/<id>/status`

Returns scoring status for polling:

```json
{"status": "processing|scored|failed", "score": 72.5, "application_status": "pending"}
```

### `GET /api/submission/<id>/breakdown`

Returns detailed score breakdown (recruiter or owning candidate).
