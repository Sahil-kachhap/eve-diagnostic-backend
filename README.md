# EVE Healthcare API

A production-oriented REST API for managing diagnostic centres, medical tests, bookings, and simulated payments. Built as part of the EVE Healthcare backend engineering assignment, with a focus on **clean API design, data integrity, authentication, payment idempotency, edge-case handling, and automated testing**.

## Tech Stack

* **Backend:** Django + Django REST Framework
* **Database:** PostgreSQL
* **Authentication:** JWT
* **API Documentation:** OpenAPI / Swagger
* **Testing:** Pytest
* **Package Management:** uv
* **Deployment:** Docker + Render
* **Payment:** Mock payment provider with webhook simulation

## Core Features

### Authentication

* User signup and login
* JWT access and refresh tokens
* Role-based access control
* Admin-only catalogue management

### Diagnostic Catalogue

* Manage diagnostic centres
* Manage diagnostic tests
* Configure tests offered by each centre
* Set test prices and availability
* Paginated catalogue APIs

### Bookings

* Create and retrieve bookings
* Booking ownership enforcement
* Appointment scheduling
* Booking status lifecycle:

  * `PENDING`
  * `CONFIRMED`
  * `FAILED`
  * `CANCELLED`
* Booking cancellation with state validation

### Payments

* Simulated payment creation
* Payment status lifecycle:

  * `PENDING`
  * `SUCCESS`
  * `FAILED`
* HMAC-signed payment webhooks
* Idempotent webhook processing
* Protection against invalid payment amounts and invalid state transitions

## API Structure

| Module               | Purpose                                 |
| -------------------- | --------------------------------------- |
| `/api/v1/accounts/`  | Authentication and user APIs            |
| `/api/v1/catalogue/` | Centres, tests and centre-test mappings |
| `/api/v1/bookings/`  | Booking management                      |
| `/api/v1/payments/`  | Payment creation and webhooks           |
| `/api/schema/`       | OpenAPI schema                          |
| `/api/docs/`         | Swagger UI                              |
| `/api/redoc/`        | ReDoc                                   |

## Important API Endpoints

### Authentication

```http
POST /api/v1/accounts/signup/
POST /api/v1/accounts/login/
POST /api/v1/accounts/token/refresh/
GET  /api/v1/accounts/me/
```

### Catalogue

```http
GET    /api/v1/catalogue/centres/
POST   /api/v1/catalogue/centres/

GET    /api/v1/catalogue/tests/
POST   /api/v1/catalogue/tests/

GET    /api/v1/catalogue/centre-tests/
POST   /api/v1/catalogue/centre-tests/

GET    /api/v1/catalogue/centre-tests/available/
```

`POST`, `PUT/PATCH`, and `DELETE` catalogue operations require an **ADMIN** role.

### Bookings

```http
GET  /api/v1/bookings/
POST /api/v1/bookings/

GET  /api/v1/bookings/<id>/
POST /api/v1/bookings/<id>/cancel/
```

### Payments

```http
POST /api/v1/payments/
POST /api/v1/payments/webhook/
```

Authenticated endpoints require:

```http
Authorization: Bearer <access_token>
```

The payment webhook uses an HMAC signature through:

```http
X-Webhook-Signature: <signature>
```

## Booking Flow

```text
User
  │
  ├── Signup / Login
  │
  ├── Browse available diagnostic tests
  │
  ├── Create Booking
  │        │
  │        └── PENDING
  │
  ├── Create Payment
  │        │
  │        └── PENDING
  │
  └── Payment Webhook
           │
           ├── SUCCESS → Booking CONFIRMED
           │
           └── FAILED  → Booking FAILED
```

## Design & Engineering Decisions

### Data Integrity

* PostgreSQL relational constraints
* Unique centre-test relationships
* Positive price/amount constraints
* Protected foreign-key relationships where appropriate
* Transactional booking and payment operations

### State Management

Booking and payment transitions are explicitly validated rather than allowing arbitrary status changes.

For example:

```text
PENDING → CONFIRMED
PENDING → FAILED
PENDING → CANCELLED
```

Terminal states cannot be transitioned again.

### Payment Idempotency

Payment webhooks contain a unique `event_id`. Previously processed events are not processed again, preventing duplicate payment updates or duplicate booking state transitions.

### Concurrency

Database transactions and row-level locking are used around critical booking/payment operations to reduce race conditions during concurrent requests.

### Security

* Passwords are hashed using Django's authentication system
* JWT-based authentication
* Role-based authorization
* Webhook HMAC verification
* Secrets/configuration loaded through environment variables
* No credentials committed to source control

## Running Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd eve-healthcare
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Create `.env`:

```env
DEBUG=True
SECRET_KEY=your-secret-key

DB_NAME=eve_healthcare
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5433

JWT_ACCESS_TOKEN_LIFETIME_MINUTES=30
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

PAYMENT_WEBHOOK_SECRET=your-webhook-secret
```

### 4. Start PostgreSQL

Using Docker:

```bash
docker compose up -d postgres
```

### 5. Run migrations

```bash
uv run python manage.py migrate
```

### 6. Start the server

```bash
uv run python manage.py runserver
```

The API will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/api/docs/
```

## Running with Docker

```bash
docker compose up --build
```

This starts the Django application and PostgreSQL database together.

## Testing

Run the complete test suite:

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=.
```

The test suite covers authentication, catalogue operations, booking lifecycle, payment processing, webhook handling, authorization, validation, and important edge cases.

## Deployment

The application is containerized and deployed using **Render** with:

* Docker-based Django web service
* Managed PostgreSQL database
* Gunicorn for production serving
* WhiteNoise for static files
* Environment-based configuration

### Live API

**[https://eve-healthcare-api.onrender.com](https://eve-healthcare-api.onrender.com)**

### API Documentation

**[https://eve-healthcare-api.onrender.com/api/docs/](https://eve-healthcare-api.onrender.com/api/docs/)**

## Project Structure

```text
eve-healthcare/
├── accounts/       # Authentication and users
├── catalogue/      # Centres, tests and pricing
├── bookings/       # Booking lifecycle
├── payments/       # Payments and webhooks
├── common/         # Shared utilities
├── <project>/      # Django project configuration
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── README.md
```

## Notes

This project uses a **mock payment provider** for demonstration purposes. No real financial transactions are performed.

The API is designed as an assignment implementation with emphasis on **maintainability, correctness, clear separation of concerns, and production-oriented backend practices**.
