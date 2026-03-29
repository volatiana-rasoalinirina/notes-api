# Notes API

A simple Django REST Framework API for managing notes. Built as a deployment learning project.

## Stack

- Python 3.11 / Django 4.2 / Django REST Framework
- PostgreSQL
- drf-spectacular (Swagger UI)
- django-environ
- coverage

## Local Setup

### 1. Prerequisites

- Python 3.11
- PostgreSQL running locally

### 2. Create the database

```bash
createdb notes_db
```

### 3. Clone and set up the environment

```bash
git clone <repo-url>
cd notes-api

python3.11 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY and DATABASE_URL
```

### 5. Run migrations and start the server

```bash
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://localhost:8000`.

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/notes/` | List all notes |
| POST | `/api/notes/` | Create a note |
| GET | `/api/notes/{id}/` | Retrieve a note |
| PATCH | `/api/notes/{id}/` | Update a note |
| DELETE | `/api/notes/{id}/` | Delete a note |

## Swagger UI

Interactive API docs available at:

```
http://localhost:8000/api/docs/
```

## Running Tests

```bash
coverage run manage.py test && coverage report
```

To view an HTML coverage report:

```bash
coverage html
open htmlcov/index.html
```
