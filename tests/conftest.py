import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db_models import Base 
from src.main import app
from fastapi.testclient import TestClient
from src.main import app, get_db
# Use SQLite for testing (simple & fast)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables before tests
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Override DB dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides = {}
app.dependency_overrides[get_db] = override_get_db

# Test client
@pytest.fixture()
def client():
    return TestClient(app)