from contextlib import asynccontextmanager
from src.config.database import get_db, engine, Base
from sqlalchemy import text
import asyncio
from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import time
import logging
import math

from src.auth import hash_password, verify_password, create_access_token, get_current_user
from src.config.database import get_db
from src.db_models import User, Project, Task, UserRoleEnum
from src.schemas import (
    UserCreateSchema,
    ProjectCreateSchema,
    TaskCreateSchema,
    AssignTaskSchema
)
from src.cache import (
    get_cached_data,
    set_cached_data,
    invalidate_cache,
    check_redis_connection,
    check_rate_limit,
    rate_limit_login,
    USERS_CACHE_KEY,
    PROJECTS_CACHE_KEY
)
from fastapi.security import OAuth2PasswordRequestForm

# ─── Logging setup ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ─── The lifespan function ──────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    max_retries = 10
    retry_delay = 3

    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            print("Database connection successful.")
            break

        except Exception as e:
            print(f"Database not ready yet (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(retry_delay)

    yield


# ─── App setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="DevCollab API",
    description="Team collaboration platform built with FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

# ─── CORS middleware ──────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request logging middleware ───────────────────────────────────────────────

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} "
        f"→ {response.status_code} ({duration}ms)"
    )
    return response

# ─── Error code helper ────────────────────────────────────────────────────────

def get_error_code(status_code: int) -> str:
    codes = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
        429: "rate_limit_exceeded",
        500: "internal_server_error"
    }
    return codes.get(status_code, "error")

# ─── Exception handlers ───────────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": get_error_code(exc.status_code),
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "status_code": 422,
            "details": exc.errors()
        }
    )

# ─── Pagination helper ────────────────────────────────────────────────────────

def paginate(query, page: int, limit: int):
    """
    Apply pagination to a SQLAlchemy query.
    Returns (items, pagination_metadata)
    """
    # Clamp values — prevent negative pages or zero limits
    page = max(1, page)
    limit = max(1, min(100, limit))  # max 100 items per page

    total = query.count()
    total_pages = math.ceil(total / limit) if total > 0 else 1
    offset = (page - 1) * limit

    items = query.offset(offset).limit(limit).all()

    pagination = {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }

    return items, pagination

# ─── Health check ─────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": "DevCollab API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "redis": "connected" if check_redis_connection() else "disconnected"
    }

# ─── Auth endpoints ───────────────────────────────────────────────────────────

@app.post("/api/v1/auth/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user.username}' already exists"
        )

    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{user.email}' already exists"
        )

    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        password_hash=hash_password(user.password),
        role=UserRoleEnum.MEMBER
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    invalidate_cache(USERS_CACHE_KEY)

    return {
        "message": "User registered successfully",
        "data": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "role": db_user.role.value,
            "is_active": db_user.is_active,
            "created_at": db_user.created_at.isoformat()
        }
    }


@app.post("/api/v1/auth/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    _=Depends(rate_limit_login)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )

    access_token = create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ─── User endpoints (PROTECTED) ──────────────────────────────────────────────

@app.get("/api/v1/users")
def get_all_users(
    request: Request,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Rate limit
    if not check_rate_limit(f"api:{current_user.username}", limit=100, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before making more requests."
        )

    # Cache only works for default page/limit
    # For paginated requests we skip cache
    if page == 1 and limit == 10:
        cached = get_cached_data(USERS_CACHE_KEY)
        if cached:
            return cached

    # Query with pagination
    query = db.query(User).filter(User.is_active == True)
    users, pagination = paginate(query, page, limit)

    response = {
        "message": "Users retrieved successfully",
        "data": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role.value,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat()
            }
            for u in users
        ],
        "pagination": pagination
    }

    # Cache only the first page
    if page == 1 and limit == 10:
        set_cached_data(USERS_CACHE_KEY, response)

    return response


@app.get("/api/v1/users/{username}")
def get_user(
    username: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not check_rate_limit(f"api:{current_user.username}", limit=100, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded."
        )

    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )
    return {
        "message": "User retrieved successfully",
        "data": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "role": db_user.role.value,
            "is_active": db_user.is_active,
            "created_at": db_user.created_at.isoformat()
        }
    }


@app.delete("/api/v1/users/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    username: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not check_rate_limit(f"api:{current_user.username}", limit=100, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded."
        )

    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )
    db_user.is_active = False
    db.commit()
    invalidate_cache(USERS_CACHE_KEY)
    return None

# ─── Project endpoints (PROTECTED) ───────────────────────────────────────────

@app.post("/api/v1/projects", status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreateSchema,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not check_rate_limit(f"api:{current_user.username}", limit=100, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded."
        )

    db_project = Project(
        name=project.name,
        description=project.description,
        max_members=project.max_members,
        owner_id=current_user.id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    invalidate_cache(PROJECTS_CACHE_KEY)

    return {
        "message": "Project created successfully",
        "data": {
            "id": db_project.id,
            "name": db_project.name,
            "description": db_project.description,
            "max_members": db_project.max_members,
            "is_active": db_project.is_active,
            "owner_id": db_project.owner_id,
            "created_at": db_project.created_at.isoformat()
        }
    }


@app.get("/api/v1/projects")
def get_all_projects(
    request: Request,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not check_rate_limit(f"api:{current_user.username}", limit=100, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded."
        )

    if page == 1 and limit == 10:
        cached = get_cached_data(PROJECTS_CACHE_KEY)
        if cached:
            return cached

    query = db.query(Project).filter(Project.is_active == True)
    projects, pagination = paginate(query, page, limit)

    response = {
        "message": "Projects retrieved successfully",
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "max_members": p.max_members,
                "is_active": p.is_active,
                "owner_id": p.owner_id,
                "created_at": p.created_at.isoformat()
            }
            for p in projects
        ],
        "pagination": pagination
    }

    if page == 1 and limit == 10:
        set_cached_data(PROJECTS_CACHE_KEY, response)

    return response


@app.get("/api/v1/projects/{project_id}")
def get_project(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not check_rate_limit(f"api:{current_user.username}", limit=100, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded."
        )

    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id '{project_id}' not found"
        )
    return {
        "message": "Project retrieved successfully",
        "data": {
            "id": db_project.id,
            "name": db_project.name,
            "description": db_project.description,
            "max_members": db_project.max_members,
            "is_active": db_project.is_active,
            "owner_id": db_project.owner_id,
            "created_at": db_project.created_at.isoformat()
        }
    }

# ─── Task endpoints (PROTECTED) ──────────────────────────────────────────────

@app.post("/api/v1/projects/{project_id}/tasks", status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    task: TaskCreateSchema,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not check_rate_limit(f"api:{current_user.username}", limit=100, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded."
        )

    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found"
        )

    db_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        project_id=project_id,
        assigned_to=None
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return {
        "message": "Task created successfully",
        "data": {
            "id": db_task.id,
            "title": db_task.title,
            "description": db_task.description,
            "priority": db_task.priority,
            "is_completed": db_task.is_completed,
            "project_id": db_task.project_id,
            "assigned_to": db_task.assigned_to,
            "created_at": db_task.created_at.isoformat()
        }
    }


@app.get("/api/v1/projects/{project_id}/tasks")
def get_project_tasks(
    project_id: int,
    request: Request,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not check_rate_limit(f"api:{current_user.username}", limit=100, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded."
        )

    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found"
        )

    query = db.query(Task).filter(Task.project_id == project_id)
    tasks, pagination = paginate(query, page, limit)

    return {
        "message": "Tasks retrieved successfully",
        "data": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "is_completed": t.is_completed,
                "project_id": t.project_id,
                "assigned_to": t.assigned_to,
                "created_at": t.created_at.isoformat()
            }
            for t in tasks
        ],
        "pagination": pagination
    }


@app.put("/api/v1/tasks/{task_id}/assign")
def assign_task(
    task_id: int,
    payload: AssignTaskSchema,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Rate limit
    if not check_rate_limit(f"api:{current_user.username}", limit=100, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded."
        )

    # Check task exists
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found"
        )

    # Get project
    db_project = db.query(Project).filter(Project.id == db_task.project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{db_task.project_id}' not found"
        )

    # Ownership check (critical)
    if db_project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can assign tasks"
        )

    # Check user exists
    db_user = db.query(User).filter(User.username == payload.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{payload.username}' not found"
        )

    # Prevent assigning to inactive user
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign task to inactive user"
        )

    # Prevent duplicate assignment
    if db_task.assigned_to == db_user.id:
        return {
            "message": "Task already assigned to this user",
            "data": {
                "task_id": db_task.id,
                "assigned_to": db_user.username
            }
        }

    # Assign task
    db_task.assigned_to = db_user.id
    db.commit()
    db.refresh(db_task)

    return {
        "message": "Task assigned successfully",
        "data": {
            "task_id": db_task.id,
            "assigned_to": db_user.username
        }
    }


@app.put("/api/v1/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Rate limit
    if not check_rate_limit(f"api:{current_user.username}", limit=100, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded."
        )

    # Check task exists
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found"
        )

    # Get project
    db_project = db.query(Project).filter(Project.id == db_task.project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{db_task.project_id}' not found"
        )

    # Authorization check
    is_owner = db_project.owner_id == current_user.id
    is_assignee = db_task.assigned_to == current_user.id

    if not (is_owner or is_assignee):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only assigned user or project owner can complete task"
        )

    # Prevent re-completing
    if db_task.is_completed:
        return {
            "message": "Task already completed",
            "data": {
                "task_id": db_task.id,
                "is_completed": True
            }
        }

    # Mark complete
    db_task.is_completed = True
    db.commit()
    db.refresh(db_task)

    return {
        "message": "Task marked as completed",
        "data": {
            "task_id": db_task.id,
            "is_completed": db_task.is_completed
        }
    }


@app.get("/api/v1/users/{username}/tasks")
def get_user_tasks(
    username: str,
    request: Request,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Rate limit
    if not check_rate_limit(f"api:{current_user.username}", limit=100, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded."
        )

    # Check user exists
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )

    # Query tasks assigned to user
    query = db.query(Task).filter(Task.assigned_to == db_user.id)

    tasks, pagination = paginate(query, page, limit)

    return {
        "message": "User tasks retrieved successfully",
        "data": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "is_completed": t.is_completed,
                "project": {
                    "id" : t.project.id,
                    "name" : t.project.name
                },
                "assigned_to": db_user.username,
                "created_at": t.created_at.isoformat()
            }
            for t in tasks
        ],
        "pagination": pagination
    }