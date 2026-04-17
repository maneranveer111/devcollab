# 🚀 DevCollab Backend API

A production-style backend system built with **FastAPI**, demonstrating real-world backend engineering concepts like authentication, caching, rate limiting, Dockerization, and automated testing.

---

## 📌 Overview

DevCollab is a backend API that simulates a collaboration platform.
It is designed to showcase **scalable, secure, and testable backend architecture** using modern technologies.

---

## 🏗️ Tech Stack

| Layer                   | Technology              |
| ----------------------- | ----------------------- |
| Backend Framework       | FastAPI                 |
| Database                | PostgreSQL              |
| ORM                     | SQLAlchemy              |
| Authentication          | JWT (OAuth2)            |
| Caching & Rate Limiting | Redis                   |
| Testing                 | pytest                  |
| Containerization        | Docker + Docker Compose |

---

## 📁 Project Structure

```text
devcollab/
│
├── src/
│   ├── main.py              # FastAPI entry point
│   ├── db_models.py        # Database models (SQLAlchemy)
│   ├── schemas.py          # Pydantic schemas
│   ├── auth.py             # JWT authentication logic
│   ├── cache.py            # Redis caching & rate limiting
│   ├── utils.py            # Helper functions (pagination)
│   ├── models.py           # Core logic
│   ├── config/             # Configuration settings
│   └── db_demo.py          # DB practice/demo script
│
├── tests/
│   ├── conftest.py         # Test DB setup & fixtures
│   ├── test_auth.py        # Auth & protected route tests
│   ├── test_utils.py       # Unit tests
│   ├── test_health.py      # API tests
│   ├── test_errors.py      # Validation & error tests
│   └── test_basic.py       # Basic pytest checks
│
├── logs/                   # Application logs
├── docs/                   # Documentation (if any)
│
├── Dockerfile              # App container config
├── docker-compose.yml      # Multi-service setup
├── requirements.txt
├── pytest.ini
├── .env                    # Environment variables
├── test.db                 # Test database (SQLite)
└── README.md
```

---

## ⚙️ Features

### 🔐 Authentication

* JWT-based authentication system
* Secure password hashing
* Protected API routes

---

### 📊 API Design

* RESTful API structure
* Proper HTTP status codes
* Standardized error responses

---

### ⚡ Performance Optimization

* Redis caching for frequently accessed data
* Rate limiting to prevent abuse
* Pagination for efficient data handling

---

### 🧠 System Design Concepts Applied

* Stateless architecture (JWT-based auth)
* Separation of concerns
* Dependency injection
* Cache-first approach

---

### 🧪 Testing

* Unit tests for helper functions
* API testing using FastAPI TestClient
* Authentication flow testing (register, login, protected routes)
* Validation and error handling tests
* Isolated test database using pytest fixtures

---

### 🐳 Docker Support

* Multi-container architecture:

  * FastAPI app
  * PostgreSQL
  * Redis
* Entire system runs with a single command

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/maneranveer111/devcollab.git
cd devcollab
```

---

### 2️⃣ Setup Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@db/devcollab
SECRET_KEY=your_secret_key
REDIS_HOST=redis
```

---

### 3️⃣ Run with Docker

```bash
docker compose up --build
```

---

### 4️⃣ Access API

* Swagger Docs → http://localhost:8000/docs
* Base URL → http://localhost:8000

---

## 🧪 Running Tests

```bash
pytest
```

---

## 📈 Example API Endpoints

| Method | Endpoint              | Description           |
| ------ | --------------------- | --------------------- |
| POST   | /api/v1/auth/register | Register user         |
| POST   | /api/v1/auth/login    | Login user            |
| GET    | /api/v1/users         | Get users (protected) |
| GET    | /health               | Health check          |

---

## ⚠️ Important Notes

* PostgreSQL is the **primary data source**
* Redis is used for **caching and rate limiting**
* Authentication is **stateless using JWT**
* Pagination prevents large data responses
* Tests use an **isolated SQLite test database (`test.db`)**

---

## 👨‍💻 Author

Backend system built as part of a structured learning journey focused on **real-world backend development and system design**.

---

## ⭐ Summary

This project demonstrates:

> Building a scalable backend system with authentication, caching, testing, and containerization using real-world engineering practices.
