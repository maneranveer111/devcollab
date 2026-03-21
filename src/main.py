from fastapi import FastAPI, HTTPException, status
from typing import List, Optional
from datetime import datetime
from src.schemas import (
    UserCreateSchema,
    UserResponseSchema,
    ProjectCreateSchema,
    ProjectResponseSchema,
    TaskCreateSchema,
    TaskResponseSchema
)

app = FastAPI(
    title="DevCollab API",
    description="Team collaboration platform built with FastAPI",
    version="1.0.0"
)

# Temporary in-memory storage (we replace this with a real DB in Week 4)
users_db: dict = {}
projects_db: dict = {}
tasks_db: dict = {}


# ─── Health check ────────────────────────────────────────────────────────────

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
def create_user(user: UserCreateSchema):
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user.username}' already exists"
        )
    users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": "member",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    return {
        "message": "User created successfully",
        "data": users_db[user.username]
    }


@app.get("/api/v1/users")
def get_all_users():
    return {
        "message": "Users retrieved successfully",
        "data": list(users_db.values()),
        "count": len(users_db)
    }


@app.get("/api/v1/users/{username}")
def get_user(username: str):
    if username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )
    return {
        "message": "User retrieved successfully",
        "data": users_db[username]
    }


@app.delete("/api/v1/users/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(username: str):
    if username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )
    users_db[username]["is_active"] = False
    return None


# ─── Project endpoints ────────────────────────────────────────────────────────

@app.post("/api/v1/projects", status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreateSchema):
    project_id = len(projects_db) + 1
    projects_db[project_id] = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "max_members": project.max_members,
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    return {
        "message": "Project created successfully",
        "data": projects_db[project_id]
    }


@app.get("/api/v1/projects")
def get_all_projects():
    return {
        "message": "Projects retrieved successfully",
        "data": list(projects_db.values()),
        "count": len(projects_db)
    }


@app.get("/api/v1/projects/{project_id}")
def get_project(project_id: int):
    if project_id not in projects_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id '{project_id}' not found"
        )
    return {
        "message": "Project retrieved successfully",
        "data": projects_db[project_id]
    }


# ─── Task endpoints ───────────────────────────────────────────────────────────

@app.post(
    "/api/v1/projects/{project_id}/tasks",
    status_code=status.HTTP_201_CREATED
)
def create_task(project_id: int, task: TaskCreateSchema):
    if project_id not in projects_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found"
        )
    task_id = len(tasks_db) + 1
    tasks_db[task_id] = {
        "id": task_id,
        "project_id": project_id,
        "title": task.title,
        "description": task.description,
        "assigned_to": task.assigned_to,
        "priority": task.priority,
        "is_completed": False,
        "created_at": datetime.now().isoformat()
    }
    return {
        "message": "Task created successfully",
        "data": tasks_db[task_id]
    }


@app.get("/api/v1/projects/{project_id}/tasks")
def get_project_tasks(project_id: int):
    if project_id not in projects_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found"
        )
    project_tasks = [
        t for t in tasks_db.values()
        if t["project_id"] == project_id
    ]
    return {
        "message": "Tasks retrieved successfully",
        "data": project_tasks,
        "count": len(project_tasks)
    }