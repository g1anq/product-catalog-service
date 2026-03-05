import os
import sys
import asyncio
import pytest
import tempfile

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create a temporary test database directory
_test_db_dir = tempfile.mkdtemp(prefix="pytest_db_")
_temp_db_path = os.path.join(_test_db_dir, "test.db")

# Set environment for testing - use temporary SQLite file database
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_temp_db_path.replace(chr(92), '/')}"

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Setup the database for testing."""
    from app.core.database import engine, Base
    
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    try:
        # Create tables before tests
        asyncio.run(create_tables())
        
        yield
    finally:
        # Cleanup after tests
        try:
            asyncio.run(engine.dispose())
            # Clean up the temporary database directory
            if os.path.exists(_temp_db_path):
                os.remove(_temp_db_path)
            if os.path.exists(_test_db_dir):
                os.rmdir(_test_db_dir)
        except:
            pass