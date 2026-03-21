from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class User:
    def __init__(
        self,
        username: str,
        email: str,
        full_name: str,
        role: UserRole = UserRole.MEMBER
    ) -> None:
        self.username = username
        self.email = email
        self.full_name = full_name
        self.role = role
        self.created_at: datetime = datetime.now()
        self.is_active: bool = True
        self._projects: List[str] = []

    def add_to_project(self, project_name: str) -> None:
        if project_name not in self._projects:
            self._projects.append(project_name)
            print(f"{self.username} added to {project_name}")

    def deactivate(self) -> None:
        self.is_active = False
        print(f"User {self.username} deactivated")

    def get_projects(self) -> List[str]:
        return self._projects.copy()

    def __repr__(self) -> str:
        return f"User(username={self.username}, role={self.role.value})"

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "projects": self._projects
        }


class Project:
    def __init__(
        self,
        name: str,
        owner: User,
        description: Optional[str] = None
    ) -> None:
        self.name = name
        self.owner = owner
        self.description = description
        self.created_at: datetime = datetime.now()
        self.is_active: bool = True
        self._members: List[User] = [owner]

    def add_member(self, user: User) -> None:
        usernames = [m.username for m in self._members]
        if user.username not in usernames:
            self._members.append(user)
            user.add_to_project(self.name)
        else:
            print(f"{user.username} is already in {self.name}")

    def get_member_count(self) -> int:
        return len(self._members)

    def __repr__(self) -> str:
        return f"Project(name={self.name}, members={self.get_member_count()})"


if __name__ == "__main__":
    ranveer = User(
        username="ranveer",
        email="ranveer@devcollab.com",
        full_name="Ranveer Mane",
        role=UserRole.ADMIN
    )
    alice = User(
        username="alice",
        email="alice@devcollab.com",
        full_name="Alice Smith"
    )
    project = Project(
        name="DevCollab API",
        owner=ranveer,
        description="Team collaboration platform"
    )
    project.add_member(alice)
    project.add_member(alice)
    print(f"\nProject: {project}")
    print(f"Members: {project.get_member_count()}")
    print(f"\nRanveer's data:")
    print(ranveer.to_dict())
    print(f"\nAlice's projects: {alice.get_projects()}")