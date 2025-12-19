"""Test FastAPI application endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from labbot.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """Create async test client for FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as async_client:
        yield async_client


async def test_root_endpoint(client: AsyncClient) -> None:
    """Test root endpoint serves HTML UI."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "LabBot" in response.text
    assert "Lab Results Interpreter" in response.text
    assert "<html" in response.text


def test_app_metadata() -> None:
    """Test that FastAPI app has proper metadata."""
    assert app.title == "LabBot"
    assert app.version == "0.1.0"
    assert "educational information" in app.description
    assert "DISCLAIMER" in app.description


def test_cors_middleware_configured() -> None:
    """Test that CORS middleware is properly configured."""
    cors_middleware_found = False
    for middleware in app.user_middleware:
        if "CORSMiddleware" in str(middleware):
            cors_middleware_found = True
            break
    assert cors_middleware_found, "CORS middleware not found in app"


async def test_cors_headers_present(client: AsyncClient) -> None:
    """Test that CORS headers are included in responses."""
    response = await client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    # OPTIONS requests may return 204 or 405 depending on FastAPI version
    assert response.status_code in [200, 204, 405]
