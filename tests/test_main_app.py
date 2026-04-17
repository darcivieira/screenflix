from fastapi.testclient import TestClient

from screenflix.main import app


def test_main_app_healthz_route():
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_main_app_registers_middlewares_and_api_prefix():
    middleware_classes = [m.cls.__name__ for m in app.user_middleware]
    paths = {route.path for route in app.routes}

    assert "CORSMiddleware" in middleware_classes
    assert "RequestLogMiddleware" in middleware_classes
    assert any(path.startswith("/api/v1/media") for path in paths)
