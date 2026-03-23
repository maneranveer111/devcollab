from sqlalchemy import (
    Column, Integer, String, Boolean, 
    DateTime, Text, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime
from src.config.database import Base
import enum


# ── Enum for user roles ────────────────────────────────────────────────────

class UserRoleEnum(enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


# ── User model ─────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRoleEnum),
        default=UserRoleEnum.MEMBER,
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationships
    owned_projects = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    assigned_tasks = relationship(
        "Task",
        back_populates="assignee"
    )

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"


# ── Project model ──────────────────────────────────────────────────────────

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    max_members = Column(Integer, default=10, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="owned_projects")
    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project(name={self.name}, owner_id={self.owner_id})>"


# ── Task model ─────────────────────────────────────────────────────────────

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), default="medium", nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")

    def __repr__(self):
        return f"<Task(title={self.title}, priority={self.priority})>"