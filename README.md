# Healthcare Backend API

A complete Django REST Framework backend for a healthcare application with JWT authentication, custom user model, and relational management for Patients, Doctors, and Patient-Doctor Mappings.

---

## Tech Stack
- **Language**: Python 3.10 (managed strictly via `venv`)
- **Web Framework**: Django 5.2 LTS
- **API Framework**: Django REST Framework (DRF)
- **Authentication**: JWT via `djangorestframework-simplejwt`
- **Database**: PostgreSQL (`psycopg2-binary`)
- **Environment Management**: `python-decouple`

---

## Setup & Installation

### 1. Prerequisites
- Python 3.10 installed on your system.
- PostgreSQL server running locally on port `5432` with a database named `healthcare_db`.

### 2. Create and Activate Virtual Environment
Using Python 3.10:
```powershell
py -3.10 -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
.\venv\Scripts\pip.exe install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` if not already created:
```powershell
cp .env.example .env
```
Fill in your database password in `.env`:
```ini
SECRET_KEY=your_generated_secret_key_here
DEBUG=True
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=your_actual_password_here
DB_HOST=localhost
DB_PORT=5432
```

### 5. Run Migrations
Apply migrations to your PostgreSQL database:
```powershell
.\venv\Scripts\python.exe manage.py migrate
```

### 6. Run Development Server
```powershell
.\venv\Scripts\python.exe manage.py runserver
```
The server will start at `http://127.0.0.1:8000/`.

---

## API Endpoints Reference

All patient, doctor, and mapping endpoints require an `Authorization: Bearer <access_token>` header.

| Method | Endpoint | Description | Auth Required | Permissions / Access |
|---|---|---|---|---|
| `POST` | `/api/auth/register/` | Register a new user | No | Anyone |
| `POST` | `/api/auth/login/` | Obtain JWT access & refresh tokens | No | Anyone |
| `GET` | `/api/patients/` | List all patients created by the authenticated user | Yes | Authenticated user (owner only) |
| `POST` | `/api/patients/` | Create a new patient (sets `created_by` to user) | Yes | Authenticated user |
| `GET` | `/api/patients/<id>/` | Retrieve patient detail | Yes | Patient owner only (403 for others) |
| `PUT` | `/api/patients/<id>/` | Update patient record | Yes | Patient owner only (403 for others) |
| `DELETE` | `/api/patients/<id>/` | Delete patient record | Yes | Patient owner only (403 for others) |
| `GET` | `/api/doctors/` | List all doctors in system | Yes | Authenticated user |
| `POST` | `/api/doctors/` | Register a doctor (sets `created_by` to user) | Yes | Authenticated user |
| `GET` | `/api/doctors/<id>/` | Retrieve doctor detail | Yes | Authenticated user |
| `PUT` | `/api/doctors/<id>/` | Update doctor details | Yes | Doctor creator only (403 for others) |
| `DELETE` | `/api/doctors/<id>/` | Delete doctor profile | Yes | Doctor creator only (403 for others) |
| `GET` | `/api/mappings/` | List all mappings for current user's patients | Yes | Authenticated user |
| `POST` | `/api/mappings/` | Assign a doctor to a patient | Yes | Patient owner only |
| `GET` | `/api/mappings/<patient_id>/` | List all doctors assigned to patient | Yes | Patient owner only |
| `DELETE` | `/api/mappings/<id>/` | Remove a doctor assignment | Yes | Patient owner only |

---

## Sample Request & Response Payloads

### 1. Register User
**`POST /api/auth/register/`**
- **Request Body**:
```json
{
  "name": "Dr. Jane Doe",
  "email": "jane.doe@example.com",
  "password": "SecurePassword123!"
}
```
- **Response (`201 Created`)**:
```json
{
  "id": 1,
  "name": "Dr. Jane Doe",
  "email": "jane.doe@example.com"
}
```

---

### 2. Login User
**`POST /api/auth/login/`**
- **Request Body**:
```json
{
  "email": "jane.doe@example.com",
  "password": "SecurePassword123!"
}
```
- **Response (`200 OK`)**:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsIn...",
  "access": "eyJhbGciOiJIUzI1NiIsIn..."
}
```

---

### 3. Create Patient
**`POST /api/patients/`**
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
```json
{
  "name": "Alice Johnson",
  "age": 32,
  "gender": "Female",
  "phone": "+1-555-0199",
  "address": "123 Maple Street, Springfield",
  "medical_history": "Hypertension diagnosed in 2021"
}
```
- **Response (`201 Created`)**:
```json
{
  "id": 1,
  "created_by": 1,
  "name": "Alice Johnson",
  "age": 32,
  "gender": "Female",
  "phone": "+1-555-0199",
  "address": "123 Maple Street, Springfield",
  "medical_history": "Hypertension diagnosed in 2021",
  "created_at": "2026-10-15T11:30:00Z",
  "updated_at": "2026-10-15T11:30:00Z"
}
```

---

### 4. Create Doctor
**`POST /api/doctors/`**
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
```json
{
  "name": "Robert Smith",
  "specialization": "Cardiology",
  "email": "dr.smith@example.com",
  "phone": "+1-555-0811",
  "experience_years": 12
}
```
- **Response (`201 Created`)**:
```json
{
  "id": 1,
  "created_by": 1,
  "name": "Robert Smith",
  "specialization": "Cardiology",
  "email": "dr.smith@example.com",
  "phone": "+1-555-0811",
  "experience_years": 12,
  "created_at": "2026-10-15T11:32:00Z",
  "updated_at": "2026-10-15T11:32:00Z"
}
```

---

### 5. Assign Doctor to Patient (Create Mapping)
**`POST /api/mappings/`**
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
```json
{
  "patient": 1,
  "doctor": 1
}
```
- **Response (`201 Created`)**:
```json
{
  "id": 1,
  "patient": 1,
  "doctor": 1,
  "assigned_at": "2026-10-15T11:35:00Z",
  "patient_details": {
    "id": 1,
    "created_by": 1,
    "name": "Alice Johnson",
    "age": 32,
    "gender": "Female",
    "phone": "+1-555-0199",
    "address": "123 Maple Street, Springfield",
    "medical_history": "Hypertension diagnosed in 2021",
    "created_at": "2026-10-15T11:30:00Z",
    "updated_at": "2026-10-15T11:30:00Z"
  },
  "doctor_details": {
    "id": 1,
    "created_by": 1,
    "name": "Robert Smith",
    "specialization": "Cardiology",
    "email": "dr.smith@example.com",
    "phone": "+1-555-0811",
    "experience_years": 12,
    "created_at": "2026-10-15T11:32:00Z",
    "updated_at": "2026-10-15T11:32:00Z"
  }
}
```

---

### 6. Get Doctors Assigned to Patient
**`GET /api/mappings/1/`**
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (`200 OK`)**:
```json
[
  {
    "id": 1,
    "created_by": 1,
    "name": "Robert Smith",
    "specialization": "Cardiology",
    "email": "dr.smith@example.com",
    "phone": "+1-555-0811",
    "experience_years": 12,
    "created_at": "2026-10-15T11:32:00Z",
    "updated_at": "2026-10-15T11:32:00Z"
  }
]
```

---

### 7. Delete Mapping
**`DELETE /api/mappings/1/`**
- **Headers**: `Authorization: Bearer <access_token>`
- **Response (`204 No Content`)**

---

## Postman Collection
Import [`postman_collection.json`](./postman_collection.json) directly into Postman. It includes pre-configured environment variables and automatically saves the JWT access token to `access_token` on login.
