import pytest
from test_api import APITester # Import từ file tester của bạn

@pytest.fixture
def tester():
    return APITester()

def test_full_api_workflow(tester):
    # Biến các lệnh in ấn thành hàm test
    # Thay đổi BASE_URL bên trong test_api.py thành URL của môi trường test nếu cần
    try:
        tester.test_user_registration()
        tester.test_user_login()
        tester.test_get_current_user()
        # Thêm các bước khác...
        assert True 
    except Exception as e:
        pytest.fail(f"API Workflow failed: {e}")