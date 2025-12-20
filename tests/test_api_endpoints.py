"""
Integration tests for Web API endpoints
"""
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from web.routes import router
from web.arena import APIArena
from ipc import IPCManager
import models
from models.base import create_db_and_tables


@pytest.fixture
async def test_app(ipc_queues):
    """Create test FastAPI app."""
    from fastapi.staticfiles import StaticFiles
    command_queue, state_queue = ipc_queues
    
    # Setup IPC
    ipc = IPCManager()
    ipc.command_queue = command_queue
    ipc.state_queue = state_queue
    APIArena.set_ipc(ipc)
    
    # Setup database
    create_db_and_tables()
    
    # Create app
    app = FastAPI()
    # Mount static files (required for templates)
    app.mount('/static', StaticFiles(directory='static'), name='static')
    app.include_router(router)
    
    return app


@pytest.mark.integration
@pytest.mark.asyncio
class TestWebAPIEndpoints:
    """Test Web API endpoints."""
    
    async def test_index_page(self, test_app):
        """Test index page loads."""
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
    
    async def test_match_control_page(self, test_app):
        """Test match control page loads."""
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/match/control")
            assert response.status_code == 200
    
    async def test_load_match_api(self, test_app, ipc_queues, sample_match_data):
        """Test load match API."""
        import time
        command_queue, state_queue = ipc_queues
        
        # Clear any existing commands
        while not command_queue.empty():
            command_queue.get()
        
        # Create a match first
        match = models.Match(**sample_match_data)
        created = models.create_match(match)
        
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Correct path is /api/match/control/load_match/{match_id}
            response = await client.post(
                f"/api/match/control/load_match/{created.id}"
            )
            assert response.status_code == 200
        
        # Small delay to ensure command is sent
        time.sleep(0.1)
        
        # Verify command was sent to IPC
        assert not command_queue.empty(), "Command queue should not be empty"
        cmd = command_queue.get()
        assert cmd["command"] == "load_match"
        assert cmd["payload"]["match_id"] == created.id
    
    async def test_start_match_api(self, test_app, ipc_queues):
        """Test start match API."""
        command_queue, state_queue = ipc_queues
        
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/match/control/start")
            assert response.status_code == 200
        
        # Verify command was sent
        assert not command_queue.empty()
        cmd = command_queue.get()
        assert cmd["command"] == "start_match"
    
    async def test_abort_match_api(self, test_app, ipc_queues):
        """Test abort match API."""
        command_queue, state_queue = ipc_queues
        
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/match/control/abort")
            assert response.status_code == 200
        
        # Verify command was sent
        assert not command_queue.empty()
        cmd = command_queue.get()
        assert cmd["command"] == "abort_match"
    
    async def test_teams_api(self, test_app, sample_team_data):
        """Test teams API."""
        # Create a team
        team = models.Team(**sample_team_data)
        models.create_team(team)
        
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Correct path is /api/setup/teams (no /list)
            response = await client.get("/api/setup/teams")
            assert response.status_code == 200
            
            data = response.json()
            assert len(data) > 0
            assert any(t["id"] == sample_team_data["id"] for t in data)
    
    async def test_event_settings_api(self, test_app):
        """Test event settings API."""
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Get current settings
            response = await client.get("/api/setup/settings")
            assert response.status_code == 200
            
            # Update settings
            response = await client.post(
                "/api/setup/settings",
                json={
                    "name": "Test Event",
                    "num_playoff_alliances": 4,
                }
            )
            assert response.status_code == 200
