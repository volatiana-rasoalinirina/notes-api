# Notes API

A production-ready REST API built with Django REST Framework, deployed on AWS with full CI/CD pipeline.

## Live API

- **Base URL:** `http://16.170.248.131:8000/api/` 
- **Interactive docs:** `http://16.170.248.131:8000/api/docs/`

> Note: IP may change if the EC2 instance is restarted.

## Architecture

```
Developer
    │
    │  git push
    ▼
GitHub Actions (CI/CD)
    │
    │  SSH deploy
    ▼
AWS EC2 (Docker + Django)
    │
    │  PostgreSQL connection
    ▼
AWS RDS (PostgreSQL)
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Django REST Framework |
| Database | PostgreSQL (AWS RDS) |
| Containerization | Docker, Docker Compose |
| Server | AWS EC2 (Ubuntu 24.04) |
| CI/CD | GitHub Actions |
| API Docs | drf-spectacular (Swagger UI) |

## Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/api/notes/` | List all notes |
| POST | `/api/notes/` | Create a note |
| GET | `/api/notes/{id}/` | Get a note |
| PATCH | `/api/notes/{id}/` | Update a note |
| DELETE | `/api/notes/{id}/` | Delete a note |

## Local Setup

**Prerequisites:** Python 3.11, Docker, PostgreSQL

**1. Clone the repo:**
```bash
git clone https://github.com/volatiana-rasoalinirina/notes-api.git
cd notes-api
```

**2. Create environment file:**
```bash
cp .env.example .env
```

Edit `.env` with your local values:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://postgres:password@localhost:5432/notesapi
ALLOWED_HOSTS=localhost,127.0.0.1
```

**3. Run with Docker:**
```bash
docker compose up
```

API is available at `http://localhost:8000/api/docs/`

**4. Run without Docker:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Deployment

Every push to `main` triggers automatic deployment via GitHub Actions:

1. GitHub Actions SSHs into EC2
2. Pulls latest code from GitHub
3. Restarts Docker containers

No manual server access needed.

## Environment Variables

| Variable | Description |
|---|---|
| `DEBUG` | Django debug mode (False in production) |
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | PostgreSQL connection string |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |

## Author

**Volatiana Rasoalinirina** — Backend Engineer · Python & Django REST Framework

- LinkedIn: [linkedin.com/in/volatianarasoalinirina-3721ab1a5](https://www.linkedin.com/in/volatianarasoalinirina-3721ab1a5)
- Email: volatiana.rasoalinirina.dev@gmail.com