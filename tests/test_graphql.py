import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestGraphQLFlow:
    access_token = None
    task_id = None
    tag_id = None

    def test_setup_login(self):
        """Lấy token để thực hiện các truy vấn GraphQL có bảo mật"""
        response = client.post(
            "/api/auth/token",
            data={"username": "testuser@example.com", "password": "securepassword123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            TestGraphQLFlow.access_token = response.json()["access_token"]
        assert response.status_code == 200

    def test_query_me(self):
        query = """
        query {
          me {
            id
            email
          }
        }
        """
        headers = {"Authorization": f"Bearer {TestGraphQLFlow.access_token}"}
        response = client.post("/graphql", json={"query": query}, headers=headers)
        assert response.status_code == 200
        assert "data" in response.json()
        assert response.json()["data"]["me"]["email"] == "testuser@example.com"

    def test_create_tag_mutation(self):
        query = """
        mutation CreateTag($name: String!) {
          createTag(name: $name) {
            id
            name
          }
        }
        """
        variables = {"name": "graphql-test-tag"}
        headers = {"Authorization": f"Bearer {TestGraphQLFlow.access_token}"}
        response = client.post("/graphql", json={"query": query, "variables": variables}, headers=headers)
        
        data = response.json()
        assert response.status_code == 200
        if data.get("data") and data["data"].get("createTag"):
            TestGraphQLFlow.tag_id = data["data"]["createTag"]["id"]
            assert data["data"]["createTag"]["name"] == "graphql-test-tag"

    def test_create_task_mutation(self):
        # Ensure we have a token - register and login if needed
        if not TestGraphQLFlow.access_token:
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
                data={"username": "testuser@example.com", "password": "securepassword123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            assert response.status_code == 200, f"Login failed: {response.json()}"
            TestGraphQLFlow.access_token = response.json()["access_token"]
        
        query = """
        mutation CreateTask($input: CreateTaskInput!) {
          createTask(input: $input) {
            id
            title
            status
          }
        }
        """
        variables = {
            "input": {
                "title": "GraphQL Task",
                "description": "Created via GitHub Actions",
                "status": "TODO",
                "tagIds": [TestGraphQLFlow.tag_id] if TestGraphQLFlow.tag_id else []
            }
        }
        headers = {"Authorization": f"Bearer {TestGraphQLFlow.access_token}"}
        response = client.post("/graphql", json={"query": query, "variables": variables}, headers=headers)
        
        assert response.status_code == 200, f"GraphQL error: {response.json()}"
        data = response.json()
        assert data["data"]["createTask"]["title"] == "GraphQL Task"
        TestGraphQLFlow.task_id = data["data"]["createTask"]["id"]

    def test_query_tasks(self):
        query = """
        query {
          tasks {
            id
            title
          }
        }
        """
        headers = {"Authorization": f"Bearer {TestGraphQLFlow.access_token}"}
        response = client.post("/graphql", json={"query": query}, headers=headers)
        assert response.status_code == 200
        assert len(response.json()["data"]["tasks"]) >= 1

    def test_unauthorized_graphql_query(self):
        query = "{ tasks { id } }"
        # Không gửi token
        response = client.post("/graphql", json={"query": query})
        # GraphQL thường trả về 200 nhưng kèm danh sách errors: "not authenticated"
        assert "errors" in response.json() or response.status_code == 401