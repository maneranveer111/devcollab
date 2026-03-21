from typing import Optional, List, Dict, Any
from datetime import datetime

project_name: str = "DevCollab"
version: float = 1.0
is_active: bool = True
max_members: int = 50
description: Optional[str] = None
team_members: List[str] = ["Ranveer", "Alice", "Bob"]
config: Dict[str, Any] = {
    "debug": True,
    "max_connections": 100,
    "database_url": "postgresql://localhost/devcollab"
}
MAX_FILE_SIZE_MB: int = 10
ALLOWED_EXTENSIONS: List[str] = [".jpg", ".png", ".pdf", ".docx"]

print(f"Starting {project_name} v{version}")
print(f"Active: {is_active}")
print(f"Team: {team_members}")
print(f"Max file size: {MAX_FILE_SIZE_MB}MB")

def create_project(
    name: str,
    owner: str,
    description: Optional[str] = None,
    max_members: int = 10
) -> Dict[str, Any]:
    """
    Create a new project in DevCollab.
    Args:
        name: The project name
        owner: Username of the project owner
        description: Optional project description
        max_members: Maximum team size (default 10)
    Returns:
        A dictionary containing the project data
    """
    if not name or not name.strip():
        raise ValueError("Project name cannot be empty")
    if max_members < 1 or max_members > 100:
        raise ValueError("max_members must be between 1 and 100")
    return {
        "id": 1,
        "name": name.strip(),
        "owner": owner,
        "description": description,
        "max_members": max_members,
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }

def get_project_summary(project: Dict[str, Any]) -> str:
    """Return a human-readable summary of a project."""
    desc = project.get("description") or "No description provided"
    return (
        f"Project: {project['name']}\n"
        f"Owner: {project['owner']}\n"
        f"Description: {desc}\n"
        f"Max members: {project['max_members']}\n"
        f"Created: {project['created_at']}"
    )

if __name__ == "__main__":
    project = create_project(
        name="DevCollab API",
        owner="Ranveer",
        description="Team collaboration platform"
    )
    print(get_project_summary(project))
    try:
        bad_project = create_project(name="", owner="Ranveer")
    except ValueError as e:
        print(f"\nCaught error: {e}")