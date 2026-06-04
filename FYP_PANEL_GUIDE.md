# AI-Powered Recruitment Assistant — Complete FYP Panel & Technical Guide

**Read this document before your viva.** It explains what the project does, how every backend component works, how the AI models score resumes (with formulas), and includes ready-made answers for common panel questions.

---

## Table of Contents

1. [30-Second Elevator Pitch](#1-30-second-elevator-pitch)
2. [Problem Statement & Objectives](#2-problem-statement--objectives)
3. [Scope & Limitations (Be Honest With Panel)](#3-scope--limitations-be-honest-with-panel)
4. [System Architecture](#4-system-architecture)
5. [Technology Stack — Why We Chose Each](#5-technology-stack--why-we-chose-each)
6. [Project Folder Structure](#6-project-folder-structure)
7. [Database Design (ER Model)](#7-database-design-er-model)
8. [Complete Request Flow — End to End](#8-complete-request-flow--end-to-end)
9. [Authentication, Security & Authorization](#9-authentication-security--authorization)
10. [AI Pipeline — Step by Step](#10-ai-pipeline--step-by-step)
11. [Resume Text Extraction (Parser)](#11-resume-text-extraction-parser)
12. [Resume Detection Model](#12-resume-detection-model)
13. [Skill Inference Engine](#13-skill-inference-engine)
14. [Scoring Algorithm — Full Mathematics](#14-scoring-algorithm--full-mathematics)
15. [Feedback Generation System](#15-feedback-generation-system)
16. [Background Processing & Async Scoring](#16-background-processing--async-scoring)
17. [API Endpoints Reference](#17-api-endpoints-reference)
18. [Email Notification System](#18-email-notification-system)
19. [Admin Panel & Role Management](#19-admin-panel--role-management)
20. [Testing Strategy](#20-testing-strategy)
21. [Deployment & DevOps](#21-deployment--devops)
22. [Panel Question Bank — With Answers](#22-panel-question-bank--with-answers)
23. [Demo Script for Presentation Day](#23-demo-script-for-presentation-day)
24. [Quick Reference Cheat Sheet](#24-quick-reference-cheat-sheet)

---

## 1. 30-Second Elevator Pitch

> "Our project is an **AI-Powered Recruitment Assistant** — a web platform where recruiters post jobs and candidates upload resumes. The system automatically **extracts text** from PDF/DOCX files, **validates** that the document is actually a resume, **parses** skills and experience, and **scores** each candidate against the job using a **hybrid AI approach**: keyword matching, **semantic similarity** via Sentence Transformers, experience detection, and format analysis. Scoring runs in a **background thread** so uploads are non-blocking. Recruiters see ranked candidates; candidates get **personalized feedback** on how to improve. The backend is **Flask with Blueprints**, secured with **CSRF, rate limiting, and role-based access control**."

---

## 2. Problem Statement & Objectives

### Problem
Manual resume screening is slow, subjective, and inconsistent. Recruiters spend hours reading hundreds of resumes. Candidates rarely get feedback on why they were rejected.

### Objectives (What We Built)
| # | Objective | How We Achieved It |
|---|-----------|-------------------|
| 1 | Automate resume screening | AI scoring pipeline in `ai/scorer.py` + `services/resume_service.py` |
| 2 | Rank candidates objectively | Weighted multi-factor score out of 100 |
| 3 | Give candidates actionable feedback | `ai/chatbot.py` + section-aware feedback |
| 4 | Secure multi-role platform | Recruiter / Candidate / Admin roles with isolation |
| 5 | Non-blocking user experience | Background threading for AI scoring |
| 6 | Production-ready architecture | Blueprints, CSRF, rate limits, tests, CI |

### SDLC Model Used
**Agile / Iterative** — we built in phases: prototype → security → blueprints → async scoring → admin → tests.

---

## 3. Scope & Limitations (Be Honest With Panel)

### In Scope
- Resume upload (PDF, DOCX, DOC)
- AI scoring and ranking
- Recruiter job management
- Candidate application tracking
- Admin user/job management
- Email notifications (optional SMTP)

### Out of Scope / Limitations (Say These Proactively)
| Limitation | Why | Future Work |
|------------|-----|-------------|
| English-only resumes | Regex + English NLP models | Multilingual BERT |
| No live video interview | FYP time constraint | Integrate Zoom API |
| In-memory rate limiter | Single-server dev setup | Redis in production |
| Thread-based background jobs | Simplicity for FYP | Celery + Redis queue |
| Semantic model loads on first use | ~90MB model download | Pre-warm on startup |
| SQLite default DB | Easy local dev | PostgreSQL in production |
| Skill inference is rule-based | Not deep learning | Train NER model on resumes |

**Panel loves when you admit limitations confidently.**

---

## 4. System Architecture

### High-Level Architecture

```
┌─────────────┐     HTTP/HTTPS      ┌──────────────────────────────────────┐
│   Browser   │ ◄─────────────────► │           Flask Application           │
│ (Bootstrap) │                     │  ┌─────────┐  ┌─────────────────────┐  │
└─────────────┘                     │  │Blueprints│  │     extensions.py   │  │
                                    │  │ auth     │  │ CSRF | Limiter | Mail│  │
                                    │  │ recruiter│  └─────────────────────┘  │
                                    │  │ candidate│                            │
                                    │  │ api      │  ┌─────────────────────┐  │
                                    │  │ admin    │  │   SQLAlchemy ORM    │  │
                                    │  └─────────┘  │   (SQLite / PG)     │  │
                                    │               └─────────────────────┘  │
                                    │  ┌─────────────────────────────────┐  │
                                    │  │      AI Module (ai/)             │  │
                                    │  │ parser → detector → inference   │  │
                                    │  │         → scorer → feedback      │  │
                                    │  └─────────────────────────────────┘  │
                                    └──────────────────────────────────────┘
                                              │
                                    ┌─────────▼─────────┐
                                    │  instance/uploads/  │
                                    │  (resume files)     │
                                    └───────────────────┘
```

### Application Factory Pattern
`app.py` uses the **Factory Pattern** — `create_app()` builds the Flask app, registers extensions and blueprints. This allows:
- Multiple configs (dev/test/prod)
- pytest to override `TESTING=True` with in-memory SQLite

### Blueprint Routing
| Blueprint | URL Prefix | Role |
|-----------|------------|------|
| `auth` | `/` | Public — login, signup, logout, index |
| `recruiter` | `/recruiter` | Recruiter only |
| `candidate` | `/candidate` | Candidate only |
| `api` | `/api` | JSON endpoints (authenticated) |
| `admin` | `/admin` | Admin only |

---

## 5. Technology Stack — Why We Chose Each

| Technology | Purpose | Why This Choice |
|------------|---------|-----------------|
| **Flask** | Web framework | Lightweight, flexible, ideal for FYP; easy Blueprint organization |
| **SQLAlchemy** | ORM | Database-agnostic; type-safe queries; migrations |
| **Flask-WTF** | CSRF protection | Industry standard for form security |
| **Flask-Limiter** | Rate limiting | Prevents brute-force login and upload spam |
| **Flask-Mail** | Email notifications | Notify candidates of status changes |
| **PyMuPDF (fitz)** | PDF text extraction | Fast, accurate for text-based PDFs |
| **pytesseract** | OCR fallback | Handles scanned/image PDFs |
| **SentenceTransformers** | Semantic similarity | `all-MiniLM-L6-v2` — 384-dim embeddings, fast inference |
| **scikit-learn** | Resume detector ML | TF-IDF + classifier for resume vs non-resume |
| **bleach** | Input sanitization | Strips XSS from user inputs |
| **Bootstrap 5** | Frontend UI | Responsive, professional look |
| **pytest** | Testing | 25 automated tests |
| **gunicorn** | Production server | Multi-worker WSGI deployment |

---

## 6. Project Folder Structure

```
ZEESHAN FYP/
├── app.py                  # Application factory (create_app)
├── config.py               # Environment-based configuration
├── extensions.py           # CSRF, Limiter, Mail — initialized once
├── models.py               # User, JobPosting, ResumeSubmission
├── app_helpers.py          # clean_text(), CSV sanitization, DB patches
├── blueprints/
│   ├── auth.py             # Login, signup, logout, index
│   ├── recruiter.py        # Jobs, reports, candidate status
│   ├── candidate.py        # Dashboard, upload, profile
│   ├── api.py              # JSON polling endpoints
│   ├── admin.py            # Platform administration
│   └── auth_utils.py       # @login_required, @role_required
├── ai/
│   ├── parser.py           # Text extraction + resume parsing
│   ├── resume_detector.py  # ML + rule-based resume validation
│   ├── skill_inference.py  # Infer skills from context
│   ├── scorer.py           # Multi-factor scoring (THE CORE)
│   ├── chatbot.py          # Feedback generation
│   └── section_feedback.py # Section-aware feedback
├── services/
│   ├── resume_service.py   # Upload, background scoring orchestration
│   └── email_service.py    # Async status emails
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS, JavaScript
├── tests/                  # pytest test suite
└── migrations/             # Alembic database migrations
```

---

## 7. Database Design (ER Model)

### Entity Relationship

```
User (1) ──────< (N) JobPosting        [recruiter posts jobs]
User (1) ──────< (N) ResumeSubmission  [candidate applies]
JobPosting (1) ──< (N) ResumeSubmission [one job, many applicants]

UNIQUE CONSTRAINT: (candidate_id, job_id) — one application per job per candidate
```

### Table: `users`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| email | VARCHAR(120) UNIQUE | Login username |
| password_hash | VARCHAR(256) | Werkzeug hashed password (never plain text) |
| role | VARCHAR(20) | `recruiter`, `candidate`, or `admin` |
| is_active | BOOLEAN | Admin can deactivate accounts |
| created_at | DATETIME | Registration timestamp |

### Table: `job_postings`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | |
| title, description | VARCHAR/TEXT | Job details |
| required_skills | TEXT | Comma-separated skills for AI scoring |
| recruiter_id | FK → users | Owner isolation |
| job_type, work_mode | VARCHAR | Full-time, Remote, etc. |
| company_name, location | VARCHAR | Display fields |
| salary_range | VARCHAR | Optional |
| expires_at | DATETIME | Application deadline |
| is_active | BOOLEAN | Recruiter can close job |

### Table: `resume_submissions`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | |
| candidate_id | FK → users | Who applied |
| job_id | FK → job_postings | Which job |
| file_path | VARCHAR | Path to uploaded file |
| score | FLOAT | Final score 0–100 |
| keyword_score | FLOAT | Max 40 |
| semantic_score | FLOAT | Max 35 |
| experience_score | FLOAT | Max 15 |
| format_score | FLOAT | Max 10 |
| scoring_status | VARCHAR | `processing` → `scored` → `failed` |
| status | VARCHAR | Recruiter decision: pending/shortlisted/rejected/selected |
| explanation | JSON | Full AI breakdown + feedback |
| parsed_summary | JSON | Extracted skills, education, experience |
| inferred_skills | JSON | Skills inferred from context |
| explicit_skills | JSON | Skills listed directly on resume |

---

## 8. Complete Request Flow — End to End

### Flow A: Candidate Uploads Resume

```
1. Candidate fills form + selects PDF → POST /candidate/upload/<job_id>
2. @role_required("candidate") checks session role
3. @limiter.limit("5 per minute") prevents spam
4. Duplicate check: UNIQUE(candidate_id, job_id)
5. Job active check: is_active=True AND not expired
6. handle_upload() → save file, validate MIME type
7. create_pending_submission() → DB row with scoring_status="processing"
8. start_background_scoring() → daemon thread spawned
9. HTTP response returns IMMEDIATELY → "Scoring in progress..."
10. Background thread:
    a. extract_text(file)           → ai/parser.py
    b. validate_resume_document()   → ai/resume_detector.py
    c. parse_resume(text)           → ai/parser.py
    d. combine_explicit_and_inferred_skills() → ai/skill_inference.py
    e. score_candidate(profile, job) → ai/scorer.py
    f. generate_feedback()          → ai/chatbot.py
    g. Update DB: score, explanation, scoring_status="scored"
11. Frontend polls GET /api/submission/<id>/status every 3 seconds
12. UI updates score badge when scoring_status="scored"
```

### Flow B: Recruiter Changes Candidate Status

```
1. Recruiter clicks Shortlist → POST /recruiter/candidate/<id>/status
2. JSON body: {"status": "shortlisted"}
3. Verify job belongs to this recruiter (user isolation)
4. Update submission.status in DB
5. notify_candidate() → async email thread (if MAIL_USERNAME configured)
6. Return JSON {"success": true, "status": "shortlisted"}
```

---

## 9. Authentication, Security & Authorization

### Password Storage
- Passwords are **never stored in plain text**
- `werkzeug.security.generate_password_hash()` → bcrypt-based hash
- Login: `check_password_hash(stored_hash, entered_password)`

### Password Policy (`utils/auth_utils.py`)
- Minimum **8 characters**
- At least **1 uppercase letter**
- At least **1 number**

### Session Management
- Flask server-side sessions (signed cookie with `SECRET_KEY`)
- `SESSION_COOKIE_HTTPONLY = True` — JavaScript cannot read session cookie
- `SESSION_COOKIE_SAMESITE = "Lax"` — CSRF mitigation
- `SESSION_COOKIE_SECURE = True` in production — HTTPS only

### CSRF Protection
- Every `<form method="POST">` includes `{{ csrf_token() }}`
- AJAX POSTs send header `X-CSRFToken`
- Flask-WTF validates token on every POST

### Rate Limiting
| Route | Limit |
|-------|-------|
| POST /login | 10 per minute |
| POST /signup | 20 per hour |
| POST /candidate/upload | 5 per minute |
| Global default | 200/day, 50/hour |

### Role-Based Access Control
```python
@role_required("recruiter")  # Only recruiters
@role_required("candidate")  # Only candidates
@role_required("admin")      # Only admins
@login_required              # Any logged-in user
```

### User Isolation (Critical for Panel)
- Recruiter can ONLY see jobs where `recruiter_id == session["user_id"]`
- Candidate can ONLY download their own submissions
- API checks ownership before returning submission data
- Admin sees everything (by design)

---

## 10. AI Pipeline — Step by Step

The AI pipeline runs inside `services/resume_service.py → process_resume()`:

```
Upload File
    │
    ▼
[1] extract_text()          ← ai/parser.py (PyMuPDF → OCR fallback)
    │
    ▼
[2] validate_resume_document() ← ai/resume_detector.py (ML or rules)
    │
    ▼
[3] parse_resume()          ← ai/parser.py (regex extraction)
    │
    ▼
[4] combine_explicit_and_inferred_skills() ← ai/skill_inference.py
    │
    ▼
[5] score_candidate()       ← ai/scorer.py (MATHEMATICAL SCORING)
    │
    ▼
[6] generate_feedback()     ← ai/chatbot.py (personalized advice)
    │
    ▼
Save to DB: score, explanation, skills, scoring_status="scored"
```

---

## 11. Resume Text Extraction (Parser)

**File:** `ai/parser.py`

### PDF Extraction Strategy (Two-Tier)
1. **Primary:** PyMuPDF (`fitz`) — extracts embedded text from PDF
   - Fast, accurate for digital/text-based PDFs
   - Requires > 50 characters to consider successful
2. **Fallback:** OCR via Tesseract + pdf2image
   - Converts PDF pages to 300 DPI images
   - Runs `pytesseract.image_to_string()` on each page
   - Used for scanned/image-based PDFs

### DOCX Extraction
- Uses `docx2txt` library
- Extracts plain text from Word documents

### Parsed Fields (`parse_resume()`)
| Field | Extraction Method |
|-------|-------------------|
| skills | Regex: `skills?:\s*(.*)` |
| education | Regex: bachelor/master/ph.d patterns |
| experiences | Regex: developer/engineer/analyst patterns |
| years_experience | Regex: `(\d+)\s*years?` patterns |
| raw_text | First 2000 characters stored |

---

## 12. Resume Detection Model

**File:** `ai/resume_detector.py`

**Purpose:** Reject non-resume uploads (random PDFs, invoices, etc.)

### Method 1: Trained ML Model (Primary)
If `training/models/resume_detector.pkl` exists:

**Features extracted:**
- Document length, word count
- Has email (`@` present)
- Has skills/experience/education sections
- Job title count (engineer, developer)
- Number count in text

**Combined with TF-IDF vectorization** of full text → fed to scikit-learn classifier

**Output:** `predict_proba()` → confidence score 0–1

### Method 2: Rule-Based Fallback
If ML model not available, weighted keyword scoring:

| Category | Weight | Keywords |
|----------|--------|----------|
| experience | 0.25 | experience, employment, career |
| education | 0.20 | education, degree, university |
| skills | 0.20 | skills, competencies, expertise |
| contact | 0.15 | email, phone, linkedin |
| personal | 0.10 | objective, summary, profile |
| achievements | 0.10 | awards, certifications, projects |

**Bonus signals:** dates (YYYY pattern), job titles, email regex, phone regex, LinkedIn/GitHub

**Decision rule:**
```
is_resume = (confidence >= 0.4) AND (keyword_categories_found >= 3)
```

---

## 13. Skill Inference Engine

**File:** `ai/skill_inference.py`

**Problem:** Candidates list "Built REST APIs using Django" but don't list "Python" or "REST API" in skills section.

**Solution:** Context-based skill inference using pattern dictionary.

### How It Works
1. Scan resume text for **context keywords** (e.g., "machine learning", "backend", "devops")
2. Each context maps to **likely skills** (e.g., "machine learning" → python, tensorflow, pandas)
3. Check 50-character window around match for skill-related terms
4. Also scan project descriptions: "built X using Y" patterns
5. Combine explicit + inferred skills (no duplicates)

**Example:**
```
Resume text: "Developed microservices using Docker and Kubernetes"
Explicit skills: []
Inferred skills: ["docker", "kubernetes", "microservices"]
```

This improves keyword matching score because inferred skills are included in profile.

---

## 14. Scoring Algorithm — Full Mathematics

**File:** `ai/scorer.py` — **THIS IS THE MOST IMPORTANT SECTION FOR PANEL**

### Overview: Weighted Multi-Factor Scoring

```
Total Score = min(100, Keyword + Semantic + Experience + Format)
Total Score = apply_length_regularization(Total Score, resume_text)
```

Maximum possible breakdown:
| Component | Max Points | Weight |
|-----------|------------|--------|
| Keyword Match | 40 | 40% |
| Semantic Similarity | 35 | 35% |
| Experience | 15 | 15% |
| Format/Structure | 10 | 10% |
| **Total** | **100** | **100%** |

---

### Component 1: Keyword Score (Max 40 points)

**Purpose:** Check if required skills appear in resume text.

**Formula:**

```
For each required skill sᵢ:
  category = SKILL_CATEGORIES[sᵢ]  (e.g., "python" → "programming")
  weight wᵢ = SKILL_WEIGHTS[category]  (programming=1.2, soft_skills=0.8)

  if sᵢ found in resume_text (case-insensitive substring):
    matched_weight += wᵢ
  total_weight += wᵢ

raw_ratio = matched_weight / total_weight

keyword_score = min(40, raw_ratio × 40)
```

**Skill Category Weights:**
| Category | Weight | Example Skills |
|----------|--------|----------------|
| programming | 1.2 | Python, Java, C++ |
| frameworks | 1.1 | Django, Flask, React |
| tools | 1.0 | Git, Docker, AWS |
| domain | 1.0 | Machine Learning, Finance |
| education | 0.9 | (education category) |
| soft_skills | 0.8 | Communication, Leadership |

**Example:**
```
Required: Python, Django, Docker
Resume contains: Python, Django (not Docker)

Python: programming, weight=1.2 → MATCHED
Django: frameworks, weight=1.1 → MATCHED
Docker: tools, weight=1.0 → NOT MATCHED

matched_weight = 1.2 + 1.1 = 2.3
total_weight = 1.2 + 1.1 + 1.0 = 3.3
raw_ratio = 2.3 / 3.3 = 0.697
keyword_score = 0.697 × 40 = 27.9 points
```

---

### Component 2: Semantic Score (Max 35 points)

**Purpose:** Measure meaning-level similarity between resume and job description (not just keywords).

**Model:** `SentenceTransformer("all-MiniLM-L6-v2")`
- Converts text to **384-dimensional dense vectors** (embeddings)
- Based on MiniLM — distilled BERT, optimized for semantic similarity
- Pre-trained on 1B+ sentence pairs

**Step 1: Generate Embeddings**
```
emb_resume = model.encode(resume_text)   → vector ∈ ℝ³⁸⁴
emb_job    = model.encode(job_description) → vector ∈ ℝ³⁸⁴
```

**Step 2: Cosine Similarity**
```
                emb_resume · emb_job
cos_sim = ─────────────────────────────────
          ‖emb_resume‖ × ‖emb_job‖
```

Cosine similarity range: **[-1, 1]**, typically [0, 1] for similar documents.

**Step 3: Temperature Scaling (Sigmoid)**
```
                1
scaled = ─────────────────────────────
         1 + e^(-(cos_sim / T) × 10)

where T = 1.5 (temperature parameter)
```

This sigmoid **spreads** the similarity scores — low similarities stay low, high similarities get boosted.

**Step 4: Scale to 35 points**
```
semantic_score = scaled × 35
```

**Fallback (if SentenceTransformers unavailable):**
```
overlap = |resume_words ∩ job_words| / |job_words|
semantic_score = min(35, overlap × 35)
```

**Why cosine similarity?**
Panel may ask: "Why not Euclidean distance?"
> "Cosine similarity measures **angle** between vectors, not magnitude. Two documents about Python programming will point in similar directions in embedding space regardless of document length. Euclidean distance is biased by document length."

---

### Component 3: Experience Score (Max 15 points)

**Purpose:** Reward candidates with relevant years of experience.

**Detection:** Regex patterns on resume text:
```
(\d+)\+?\s*years?\s*of\s*experience
(\d+)\+?\s*yrs?\s*experience
experience\s*of\s+(\d+)\+?\s*years?
```

**Scoring tiers:**
| Years Found | Points |
|-------------|--------|
| ≥ 8 years | 15.0 |
| ≥ 5 years | 10.0 |
| ≥ 3 years | 7.0 |
| ≥ 1 year | 4.0 |
| 0 years | 0.0 |

Takes the **maximum** year value found across all patterns.

---

### Component 4: Format Score (Max 10 points)

**Purpose:** Reward well-structured resumes.

| Condition | Points |
|-----------|--------|
| Contains "education", "degree", or "university" | +3 |
| Contains "experience", "worked", or "employment" | +3 |
| Contains "skill", "proficient", or "expertise" | +2 |
| Has email (@) AND contact info (phone/mobile) | +2 |

Maximum: 10 points

---

### Component 5: Length Regularization

**Purpose:** Penalize suspiciously short resumes (likely incomplete).

```
word_count = len(resume_text.split())

if word_count < 100:
    final_score = score × 0.85   (15% penalty)
else:
    final_score = score
```

---

### Final Score Calculation — Complete Example

```
Resume: "Python developer with 5 years experience..."
Job required skills: Python, Flask, SQL
Job description: "Looking for backend developer..."

keyword_score    = 32.0  (Python+Flask matched, SQL missing)
semantic_score   = 24.5  (good semantic alignment)
experience_score = 10.0  (5 years detected)
format_score     = 8.0   (has education, experience, skills sections)

raw_total = 32.0 + 24.5 + 10.0 + 8.0 = 74.5
word_count = 450 (> 100, no penalty)

FINAL SCORE = 74.5 / 100
```

### Skill Gap Detection
```
missing_skills = [s for s in required_skills if s not in resume_text.lower()]
```
Returned in scoring result for feedback generation.

### Percentage Metrics (for UI display)
```
skill_match      = (keyword_score / 40) × 100
experience_match = (experience_score / 15) × 100
keyword_match    = (semantic_score / 35) × 100
```

---

## 15. Feedback Generation System

**File:** `ai/chatbot.py`

After scoring, the system generates **personalized feedback** based on:
- Overall score
- Semantic score vs keyword score gaps
- Missing skills list
- Section-aware analysis (`section_feedback.py`)

**Feedback structure:**
1. Overall Assessment (2 sentences)
2. Top 3 Missing Skills with learning plans
3. What You Did Well (strengths)
4. Recommended Next Steps (actionable)

**Validation:** `feedback_validator.py` ensures feedback references only skills actually in/missing from the resume (prevents hallucination).

---

## 16. Background Processing & Async Scoring

### Why Background Threading?
AI scoring takes **5–30 seconds** (model loading + inference). Blocking the HTTP request would freeze the browser.

### Implementation (`services/resume_service.py`)
```python
thread = threading.Thread(
    target=score_in_background,
    args=(app, submission_id, file_path, job_id),
    daemon=True  # dies when main process exits
)
thread.start()
# HTTP response returns immediately
```

### Critical: Flask App Context
Background threads don't have Flask context by default. We wrap all DB operations:
```python
with app.app_context():
    submission = db.session.get(ResumeSubmission, submission_id)
    process_resume(...)
    db.session.commit()
```

### Scoring Status State Machine
```
pending → processing → scored
                    ↘ failed (on exception)
```

### Frontend Polling
JavaScript on candidate dashboard polls every 3 seconds:
```javascript
fetch('/api/submission/' + id + '/status')
  .then(data => {
    if (data.scoring_status === 'scored') updateScoreBadge(data.score)
  })
```

---

## 17. API Endpoints Reference

| Method | URL | Auth | Returns |
|--------|-----|------|---------|
| GET | `/api/job/<id>/submissions` | Recruiter | JSON list of submissions |
| GET | `/api/submission/<id>/status` | Login | `{scoring_status, score, status}` |
| GET | `/api/submission/<id>/breakdown` | Login | Full score breakdown JSON |

---

## 18. Email Notification System

**File:** `services/email_service.py`

Triggered when recruiter changes status to:
- `shortlisted` → "Congratulations! You've been shortlisted."
- `selected` → "Great news! You've been selected."
- `rejected` → "Thank you for applying..."

Sent **asynchronously** in background thread. Skipped if `MAIL_USERNAME` not configured.

---

## 19. Admin Panel & Role Management

**Routes:** `/admin/dashboard`, `/admin/users`, `/admin/jobs`

| Action | Description |
|--------|-------------|
| View stats | Total users, jobs, submissions, avg score |
| Toggle user | Activate/deactivate accounts |
| Remove job | Delete job posting from platform |

Admin cannot deactivate other admin accounts.

---

## 20. Testing Strategy

**25 tests** in `tests/` using pytest + Flask test client.

| Test File | What It Tests |
|-----------|---------------|
| test_auth.py | Login, signup, rate limiting, password validation |
| test_candidate.py | Duplicate submission, expired/closed jobs, access control |
| test_recruiter.py | Job creation, recruiter isolation on reports |
| test_api.py | API auth, candidate isolation on submission status |
| test_security.py | Deactivated users, XSS sanitization |
| test_models.py | as_dict(), unique constraint |
| test_ai_scorer.py | Score range 0–100, empty resume handling |
| test_ai_parser.py | Parser returns expected keys |

Tests use **in-memory SQLite** — never touch production database.
CSRF disabled in tests (`WTF_CSRF_ENABLED=False`) for simpler POST testing.

---

## 21. Deployment & DevOps

### Local Development
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
flask db upgrade
flask run
```

### Production (gunicorn)
```
web: gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT
```

### CI Pipeline (`.github/workflows/ci.yml`)
- Runs on push to main/develop
- Installs dependencies + system OCR tools
- Runs `pytest tests/ -v`
- Checks for hardcoded `debug=True` and demo credentials

### Environment Variables (Production Checklist)
- [ ] `SECRET_KEY` — strong random 64-char string
- [ ] `FLASK_ENV=production`
- [ ] `SEED_DEMO_USERS=false`
- [ ] `DATABASE_URL` — PostgreSQL recommended
- [ ] `MAIL_USERNAME` / `MAIL_PASSWORD` — for email notifications

---

## 22. Panel Question Bank — With Answers

### Project Overview Questions

**Q: What is your project about?**
> An AI-powered web platform that automates resume screening. Recruiters post jobs; candidates upload resumes; the system scores and ranks candidates using NLP and machine learning, providing feedback to both parties.

**Q: What problem does it solve?**
> Manual resume screening is time-consuming and biased. Our system provides consistent, explainable, multi-factor scoring in seconds instead of hours.

**Q: Who are the users?**
> Three roles: **Candidates** (apply and get feedback), **Recruiters** (post jobs and review ranked candidates), **Admins** (manage platform users and jobs).

**Q: Why Flask and not Django?**
> Flask is lightweight and modular — ideal for our Blueprint-based architecture. Django would add unnecessary overhead for our focused feature set. Flask gives us full control over the AI pipeline integration.

---

### AI / ML Questions

**Q: Explain your scoring algorithm.**
> We use a weighted multi-factor model scoring out of 100: Keyword matching (40%), semantic similarity using Sentence Transformers (35%), experience detection (15%), and resume format quality (10%). Each component addresses a different dimension of candidate-job fit.

**Q: What ML models did you use?**
> 1. **SentenceTransformer `all-MiniLM-L6-v2`** — 384-dimensional semantic embeddings for resume-job similarity via cosine similarity.
> 2. **scikit-learn classifier** — TF-IDF + handcrafted features for resume vs non-resume detection.
> 3. **Rule-based skill inference** — pattern dictionary mapping context keywords to likely skills.

**Q: What is cosine similarity? Why use it?**
> Cosine similarity measures the angle between two vectors: `cos(θ) = (A·B) / (‖A‖×‖B‖)`. Values near 1 mean similar direction (similar meaning). We use it because embedding vectors represent semantic meaning — two texts about Python development will have similar vectors regardless of length.

**Q: What is Sentence Transformers / all-MiniLM-L6-v2?**
> A pre-trained neural network that converts sentences into 384-dimensional dense vectors capturing semantic meaning. MiniLM is a distilled version of BERT — smaller and faster while retaining ~95% of BERT's accuracy on similarity tasks. We use it because it's state-of-the-art for semantic text similarity without needing GPU.

**Q: Why not use ChatGPT/GPT-4 for scoring?**
> 1. Cost — API calls per resume add up
> 2. Latency — network round-trip vs local inference
> 3. Explainability — our weighted formula gives transparent breakdown; GPT is a black box
> 4. Privacy — resumes contain PII; local processing is safer
> 5. FYP scope — demonstrates our own algorithm design

**Q: How do you handle scanned PDFs?**
> Two-tier extraction: PyMuPDF first (fast, for digital PDFs). If text < 50 chars, fallback to OCR: pdf2image converts pages to 300 DPI images, Tesseract extracts text.

**Q: How do you prevent non-resume uploads?**
> Resume detection layer: ML classifier (TF-IDF + features) if model file exists, else rule-based scoring of resume-specific keywords (experience, education, skills sections). Rejects documents below 0.4 confidence with fewer than 3 keyword categories.

**Q: What is skill inference?**
> Candidates often describe skills in project descriptions without listing them explicitly. Our inference engine scans for context keywords ("built microservices using Docker") and infers related skills (Docker, Kubernetes, REST API) using a pattern dictionary of 50+ technology mappings.

**Q: How accurate is your scoring?**
> Scoring is heuristic + ML-based, not ground-truth validated. Keyword and semantic components are complementary — keywords catch exact skill matches, semantics catch related experience. We provide score breakdown so recruiters can judge themselves. For production, we'd validate against human recruiter ratings.

---

### Backend / Architecture Questions

**Q: Explain your system architecture.**
> Three-tier: Presentation (Bootstrap templates + JS polling), Application (Flask Blueprints + services), Data (SQLAlchemy ORM + SQLite/PostgreSQL). AI module is a separate Python package (`ai/`) called by the service layer.

**Q: What is the Application Factory pattern?**
> `create_app()` in app.py builds and configures the Flask app. Benefits: testability (pytest passes config overrides), multiple environments (dev/test/prod), lazy initialization of extensions.

**Q: What are Blueprints?**
> Flask Blueprints modularize routes by feature. We have 5: auth, recruiter, candidate, api, admin. Each has its own file, URL prefix, and templates. Enables team development and clean separation of concerns.

**Q: How does authentication work?**
> Session-based auth. On login: verify password hash → store user_id and role in Flask session (signed cookie). `@role_required` decorator checks session on every protected route. Passwords hashed with Werkzeug (bcrypt).

**Q: How do you prevent CSRF attacks?**
> Flask-WTF CSRFProtect generates a token per session. Every POST form includes hidden `csrf_token` field. AJAX requests send `X-CSRFToken` header. Server rejects POSTs without valid token.

**Q: How does background scoring work?**
> Upload creates DB record with `scoring_status=processing`, spawns daemon thread with Flask app context, thread runs full AI pipeline, updates DB with score and `scoring_status=scored`. Frontend polls API every 3 seconds for status update.

**Q: Why threading and not Celery?**
> Threading is simpler for FYP scope — no Redis/RabbitMQ dependency. Trade-off: threads don't survive server restart and don't scale across machines. Production would use Celery task queue.

**Q: Explain the database schema.**
> Three main tables: User (auth), JobPosting (recruiter's jobs), ResumeSubmission (applications with scores). Foreign keys link them. Unique constraint on (candidate_id, job_id) prevents duplicate applications.

---

### Security Questions

**Q: How do you protect user data?**
> Role-based access control, user isolation (recruiters see only their jobs), password hashing, CSRF tokens, rate limiting, input sanitization with bleach, HTTPOnly session cookies, file type validation (MIME check).

**Q: Can one candidate see another's submission?**
> No. API and download routes check `submission.candidate_id == session["user_id"]`. Returns 403 if unauthorized.

**Q: Can one recruiter see another's candidates?**
> No. All recruiter queries filter by `recruiter_id == session["user_id"]`. Report download returns 404 for other recruiters' jobs.

---

### Testing Questions

**Q: How did you test the system?**
> 25 automated pytest tests covering authentication, authorization boundaries, duplicate submission prevention, API isolation, XSS sanitization, model constraints, and AI scorer output range. CI runs tests on every GitHub push.

**Q: How do you test without a real database?**
> pytest fixture creates app with `SQLALCHEMY_DATABASE_URI: "sqlite://"` (in-memory). Database created and dropped per test session.

---

### Limitations & Future Work Questions

**Q: What are the limitations?**
> English-only, thread-based background jobs, in-memory rate limiter, no mobile app, skill inference is rule-based not ML, semantic model requires first-load download, SQLite not ideal for high concurrency.

**Q: What would you add next?**
> Celery task queue, Redis rate limiter, PostgreSQL, multilingual support, fine-tuned BERT for resume parsing, interview scheduling module, analytics dashboard with ML insights.

---

## 23. Demo Script for Presentation Day

### Step 1: Show Landing Page (30 sec)
"This is the landing page. Three user roles: candidate, recruiter, admin."

### Step 2: Login as Recruiter (1 min)
```
Email: recruiter@example.com
Password: recruiter123
```
"Recruiter dashboard shows all posted jobs and ranked candidates."

### Step 3: Create a Job (1 min)
- Title: "Python Developer"
- Skills: "Python, Flask, SQL, REST API"
- Description: "Build backend APIs for recruitment platform"
"Skills field directly feeds the AI keyword scorer."

### Step 4: Login as Candidate (1 min)
```
Email: candidate@example.com
Password: candidate123
```
"Candidate sees active jobs, can search and filter."

### Step 5: Upload Resume (2 min)
- Upload a PDF resume
- Point out: "Upload returns immediately — scoring in background"
- Watch score badge update via polling (3 sec intervals)
"System extracted text, validated resume, scored against job, generated feedback."

### Step 6: Show Score Breakdown (1 min)
- Click "View Feedback"
- Show: skill match %, semantic analysis, missing skills, rationale

### Step 7: Recruiter Reviews (1 min)
- Login as recruiter
- Show ranked candidates table
- Change status to "Shortlisted"
- Mention email notification sent

### Step 8: Show Architecture Diagram (1 min)
Walk through architecture from Section 4 of this guide.

### Step 9: Show Code — Scorer (2 min)
Open `ai/scorer.py` — explain the 4 scoring components and formula.

---

## 24. Quick Reference Cheat Sheet

### Score Formula (Memorize This)
```
Total = Keyword(40) + Semantic(35) + Experience(15) + Format(10)
If words < 100: Total × 0.85
Final = min(100, Total)
```

### Key Files (Memorize)
| File | One Line |
|------|----------|
| `ai/scorer.py` | Scoring math |
| `ai/parser.py` | Text extraction |
| `ai/resume_detector.py` | Resume validation |
| `ai/skill_inference.py` | Skill inference |
| `services/resume_service.py` | Pipeline orchestration |
| `models.py` | Database schema |
| `blueprints/candidate.py` | Upload route |
| `extensions.py` | CSRF + Limiter + Mail |

### Tech Stack One-Liner
Flask + SQLAlchemy + SentenceTransformers + scikit-learn + Bootstrap 5

### Demo Accounts
| Role | Email | Password |
|------|-------|----------|
| Recruiter | recruiter@example.com | recruiter123 |
| Candidate | candidate@example.com | candidate123 |
| Admin | admin@example.com | admin123 |

### Run Commands
```powershell
.\.venv\Scripts\Activate.ps1
flask run
pytest tests/ -v
```

---

*End of FYP Panel Guide. Read Sections 14, 22, and 24 twice before your viva.*
