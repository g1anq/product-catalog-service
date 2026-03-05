import pytest
from fastapi.testclient import TestClient
from app.main import app  # Đảm bảo đường dẫn này đúng với project của bạn

# Khởi tạo client để test trực tiếp vào logic app
client = TestClient(app)

# Dùng class để nhóm các test lại (Pytest sẽ tự nhận diện các hàm có tiền tố test_)
class TestProductCatalogAPI:
    access_token = None
    task_id = None
    tag_id = None

    def test_user_registration(self):
        response = client.post(
            "/api/users/register",
            json={
                "email": "testuser@example.com",
                "password": "securepassword123"
            }
        )
        # Chấp nhận 201 (tạo mới) hoặc 409 (đã tồn tại)
        assert response.status_code in [201, 409]
        if response.status_code == 201:
            assert "id" in response.json()

    def test_user_login(self):
        response = client.post(
            "/api/auth/token",
            data={
                "username": "testuser@example.com",
                "password": "securepassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        TestProductCatalogAPI.access_token = data["access_token"]

    def test_get_current_user(self):
        headers = {"Authorization": f"Bearer {TestProductCatalogAPI.access_token}"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == "testuser@example.com"

    def test_create_tag(self):
        headers = {"Authorization": f"Bearer {TestProductCatalogAPI.access_token}"}
        response = client.post(
            "/api/tags",
            headers=headers,
            json={"name": "urgent_test"}
        )
        assert response.status_code in [201, 409]
        if response.status_code == 201:
            TestProductCatalogAPI.tag_id = response.json()["id"]

    def test_create_task(self):
        # Ensure we have a token - register and login if needed
        if not TestProductCatalogAPI.access_token:
            # Register user if not exists
            client.post(
                "/api/users/register",
                json={
                    "email": "testuser@example.com",
                    "password": "securepassword123"
                }
            )
            # Login to get token
            response = client.post(
                "/api/auth/token",
                data={
                    "username": "testuser@example.com",
                    "password": "securepassword123"
                }
            )
            assert response.status_code == 200, f"Login failed: {response.json()}"
            TestProductCatalogAPI.access_token = response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {TestProductCatalogAPI.access_token}"}
        response = client.post(
            "/api/tasks",
            headers=headers,
            json={
                "title": "CI/CD Task",
                "description": "Testing coverage",
                "status": "TODO",
                "tag_ids": [TestProductCatalogAPI.tag_id] if TestProductCatalogAPI.tag_id else []
            }
        )
        assert response.status_code == 201, f"Task creation failed: {response.json()}"
        TestProductCatalogAPI.task_id = response.json()["id"]

    def test_unauthorized_access(self):
        # Không gửi token để test lỗi 401
        response = client.get("/api/tasks")
        assert response.status_code == 401

    def test_not_found(self):
        headers = {"Authorization": f"Bearer {TestProductCatalogAPI.access_token}"}
        response = client.get("/api/tasks/99999", headers=headers)
        assert response.status_code == 404