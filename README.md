🚀 DevCollab — Backend API for Team Collaboration
A production-ready backend system for managing users, projects, and tasks, built with modern backend technologies and real-world architecture patterns.

---
📌 Overview
DevCollab is a backend service that enables teams to:
Manage users and authentication
Create and manage projects
Assign and track tasks
Enforce access control with authorization
Search and filter data efficiently
The focus is on clean architecture, scalability, and real backend engineering practices.
---

🛠 Tech Stack
Layer	Technology
Backend	FastAPI
Database	PostgreSQL
ORM	SQLAlchemy
Migrations	Alembic
Caching & Rate Limiting	Redis
Authentication	JWT (OAuth2)
Containerization	Docker (optional)
---

✨ Features
🔐 Authentication & Users
User registration & login (JWT-based)
Secure password handling
Role system: `ADMIN`, `MEMBER`, `VIEWER`
Soft delete users (`is_active` flag)

📁 Projects
Create project
Get all projects (pagination supported)
Get project by ID
Update project
Soft delete project

📋 Tasks
Create tasks under projects
Assign tasks to users
Mark tasks as complete
Update task details
Get tasks per project

🔄 Task Lifecycle
```
Create → Assign → Complete → Track
```
🔎 Filtering & Search
Filter tasks by:
Status: `completed`, `pending`
Priority: `low`, `medium`, `high`, `critical`
Search tasks by title or description
Search projects by name or description

📊 Pagination
All list APIs support pagination
Consistent API responses

🔐 Authorization
Only the project owner can:
Assign tasks
Update / delete the project
Only the assigned user or owner can:
Complete a task
⚡ Performance
Redis-based rate limiting
Optimized queries using SQLAlchemy
Clean and modular structure
🧱 Database Management
Alembic migrations for schema versioning
No runtime `create_all` (production practice)

---
📂 Project Structure
```
devcollab/
│── src/
│   ├── config/        # DB and settings
│   ├── db_models.py   # SQLAlchemy models
│   ├── schemas.py     # Pydantic schemas
│   ├── main.py        # FastAPI app
│
│── alembic/           # Database migrations
│── scripts/           # Utility scripts (optional)
│── tests/             # Test cases (optional)
│── .env.example       # Environment template
│── docker-compose.yml
│── README.md
```
---
⚙️ Setup Instructions
1️⃣ Clone Repository
```bash
git clone https://github.com/maneranveer111/devcollab
cd devcollab
```
2️⃣ Create Virtual Environment
```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows
```
3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
4️⃣ Setup Environment Variables
Create a `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost/devcollab
SECRET_KEY=your_secret_key
REDIS_HOST=localhost
```
5️⃣ Run Migrations
```bash
alembic upgrade head
```
6️⃣ Start Server
```bash
uvicorn src.main:app --reload
```
7️⃣ Open API Docs
```
http://127.0.0.1:8000/docs
```
---
🧪 API Examples
🔐 Login
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ranveer&password=password123"
```
🔎 Search Tasks
```bash
curl "http://127.0.0.1:8000/api/v1/tasks/search?search=bug" \
  -H "Authorization: Bearer <TOKEN>"
```
🔍 Filter Tasks
```bash
curl "http://127.0.0.1:8000/api/v1/projects/1/tasks?status=completed&priority=high" \
  -H "Authorization: Bearer <TOKEN>"
```
---
🧠 Key Backend Concepts Implemented
RESTful API design
JWT Authentication & Authorization
Role-based access control (basic)
Database migrations (Alembic)
Pagination, filtering, and search
Rate limiting with Redis
Clean architecture & modular design

---
📈 Project Highlights
Production-style DB handling (no `create_all`)
Clean and consistent API responses
Real-world business logic (task lifecycle)
Secure and structured backend design

---
🚀 Future Improvements
Project member management
Advanced role-based access control (RBAC)
Activity logs
Notifications system

---
👨‍💻 Author
Ranveer Mane
GitHub: https://github.com/maneranveer111