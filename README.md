# 🗂️ FMS Django Backend

A production-ready **Django REST API** that powers the FMS League of Legends portfolio site.  
Handles authentication, player & match data, tournament statistics, content management and integrates with **Riot Games**, **Leaguepedia** and **Pandascore** APIs.

---

## 🚀 Live API
```bash
https://api.fms-project.fun
```

---

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [API Overview](#-api-overview)
- [Authentication & Permissions](#-authentication--permissions)
- [Caching & Performance](#-caching--performance)
- [Deployment Notes](#-deployment-notes)

---

## ✨ Features
| Domain | Highlights |
|--------|------------|
| **Authentication** | JWT access tokens + CSRF cookies, role-based access (USER / EDITOR / ADMIN) |
| **Player Data** | CRUD for players, summoners, ranks, social links |
| **Match Stats** | Solo-queue matches from Riot API, official tournament stats from Leaguepedia |
| **Content** | Markdown blog posts, newsletter subscriptions |
| **External APIs** | Auto-sync with Riot, Leaguepedia & Pandascore |
| **Admin Panel** | Rich Django-admin with inline editing |
| **Caching** | Redis-backed caching for heavy stats endpoints |
| **Security** | CSP, HSTS, rate-limiting, secure cookies |

---

## 🛠 Tech Stack
| Layer | Technology |
|-------|------------|
| Framework | Django 5.2 + Django REST Framework |
| Database | PostgreSQL (with SSL) |
| Cache | Upstash Redis (prod) / LocMem (dev) |
| Auth | djangorestframework-simplejwt |
| Security | django-cors-headers, custom middleware |
| External | `requests`, `mwrogue`, `bleach`, `python-dotenv` |
| WSGI | Gunicorn + WhiteNoise |

---

## 🏗 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/your-username/fms-django-backend.git
cd fms-django-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment
Copy `.env.example` → `.env` and fill:

```env
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
DB_NAME=fms_db
DB_USER=fms_user
DB_PASSWORD=pass
DB_HOST=localhost
RIOT_API_KEY=RGAPI-xxxxxxxxxxxx
PANDASCORE_API_KEY=xxxxxxxxxxxx
UPSTASH_REDIS_REST_URL=https://your-upstash-url
```

### 3. Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run
```bash
python manage.py runserver
```
API now available at `http://localhost:8000/api/`

---

## 📁 Project Structure
```
FMS_Django_Init/
├── FMS_Django_App/
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       ├── fetch_matches.py
│   │       ├── fetch_player_stats.py
│   │       └── fetch_puuids.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── authentication.py
│   └── middleware.py
├── FMS_Django_Init/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt
└── manage.py
```

---

## 🔐 Environment Variables
| Variable | Purpose |
|----------|---------|
| `DEBUG` | Toggle dev vs prod settings |
| `DJANGO_SECRET_KEY` | Django signing key |
| `DATABASE_URL` | **Optional** Render/Supabase connection string |
| `RIOT_API_KEY` | Fetch solo-queue matches & ranks |
| `PANDASCORE_API_KEY` | Official tournament matches |
| `UPSTASH_REDIS_REST_URL` | Redis cache (prod) |

---

## ⚙️ Management Commands
Run these periodically (cron / GitHub Actions):

| Command | Description |
|---------|-------------|
| `python manage.py fetch_puuids` | Resolve Riot PUUIDs for all stored `riot_id`s |
| `python manage.py fetch_matches` | Pull latest 20 solo-queue matches per summoner |
| `python manage.py fetch_player_stats <nick>` | Import official stats from Leaguepedia |

---

## 📡 API Overview
All endpoints live under `/api/`

### 🔑 Auth
```
POST /api/register/
POST /api/login/           → sets HttpOnly JWT cookie
POST /api/logout/          → clears cookie
GET  /api/me/              → current user info
```

### 👥 Users (Admin)
```
GET    /api/users/
POST   /api/users/create/
GET    /api/users/<nick>/
PUT    /api/users/<nick>/edit/
DELETE /api/users/<nick>/delete/
```

### 🎮 Players & Stats
```
GET /api/players/
GET /api/players/<nick>/
GET /api/players/<nick>/ranks/
GET /api/players/<nick>/matches/          (paginated)
GET /api/players/<nick>/official_stats/   (aggregated + paginated matches)
GET /api/players/<nick>/official_stats/options/  (filter values)
```

### 📝 Content
```
GET  /api/posts/
POST /api/posts/create/
PUT  /api/posts/<id>/edit/
DELETE /api/posts/<id>/delete/
POST /api/newsletter/
```

### 🏆 Official Matches
```
GET /api/officialmatches/?team_id=136773&status=not_started&page=1
```

---

## 🔐 Authentication & Permissions
| Role | Capabilities |
|------|--------------|
| **USER** | view public data, edit own profile |
| **EDITOR** | create/edit own posts |
| **ADMIN** | full CRUD on users, players, posts |

JWT is returned in **HttpOnly cookie** (`access_token`) and validated via custom `JWTAuthentication` class.

---

## 🚀 Caching & Performance
- **Redis** (Upstash) in production – 1 h TTL for stats, 2 h for filter options.  
- **LocMem** in development.  
- Cache keys include hashed filter strings to guarantee uniqueness.

---

## 🛡 Security Checklist
| Measure | Status |
|---------|--------|
| HTTPS redirect & HSTS | ✅ |
| CSP (strict in prod, relaxed in dev) | ✅ |
| Rate-limiting (DRF throttling scopes) | ✅ |
| Secure cookies (`Secure`, `HttpOnly`, `SameSite=Lax`) | ✅ |
| Password validation & bcrypt hashing | ✅ |
| Input sanitization (bleach) | ✅ |
| CORS credentials & trusted origins | ✅ |

---

## 📦 Deployment Notes
| Provider | Notes |
|----------|-------|
| **Render** | `DATABASE_URL` auto-injected, set `DEBUG=False`, `ALLOWED_HOSTS` includes `*.onrender.com` |
| **Upstash Redis** | Plug-and-play via `UPSTASH_REDIS_REST_URL` |
| **Static Files** | Served by WhiteNoise + Gunicorn |
| **Environment** | All secrets via Render dashboard |


---

## 📄 License
MIT © 2025

---

## Autor

**Igor Suchodolski**
- Email: [igor.suchodolskii@gmail.com](mailto:igor.suchodolskii@gmail.com)
- GitHub: [@m4jorskyy](https://github.com/m4jorskyy)
