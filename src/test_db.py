from src.config.database import SessionLocal
from src.db_models import User, Project, Task, UserRoleEnum

def test_database_operations():
    db = SessionLocal()

    try:
        print("== Creating users ==")
        ranveer = User(
            username = "ranveer",
            email = "ranveer@devcollab.com",
            full_name = "Ranveer Mane",
            password_hash = "hashed_password_here",
            role = UserRoleEnum.ADMIN
        )
        alice = User(
            username="alice",
            email="alice@devcollab.com",
            full_name="Alice Smith",
            password_hash="hashed_password_here",
            role=UserRoleEnum.MEMBER 
        )

        db.add(ranveer)
        db.add(alice)
        db.commit()
        db.refresh(ranveer)
        db.refresh(alice)
        print(f"Created: {ranveer}")
        print(f"Created: {alice}")
        print(f"Ranveer's ID: {ranveer.id}")

        print("\n=== Creating project ===")
        project = Project(
            name="DevCollab API",
            description="Team collaboration platform",
            max_members=10,
            owner_id=ranveer.id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"Created: {project}")

        print("\n=== Creating tasks ===")
        task1 = Task(
            title="Set up database",
            priority="high",
            project_id=project.id,
            assigned_to=ranveer.id
        )
        task2 = Task(
            title="Write API endpoints",
            priority="medium",
            project_id=project.id,
            assigned_to=alice.id
        )
        task3 = Task(
            title="Deploy to AWS",
            priority="low",
            project_id=project.id
        )
        db.add_all([task1, task2, task3])
        db.commit()


        print("\n=== Reading data ===")

        # Get all users
        all_users = db.query(User).all()
        print(f"All users: {all_users}")

        # Get user by username
        user = db.query(User).filter(User.username == "ranveer").first()
        print(f"Found user: {user}")

        # Get user's projects using relationship
        print(f"Ranveer's projects: {user.owned_projects}")

        # Get project's tasks using relationship
        print(f"Project tasks: {project.tasks}")

        # Filter tasks by priority
        high_tasks = db.query(Task).filter(Task.priority == "high").all()
        print(f"High priority tasks: {high_tasks}")

        # ── UPDATE ─────────────────────────────────────────────
        print("\n=== Updating data ===")
        task1.is_completed = True
        db.commit()
        print(f"Task1 completed: {task1.is_completed}")

        # ── DELETE (soft) ──────────────────────────────────────
        print("\n=== Soft delete user ===")
        alice.is_active = False
        db.commit()
        print(f"Alice active: {alice.is_active}")

        # Query only active users
        active_users = db.query(User).filter(User.is_active == True).all()
        print(f"Active users: {active_users}")

        print("\n=== All operations successful ===")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    test_database_operations()