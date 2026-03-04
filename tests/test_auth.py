import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Dùng class để lưu trạng thái giữa các bước test (token, refresh token)
class TestAuthFlow:
    access_token = None
    refresh_token = None

    def test_register_user(self):
        register_data = {
            "email": "test_auth@example.com",
            "password": "securepassword123"
        }
        # Endpoint có thể là /api/auth/register hoặc /api/users/register tùy project của bạn
        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code in [201, 400, 409] # 400/409 nếu user đã tồn tại

    def test_login_get_token(self):
        login_data = {
            "username": "test_auth@example.com",
            "password": "securepassword123"
        }
        # Lưu ý: OAuth2 password flow thường dùng form-data thay vì json
        response = client.post(
            "/api/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        
        # Lưu lại token cho các bước sau
        TestAuthFlow.access_token = data["access_token"]
        TestAuthFlow.refresh_token = data["refresh_token"]

    def test_access_protected_me(self):
        headers = {"Authorization": f"Bearer {TestAuthFlow.access_token}"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        assert "email" in response.json()

    def test_refresh_token(self):
        refresh_data = {"refresh_token": TestAuthFlow.refresh_token}
        response = client.post("/api/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_unauthorized_access_blocked(self):
        # Không gửi headers
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_logout(self):
        headers = {"Authorization": f"Bearer {TestAuthFlow.access_token}"}
        response = client.post("/api/auth/logout", headers=headers)
        # Tùy code của bạn trả về 200 hoặc 204
        assert response.status_code in [200, 204]