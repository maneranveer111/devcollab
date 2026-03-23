from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from src.config.database import get_db
from src.db_models import User, Project, Task, UserRoleEnum
from src.schemas import (
    UserCreateSchema,
    ProjectCreateSchema,
    TaskCreateSchema,
)

app = FastAPI(
    title="DevCollab API",
    description="Team collaboration platform built with FastAPI",
    version="1.0.0"
)


# ─── Health check ─────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": "DevCollab API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# ─── User endpoints ───────────────────────────────────────────────────────────

@app.post("/api/v1/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    # Check if username already exists
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user.username}' already exists"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{user.email}' already exists"
        )

    # Create the user
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        password_hash=user.password,
        role=UserRoleEnum.MEMBER
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "message": "User created successfully",
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


@app.get("/api/v1/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.is_active == True).all()
    return {
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
        "count": len(users)
    }


@app.get("/api/v1/users/{username}")
def get_user(username: str, db: Session = Depends(get_db)):
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
def delete_user(username: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )
    db_user.is_active = False
    db.commit()
    return None


# ─── Project endpoints ────────────────────────────────────────────────────────

@app.post("/api/v1/projects", status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreateSchema, db: Session = Depends(get_db)):
    db_project = Project(
        name=project.name,
        description=project.description,
        max_members=project.max_members,
        owner_id=1
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
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
def get_all_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).filter(Project.is_active == True).all()
    return {
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
        "count": len(projects)
    }


@app.get("/api/v1/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
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


# ─── Task endpoints ───────────────────────────────────────────────────────────

@app.post("/api/v1/projects/{project_id}/tasks", status_code=status.HTTP_201_CREATED)
def create_task(project_id: int, task: TaskCreateSchema, db: Session = Depends(get_db)):
    # Verify project exists
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
def get_project_tasks(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found"
        )

    tasks = db.query(Task).filter(Task.project_id == project_id).all()
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
        "count": len(tasks)
    }