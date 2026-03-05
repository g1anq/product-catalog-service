import os
import sys
import asyncio
import pytest

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get temp paths from root conftest.py (set via environment variables)
_temp_db_path = os.environ.get("_TEMP_DB_PATH")
_test_db_dir = os.environ.get("_TEST_DB_DIR")

# DATABASE_URL should already be set by root conftest.py before any imports
# Import app modules AFTER sys.path and DATABASE_URL are set
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
                try:
                    os.remove(_temp_db_path)
                except:
                    pass
            if _test_db_dir and os.path.exists(_test_db_dir):
                try:
                    os.rmdir(_test_db_dir)
                except:
                    pass
        except Exception as e:
            print(f"Error during cleanup: {e}")