import requests
import json

BASE_URL = "http://localhost:8000/api"

def print_section(title: str):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_response(response: requests.Response):
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def main():
    print_section("1. Register a New User")
    
    register_data = {
        "email": "test2@gmail.com",
        "password": "securepassword123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=register_data
    )
    print_response(response)
    
    if response.status_code != 201:
        print("\n⚠️  Registration failed. User might already exist.")
        print("Continuing with login...")
    
    print_section("2. Login (Get Access Token)")
    
    login_data = {
        "username": "testuser@example.com",  
        "password": "securepassword123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data=login_data,  
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print_response(response)
    
    if response.status_code != 200:
        print("\n❌ Login failed. Exiting...")
        return
    
    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    print(f"\n✅ Access Token: {access_token[:50]}...")
    print(f"✅ Refresh Token: {refresh_token[:50]}...")
    
    print_section("3. Access Protected Endpoint (/auth/me)")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"\n✅ Authenticated as: {user_data['email']}")
        print(f"✅ User ID: {user_data['id']}")
        print(f"✅ Is Active: {user_data['is_active']}")
    
    print_section("4. Refresh Access Token")
    
    refresh_data = {
        "refresh_token": refresh_token
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json=refresh_data
    )
    print_response(response)
    
    if response.status_code == 200:
        new_tokens = response.json()
        print(f"\n✅ New Access Token: {new_tokens['access_token'][:50]}...")
        print(f"✅ New Refresh Token: {new_tokens['refresh_token'][:50]}...")
    
    print_section("5. Test Unauthorized Access")
    
    response = requests.get(f"{BASE_URL}/auth/me")
    print_response(response)
    
    if response.status_code == 401:
        print("\n✅ Unauthorized access properly blocked!")
    
    print_section("6. Logout")
    
    response = requests.post(
        f"{BASE_URL}/auth/logout",
        headers=headers
    )
    print_response(response)
    
    print("\n" + "="*60)
    print("  ✅ All Tests Completed!")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure the FastAPI server is running:")
        print("    uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
