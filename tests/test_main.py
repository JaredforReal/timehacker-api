from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """
    测试健康检查端点
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data
    assert "version" in data


def test_api_root():
    """
    测试API根端点
    """
    response = client.get("/api/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
