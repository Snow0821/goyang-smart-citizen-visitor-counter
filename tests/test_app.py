from fastapi.testclient import TestClient

import app as app_module


client = TestClient(app_module.app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_visit_endpoint_returns_incremented_count(monkeypatch) -> None:
    async def fake_increment_page_view(page_key: str = "home") -> int:
        assert page_key == "home"
        return 7

    monkeypatch.setattr(app_module, "increment_page_view", fake_increment_page_view)

    response = client.post("/api/visit")

    assert response.status_code == 200
    assert response.json() == {"count": 7}


def test_home_page_is_served() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "김시민의 한 페이지 소개" in response.text
