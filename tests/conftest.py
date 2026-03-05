import os
import sys
import asyncio
import pytest
import tempfile

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create a temporary test database directory
try:
    _test_db_dir = tempfile.mkdtemp(prefix="pytest_db_")
    _temp_db_path = os.path.join(_test_db_dir, "test.db")
except Exception as e:
    print(f"Warning: Could not create temp database directory: {e}")
    _temp_db_path = "test.db"
    _test_db_dir = None

# Set environment for testing - use temporary SQLite file database
# This MUST be set before ANY app modules are imported
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_temp_db_path.replace(chr(92), '/')}"


def pytest_configure(config):
    """Hook called before test collection - set up environment variables."""
    # DATABASE_URL already set above, but this hook ensures it's set early
    os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{_temp_db_path.replace(chr(92), '/')}")


# Now import app AFTER setting DATABASE_URL
try:
    from app.core.database import engine, Base
except Exception as e:
    print(f"Error importing app.core.database: {e}")
    raise


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Setup the database for testing."""
    
    async def create_tables():
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise
    
    try:
        # Create tables before tests
        asyncio.run(create_tables())
        yield
    finally:
        # Cleanup after tests
        try:
            asyncio.run(engine.dispose())
            # Clean up the temporary database directory
            if _temp_db_path and _temp_db_path != "test.db" and os.path.exists(_temp_db_path):
                os.remove(_temp_db_path)
            if _test_db_dir and os.path.exists(_test_db_dir):
                os.rmdir(_test_db_dir)
        except Exception as e:
            print(f"Error during cleanup: {e}")