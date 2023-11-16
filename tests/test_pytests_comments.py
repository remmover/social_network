from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from main import app

# Import your database models and schemas here

# Replace this with your actual database URL
DATABASE_URL = "sqlite:///./test.db"

# Create a test database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# Create a function to override the dependency for database sessions
def override_get_db():
    with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


# Create a test client for the FastAPI app
client = TestClient(app)


def test_create_comment():
    # Test creating a new comment
    response = client.post(
        "/comments/",
        json={
            "post_id": 1,
            "comment": "This is a test comment."
        }
    )
    assert response.status_code == 200
    # You can add more assertions to check the response content


def test_update_comment():
    # Test updating an existing comment
    response = client.put(
        "/comments/update",
        json={
            "comment_id": 1,
            "post_id": 1,
            "comment": "Updated comment text."
        }
    )
    assert response.status_code == 200
    # You can add more assertions to check the response content


def test_get_comments_for_post():
    # Test getting comments for a specific post
    response = client.get("/comments/posts/1/comments/")
    assert response.status_code == 200
    # You can add more assertions to check the response content


# You can add more tests for other endpoints and functions as needed

if __name__ == "__main__":
    import pytest

    pytest.main()
