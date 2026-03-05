"""
Root conftest.py - runs BEFORE any tests are collected
This ensures DATABASE_URL and other environment variables are set early
"""
import os
import tempfile

# Create a temporary test database directory
try:
    _test_db_dir = tempfile.mkdtemp(prefix="pytest_db_")
    _temp_db_path = os.path.join(_test_db_dir, "test.db")
    
    # Set environment for testing - use temporary SQLite file database
    db_url = f"sqlite+aiosqlite:///{_temp_db_path.replace(chr(92), '/')}"
    os.environ["DATABASE_URL"] = db_url
    os.environ["_TEST_DB_DIR"] = _test_db_dir
    os.environ["_TEMP_DB_PATH"] = _temp_db_path
    
except Exception as e:
    print(f"Warning: Could not create temp database: {e}")
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///test.db")
