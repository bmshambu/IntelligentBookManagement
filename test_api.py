import pytest
from httpx import AsyncClient
from app_async import app  
import base64
from sqlalchemy.sql import text
import pytest
import base64
from httpx import AsyncClient
from app_async import app, async_session  

# Setup credentials for basic authentication
username = "admin"
password = "password123"
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# Headers to use in the tests
auth_headers = {
    "Authorization": f"Basic {encoded_credentials}"
}

@pytest.mark.asyncio
async def test_get_book_success():
    # Insert a test book into the database
    async with async_session() as session:
        stmt = text("INSERT INTO books (title, author, genre, year_published, summary) "
                    "VALUES (:title, :author, :genre, :year_published, :summary) "
                    "RETURNING id")
        result = await session.execute(stmt, {
            "title": "Test Book",
            "author": "Test Author",
            "genre": "Fiction",
            "year_published": 2022,
            "summary": "This is a test summary."
        })
        book_id = result.scalar_one()
        await session.commit()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"/books/{book_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Test Book"
        assert response.json()["author"] == "Test Author"


@pytest.mark.asyncio
async def test_get_book_authentication_required():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/books/1",  # Assuming there's a book with ID 1
        )
        assert response.status_code == 401
        assert response.json()["message"] == "Authentication required."

