"""
Pytest configuration and fixtures for Pengiloo tests
"""
import asyncio
import multiprocessing
import pytest
from pathlib import Path

# Set test database path
TEST_DB_PATH = Path(__file__).parent / "test_pengiloo.db"


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use the same event loop policy for all tests."""
    return asyncio.get_event_loop_policy()


@pytest.fixture(scope="session")
def test_db_path():
    """Provide test database path."""
    return TEST_DB_PATH


@pytest.fixture(autouse=True)
def setup_test_db(test_db_path):
    """Setup and teardown test database for each test."""
    # Remove existing test database
    if test_db_path.exists():
        test_db_path.unlink()
    
    yield
    
    # Cleanup after test
    if test_db_path.exists():
        test_db_path.unlink()


@pytest.fixture
def ipc_queues():
    """Create IPC queues for testing."""
    command_queue = multiprocessing.Queue()
    state_queue = multiprocessing.Queue()
    return command_queue, state_queue


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "name": "Test Event 2024",
        "playoff_type": 0,
        "num_playoff_alliances": 8,
        "tba_event_code": "2024test",
    }


@pytest.fixture
def sample_team_data():
    """Sample team data for testing."""
    return {
        "id": 1234,
        "name": "Test Team",
        "nickname": "Test",
        "city": "Test City",
        "state_prov": "TS",
        "country": "Test Country",
    }


@pytest.fixture
def sample_match_data():
    """Sample match data for testing."""
    return {
        "type": 1,  # QUALIFICATION
        "type_order": 1,
        "red1": 1234,
        "red2": 5678,
        "red3": 9012,
        "blue1": 3456,
        "blue2": 7890,
        "blue3": 1357,
    }
