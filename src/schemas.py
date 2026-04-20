from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class UserCreateSchema(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def username_must_be_alphanumeric(cls, value: str) -> str:
        if not value.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, underscores")
        return value.lower()


class ProjectCreateSchema(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    max_members: int = Field(default=10, ge=1, le=100)


class TaskCreateSchema(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: Optional[str] = None
    # assigned_to: Optional[str] = None
    priority: str = Field(default="medium")

    @field_validator("priority")
    @classmethod
    def priority_must_be_valid(cls, value: str) -> str:
        allowed = ["low", "medium", "high", "critical"]
        if value.lower() not in allowed:
            raise ValueError(f"Priority must be one of: {allowed}")
        return value.lower()


class UserResponseSchema(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectResponseSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]
    max_members: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class TaskResponseSchema(BaseModel):
    """What the API returns when asked about a task."""
    id: int
    title: str
    description: Optional[str]
    assigned_to: Optional[str]
    priority: str
    is_completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class AssignTaskSchema(BaseModel):
    username: str = Field(min_length=3, max_length=30)

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, value: str) -> str:
        if not value.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, underscores")
        return value.lower()

class ProjectUpdateSchema(BaseModel):
    name:  Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    max_members: Optional[int] = Field(default=None, ge=1, le=100)

    
class TaskUpdateSchema(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = None

if __name__ == "__main__":
    print("=== Test 1: Valid user ===")
    valid_user = UserCreateSchema(
        username="ranveer_111",
        email="ranveer@devcollab.com",
        full_name="Ranveer Mane",
        password="securepass123"
    )
    print(valid_user)

    print("\n=== Test 2: Invalid email ===")
    try:
        bad_user = UserCreateSchema(
            username="ranveer",
            email="not-an-email",
            full_name="Ranveer Mane",
            password="securepass123"
        )
    except Exception as e:
        print(f"Caught: {e}")

    print("\n=== Test 3: Password too short ===")
    try:
        bad_user = UserCreateSchema(
            username="ranveer",
            email="ranveer@devcollab.com",
            full_name="Ranveer Mane",
            password="short"
        )
    except Exception as e:
        print(f"Caught: {e}")

    print("\n=== Test 4: Invalid priority ===")
    try:
        bad_task = TaskCreateSchema(
            title="Fix login bug",
            priority="urgent"
        )
    except Exception as e:
        print(f"Caught: {e}")

    print("\n=== Test 5: Valid project ===")
    project = ProjectCreateSchema(
        name="DevCollab API",
        description="Team collaboration platform",
        max_members=15
    )
    print(project)
    print(f"As dict: {project.model_dump()}")

