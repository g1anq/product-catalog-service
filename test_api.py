import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000/api"


class APITester:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.task_id: Optional[int] = None
        self.tag_id: Optional[int] = None
    
    def print_section(self, title: str):
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def print_response(self, response: requests.Response, show_body: bool = True):
        status_emoji = "✅" if 200 <= response.status_code < 300 else "❌"
        print(f"{status_emoji} Status Code: {response.status_code}")
        
        if show_body:
            try:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Response: {response.text}")
    
    def get_headers(self) -> dict:
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}
    
    def test_user_registration(self):
        self.print_section("1. User Registration")
        
        response = requests.post(
            f"{BASE_URL}/users/register",
            json={
                "email": "testuser@example.com",
                "password": "securepassword123"
            }
        )
        self.print_response(response)
        
        if response.status_code == 201:
            self.user_id = response.json()["id"]
            print(f"✅ User created with ID: {self.user_id}")
        elif response.status_code == 409:
            print("⚠️  User already exists, continuing with login...")
    
    def test_user_login(self):
        self.print_section("2. User Login")
        
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={
                "username": "testuser@example.com",
                "password": "securepassword123"
            }
        )
        self.print_response(response)
        
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens["access_token"]
            print(f"✅ Access Token: {self.access_token[:50]}...")
    
    def test_get_current_user(self):
        self.print_section("3. Get Current User (/users/me)")
        
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers=self.get_headers()
        )
        self.print_response(response)
        
        if response.status_code == 200:
            user = response.json()
            self.user_id = user["id"]
            print(f"✅ Logged in as: {user['email']} (ID: {user['id']})")
    
    def test_update_user(self):
        self.print_section("4. Update User Profile")
        
        response = requests.put(
            f"{BASE_URL}/users/me",
            headers=self.get_headers(),
            json={
                "email": "testuser@example.com"
            }
        )
        self.print_response(response)
    
    def test_create_tag(self):
        self.print_section("5. Create Tag")
        
        response = requests.post(
            f"{BASE_URL}/tags",
            headers=self.get_headers(),
            json={"name": "urgent"}
        )
        self.print_response(response)
        
        if response.status_code == 201:
            self.tag_id = response.json()["id"]
            print(f"✅ Tag created with ID: {self.tag_id}")
        elif response.status_code == 409:
            print("⚠️  Tag already exists")
            response = requests.get(
                f"{BASE_URL}/tags",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                tags = response.json()
                for tag in tags:
                    if tag["name"] == "urgent":
                        self.tag_id = tag["id"]
                        print(f"✅ Using existing tag ID: {self.tag_id}")
                        break
    
    def test_create_task(self):
        self.print_section("6. Create Task")
        
        response = requests.post(
            f"{BASE_URL}/tasks",
            headers=self.get_headers(),
            json={
                "title": "Complete API implementation",
                "description": "Implement all REST endpoints",
                "status": "TODO",
                "tag_ids": [self.tag_id] if self.tag_id else []
            }
        )
        self.print_response(response)
        
        if response.status_code == 201:
            self.task_id = response.json()["id"]
            print(f"✅ Task created with ID: {self.task_id}")
    
    def test_list_tasks(self):
        self.print_section("7. List Tasks")
        
        response = requests.get(
            f"{BASE_URL}/tasks",
            headers=self.get_headers()
        )
        self.print_response(response)
    
    def test_get_task(self):
        self.print_section("8. Get Specific Task")
        
        if not self.task_id:
            print("⚠️  No task ID available, skipping...")
            return
        
        response = requests.get(
            f"{BASE_URL}/tasks/{self.task_id}",
            headers=self.get_headers()
        )
        self.print_response(response)
    
    def test_update_task(self):
        self.print_section("9. Update Task")
        
        if not self.task_id:
            print("⚠️  No task ID available, skipping...")
            return
        
        response = requests.put(
            f"{BASE_URL}/tasks/{self.task_id}",
            headers=self.get_headers(),
            json={
                "title": "Complete API implementation - UPDATED",
                "status": "IN_PROGRESS"
            }
        )
        self.print_response(response)
    
    def test_add_tags_to_task(self):
        self.print_section("10. Add Tags to Task")
        
        if not self.task_id or not self.tag_id:
            print("⚠️  No task/tag ID available, skipping...")
            return
        
        response = requests.post(
            f"{BASE_URL}/tasks/{self.task_id}/tags",
            headers=self.get_headers(),
            json=[self.tag_id]
        )
        self.print_response(response)
    
    def test_list_tags(self):
        self.print_section("11. List Tags")
        
        response = requests.get(
            f"{BASE_URL}/tags",
            headers=self.get_headers()
        )
        self.print_response(response)
    
    def test_search_tags(self):
        self.print_section("12. Search Tags")
        
        response = requests.get(
            f"{BASE_URL}/tags?search=urg",
            headers=self.get_headers()
        )
        self.print_response(response)
    
    def test_unauthorized_access(self):
        self.print_section("13. Test Unauthorized Access (401)")
        
        response = requests.get(f"{BASE_URL}/tasks")
        self.print_response(response)
        
        if response.status_code == 401:
            print("✅ Correctly returned 401 Unauthorized")
    
    def test_validation_error(self):
        self.print_section("14. Test Validation Error (422)")
        
        response = requests.post(
            f"{BASE_URL}/tasks",
            headers=self.get_headers(),
            json={
                "title": "", 
                "status": "INVALID_STATUS"
            }
        )
        self.print_response(response)
        
        if response.status_code == 422:
            print("✅ Correctly returned 422 Validation Error")
    
    def test_not_found(self):
        self.print_section("15. Test Not Found (404)")
        
        response = requests.get(
            f"{BASE_URL}/tasks/99999",
            headers=self.get_headers()
        )
        self.print_response(response)
        
        if response.status_code == 404:
            print("✅ Correctly returned 404 Not Found")
    
    def test_delete_task(self):
        self.print_section("16. Delete Task")
        
        if not self.task_id:
            print("⚠️  No task ID available, skipping...")
            return
        
        response = requests.delete(
            f"{BASE_URL}/tasks/{self.task_id}",
            headers=self.get_headers()
        )
        self.print_response(response, show_body=False)
        
        if response.status_code == 204:
            print("✅ Task deleted successfully")
    
    def run_all_tests(self):
        print("\n" + "🚀" * 35)
        print("  COMPREHENSIVE API TEST SUITE")
        print("🚀" * 35)
        
        try:
            self.test_user_registration()
            self.test_user_login()
            self.test_get_current_user()
            self.test_update_user()
            self.test_create_tag()
            self.test_create_task()
            self.test_list_tasks()
            self.test_get_task()
            self.test_update_task()
            self.test_add_tags_to_task()
            self.test_list_tags()
            self.test_search_tags()
            self.test_unauthorized_access()
            self.test_validation_error()
            self.test_not_found()
            self.test_delete_task()
            
            print("\n" + "="*70)
            print("  ✅ ALL TESTS COMPLETED!")
            print("="*70)
            
        except requests.exceptions.ConnectionError:
            print("\n❌ Error: Could not connect to the server.")
            print("Make sure the FastAPI server is running:")
            print("    uvicorn app.main:app --reload")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
