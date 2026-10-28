# Healthcare Backend

A Django REST Framework API for JWT authentication, patients, doctors, and patient-doctor mappings. PostgreSQL is used by the application; the test profile uses an isolated in-memory SQLite database.

## Technology

- Python 3.10+
- Django 5.2
- Django REST Framework 3.16
- Simple JWT
- PostgreSQL with Psycopg 3
- `python-dotenv`

## Project structure

```text
accounts/               User model, registration, login, admin, and tests
config/                 Django settings, URLs, and WSGI/ASGI entry points
doctors/                Doctor model and authenticated CRUD API
mappings/               Patient-doctor association API
patients/               Owner-scoped patient CRUD API
postman/                Importable Postman collection and existing request files
manage.py
requirements.txt
.env.example
```

Each Django app includes its initial migration.

## Prerequisites

- Python 3.10 or newer
- PostgreSQL 13 or newer
- PowerShell

## Install and configure

Open PowerShell in the project directory:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` locally and set a unique `DJANGO_SECRET_KEY` and your PostgreSQL connection details. Do not commit `.env` or share its contents. Configure:

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Private Django signing key |
| `DJANGO_DEBUG` | `True` for local development; `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated trusted hostnames |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL role |
| `DB_PASSWORD` | PostgreSQL role password |
| `DB_HOST` | PostgreSQL server host |
| `DB_PORT` | PostgreSQL server port, normally `5432` |

The application does not fall back to SQLite for normal operation. `.env.example` contains placeholders only.

### PostgreSQL database setup

If you need to create a local role and database, connect as a PostgreSQL administrator and run:

```sql
CREATE ROLE healthcare_user WITH LOGIN PASSWORD 'replace-with-a-strong-password';
CREATE DATABASE healthcare_db OWNER healthcare_user;
```

Use the corresponding database values in `.env`. This is an example for a new local setup; it does not require changing an existing administrator password or resetting an existing database. For production, use a secret manager, set `DJANGO_DEBUG=False`, restrict `DJANGO_ALLOWED_HOSTS`, and use HTTPS.

## Migrate and start the server

With the virtual environment active and `.env` configured:

```powershell
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/`; the Django admin is at `/admin/`.

## Automated checks

Run the app check, test suite, and migration consistency check:

```powershell
python manage.py check
python manage.py test --settings=config.test_settings
python manage.py makemigrations --check --dry-run --settings=config.test_settings
```

`config.test_settings` uses an in-memory SQLite database, so these checks do not modify the development PostgreSQL database. To run tests against PostgreSQL instead, use `python manage.py test` with `.env` configured; Django uses a separate `test_...` database.

## JWT authentication

Register with `POST /api/auth/register/`, then log in with `POST /api/auth/login/`. Login returns access and refresh JWTs. Include the access token with protected requests:

```http
Authorization: Bearer <your-access-token>
```

Access tokens expire after 30 minutes; refresh tokens expire after one day. Request a new access token with `POST /api/auth/token/refresh/` and a JSON body containing the refresh token.

## API endpoints

Registration and login are public. Patient, doctor, and mapping routes require a valid access token.

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/register/` | Register with `name`, `email`, and `password` |
| POST | `/api/auth/login/` | Obtain access and refresh JWTs |
| POST | `/api/auth/token/refresh/` | Obtain a new access token |
| POST | `/api/patients/` | Create a patient owned by the current user |
| GET | `/api/patients/` | List the current user's patients |
| GET | `/api/patients/{id}/` | Retrieve an owned patient |
| PUT | `/api/patients/{id}/` | Update an owned patient |
| DELETE | `/api/patients/{id}/` | Delete an owned patient |
| POST | `/api/doctors/` | Create a doctor record |
| GET | `/api/doctors/` | List doctor records |
| GET | `/api/doctors/{id}/` | Retrieve a doctor |
| PUT | `/api/doctors/{id}/` | Update a doctor |
| DELETE | `/api/doctors/{id}/` | Delete a doctor |
| POST | `/api/mappings/` | Assign a doctor to an owned patient |
| GET | `/api/mappings/` | List assignments for the current user's patients |
| GET | `/api/mappings/{patient_id}/` | List doctors assigned to an owned patient |
| DELETE | `/api/mappings/{mapping_id}/` | Delete an assignment by mapping ID |

Patient fields are `name`, `age` (0-150), `gender` (`female`, `male`, `other`, or `prefer_not_to_say`), `address`, and `phone_number`. The patient owner is derived from the authenticated user. Doctor fields are `name`, `specialization`, `email`, and `phone_number`. Mapping creation accepts numeric `patient` and `doctor` IDs, for example `{"patient": 1, "doctor": 2}`.

Doctor records are shared among authenticated users. Patient and mapping records are owner-scoped. Duplicate patient-doctor pairs are prevented by serializer validation and a database uniqueness constraint. Deleting a patient or doctor cascades to its assignments; deleting an assignment does not delete either related record.

## Postman

Import [`postman/healthcare-backend.postman_collection.json`](postman/healthcare-backend.postman_collection.json) into Postman. Set the collection variables `baseUrl`, `testEmail`, and `testPassword`; use a new email when registering against a persistent database. Run Register, then Login. The collection stores the returned JWTs for subsequent protected requests and captures created patient, doctor, and mapping IDs for dependent requests. The collection contains no local environment credentials or pre-filled JWTs.
