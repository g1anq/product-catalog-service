import requests
import json

BASE_URL = "http://localhost:8000"
GRAPHQL_URL = f"{BASE_URL}/graphql"
AUTH_URL = f"{BASE_URL}/api/auth/token"


class GraphQLTester:
    def __init__(self):
        self.access_token = None
        self.task_id = None
        self.tag_id = None
    
    def print_section(self, title: str):
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def print_response(self, response: dict):
        if "errors" in response:
            print("❌ Errors:")
            for error in response["errors"]:
                print(f"  - {error.get('message', error)}")
        
        if "data" in response:
            print("✅ Data:")
            print(json.dumps(response["data"], indent=2))
    
    def execute_graphql(self, query: str, variables: dict = None):
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(
            GRAPHQL_URL,
            json=payload,
            headers=headers
        )
        
        return response.json()
    
    def test_login(self):
        self.print_section("1. Login (REST API)")
        
        response = requests.post(
            AUTH_URL,
            data={
                "username": "testuser@example.com",
                "password": "securepassword123"
            }
        )
        
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens["access_token"]
            print(f"✅ Access Token: {self.access_token[:50]}...")
        else:
            print(f"❌ Login failed: {response.text}")
            print("⚠️  Make sure to register first or run test_api.py")
    
    def test_query_me(self):
        self.print_section("2. Query: me")
        
        query = """
        query {
          me {
            id
            email
            isActive
            createdAt
          }
        }
        """
        
        result = self.execute_graphql(query)
        self.print_response(result)
    
    def test_query_users(self):
        self.print_section("3. Query: users")
        
        query = """
        query {
          users {
            id
            email
            isActive
          }
        }
        """
        
        result = self.execute_graphql(query)
        self.print_response(result)
    
    def test_create_tag(self):
        self.print_section("4. Mutation: createTag")
        
        query = """
        mutation CreateTag($name: String!) {
          createTag(name: $name) {
            id
            name
          }
        }
        """
        
        result = self.execute_graphql(query, {"name": "graphql-test"})
        self.print_response(result)
        
        if "data" in result and result["data"] and result["data"].get("createTag"):
            self.tag_id = result["data"]["createTag"]["id"]
            print(f"✅ Tag ID: {self.tag_id}")
        elif "errors" in result and any("already exists" in e["message"] for e in result["errors"]):
            print("⚠️  Tag already exists, fetching existing tag...")
            query = """
            query {
              tags {
                id
                name
              }
            }
            """
            result = self.execute_graphql(query)
            if "data" in result and result["data"]:
                for tag in result["data"]["tags"]:
                    if tag["name"] == "graphql-test":
                        self.tag_id = tag["id"]
                        print(f"✅ Found existing Tag ID: {self.tag_id}")
                        break
    
    def test_query_tags(self):
        self.print_section("5. Query: tags")
        
        query = """
        query {
          tags {
            id
            name
          }
        }
        """
        
        result = self.execute_graphql(query)
        self.print_response(result)
    
    def test_create_task(self):
        self.print_section("6. Mutation: createTask")
        
        query = """
        mutation CreateTask($input: CreateTaskInput!) {
          createTask(input: $input) {
            id
            title
            description
            status
            ownerId
            tags {
              id
              name
            }
          }
        }
        """
        
        variables = {
            "input": {
                "title": "GraphQL Test Task",
                "description": "Testing GraphQL mutations",
                "status": "TODO",
                "tagIds": [self.tag_id] if self.tag_id else []
            }
        }
        
        result = self.execute_graphql(query, variables)
        self.print_response(result)
        
        if "data" in result and result["data"] and result["data"].get("createTask"):
            self.task_id = result["data"]["createTask"]["id"]
            print(f"✅ Task ID: {self.task_id}")
    
    def test_query_tasks(self):
        self.print_section("7. Query: tasks")
        
        query = """
        query GetTasks($status: String, $limit: Int) {
          tasks(status: $status, limit: $limit) {
            id
            title
            description
            status
            tags {
              id
              name
            }
          }
        }
        """
        
        result = self.execute_graphql(query, {"status": "TODO", "limit": 10})
        self.print_response(result)
    
    def test_query_task(self):
        self.print_section("8. Query: task")
        
        if not self.task_id:
            print("⚠️  No task ID available, skipping...")
            return
        
        query = """
        query GetTask($taskId: Int!) {
          task(taskId: $taskId) {
            id
            title
            description
            status
            tags {
              id
              name
            }
          }
        }
        """
        
        result = self.execute_graphql(query, {"taskId": self.task_id})
        self.print_response(result)
    
    def test_query_tasks_by_tag(self):
        self.print_section("9. Query: tasksByTag")
        
        query = """
        query GetTasksByTag($tagName: String!, $limit: Int) {
          tasksByTag(tagName: $tagName, limit: $limit) {
            id
            title
            status
            tags {
              id
              name
            }
          }
        }
        """
        
        result = self.execute_graphql(query, {"tagName": "graphql-test", "limit": 10})
        self.print_response(result)
    
    def test_update_task(self):
        self.print_section("10. Mutation: updateTask")
        
        if not self.task_id:
            print("⚠️  No task ID available, skipping...")
            return
        
        query = """
        mutation UpdateTask($taskId: Int!, $input: UpdateTaskInput!) {
          updateTask(taskId: $taskId, input: $input) {
            id
            title
            description
            status
            tags {
              id
              name
            }
          }
        }
        """
        
        variables = {
            "taskId": self.task_id,
            "input": {
                "title": "Updated GraphQL Task",
                "status": "IN_PROGRESS"
            }
        }
        
        result = self.execute_graphql(query, variables)
        self.print_response(result)
    
    def test_add_tag_to_task(self):
        self.print_section("11. Mutation: addTagToTask")
        
        if not self.task_id or not self.tag_id:
            print("⚠️  No task/tag ID available, skipping...")
            return
        
        query = """
        mutation AddTagToTask($input: AddTagToTaskInput!) {
          addTagToTask(input: $input) {
            id
            title
            tags {
              id
              name
            }
          }
        }
        """
        
        variables = {
            "input": {
                "taskId": self.task_id,
                "tagId": self.tag_id
            }
        }
        
        result = self.execute_graphql(query, variables)
        self.print_response(result)
    
    def test_remove_tag_from_task(self):
        self.print_section("12. Mutation: removeTagFromTask")
        
        if not self.task_id or not self.tag_id:
            print("⚠️  No task/tag ID available, skipping...")
            return
        
        query = """
        mutation RemoveTagFromTask($taskId: Int!, $tagId: Int!) {
          removeTagFromTask(taskId: $taskId, tagId: $tagId) {
            id
            title
            tags {
              id
              name
            }
          }
        }
        """
        
        variables = {
            "taskId": self.task_id,
            "tagId": self.tag_id
        }
        
        result = self.execute_graphql(query, variables)
        self.print_response(result)
    
    def test_unauthorized_query(self):
        self.print_section("13. Test Unauthorized Query")
        
        original_token = self.access_token
        self.access_token = None
        
        query = """
        query {
          tasks {
            id
          }
        }
        """
        
        result = self.execute_graphql(query)
        self.print_response(result)
        
        if "errors" in result:
            print("✅ Correctly returned error for unauthenticated request")
        
        self.access_token = original_token
    
    def test_delete_task(self):
        self.print_section("14. Mutation: deleteTask")
        
        if not self.task_id:
            print("⚠️  No task ID available, skipping...")
            return
        
        query = """
        mutation DeleteTask($taskId: Int!) {
          deleteTask(taskId: $taskId)
        }
        """
        
        result = self.execute_graphql(query, {"taskId": self.task_id})
        self.print_response(result)
        
        if "data" in result and result["data"] and result["data"].get("deleteTask"):
            print("✅ Task deleted successfully")
    
    def run_all_tests(self):
        print("\n" + "🚀" * 35)
        print("  GRAPHQL API TEST SUITE")
        print("🚀" * 35)
        
        try:
            self.test_login()
            
            if not self.access_token:
                print("\n❌ Cannot proceed without access token")
                print("Please run: python test_api.py first to create a user")
                return
            
            self.test_query_me()
            self.test_query_users()
            self.test_create_tag()
            self.test_query_tags()
            self.test_create_task()
            self.test_query_tasks()
            self.test_query_task()
            self.test_query_tasks_by_tag()
            self.test_update_task()
            self.test_add_tag_to_task()
            self.test_remove_tag_from_task()
            self.test_unauthorized_query()
            self.test_delete_task()
            
            print("\n" + "="*70)
            print("  ✅ ALL GRAPHQL TESTS COMPLETED!")
            print("="*70)
            print("\n💡 Tip: Open http://localhost:8000/graphql in your browser")
            print("   to use the interactive GraphiQL interface!")
            
        except requests.exceptions.ConnectionError:
            print("\n❌ Error: Could not connect to the server.")
            print("Make sure the FastAPI server is running:")
            print("    uvicorn app.main:app --reload")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    tester = GraphQLTester()
    tester.run_all_tests()
