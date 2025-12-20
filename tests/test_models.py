"""
Unit tests for SQLModel models
"""
import pytest
from sqlmodel import Session, select
import models
from models.base import engine, create_db_and_tables


@pytest.mark.unit
class TestEventModel:
    """Test Event model CRUD operations."""
    
    @pytest.fixture(autouse=True)
    def setup(self, setup_test_db):
        """Setup database for each test."""
        from sqlmodel import Session, select
        from models.base import engine
        create_db_and_tables()
        # Clean up rankings table before each test
        with Session(engine) as session:
            statement = select(models.Ranking)
            results = session.exec(statement)
            for ranking in results:
                session.delete(ranking)
            session.commit()
        # Clean up matches table before each test
        models.truncate_matches()
        yield
    
    def test_read_event_settings_default(self):
        """Test reading default event settings."""
        event = models.read_event_settings()
        assert event is not None
        # Event may have been modified by previous tests, just check it exists
        assert event.num_playoff_alliances >= 4
    
    def test_update_event_settings(self, sample_event_data):
        """Test updating event settings."""
        event = models.read_event_settings()
        event.name = sample_event_data["name"]
        event.tba_event_code = sample_event_data["tba_event_code"]
        
        updated = models.update_event_settings(event)
        assert updated is not None
        assert updated.name == sample_event_data["name"]
        assert updated.tba_event_code == sample_event_data["tba_event_code"]


@pytest.mark.unit
class TestTeamModel:
    """Test Team model CRUD operations."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup database for each test."""
        create_db_and_tables()
        # Clean up teams table before each test
        models.truncate_teams()
        yield
    
    def test_create_team(self, sample_team_data):
        """Test creating a team."""
        team = models.Team(**sample_team_data)
        created = models.create_team(team)
        
        assert created is not None
        assert created.id == sample_team_data["id"]
        assert created.name == sample_team_data["name"]
    
    def test_create_duplicate_team(self, sample_team_data):
        """Test creating duplicate team returns None."""
        team1 = models.Team(**sample_team_data)
        models.create_team(team1)
        
        team2 = models.Team(**sample_team_data)
        result = models.create_team(team2)
        assert result is None
    
    def test_read_team_by_id(self, sample_team_data):
        """Test reading team by ID."""
        team = models.Team(**sample_team_data)
        models.create_team(team)
        
        found = models.read_team_by_id(sample_team_data["id"])
        assert found is not None
        assert found.id == sample_team_data["id"]
        assert found.name == sample_team_data["name"]
    
    def test_read_team_by_id_not_found(self):
        """Test reading non-existent team."""
        found = models.read_team_by_id(99999)
        assert found is None
    
    def test_read_team_by_id_null(self):
        """Test reading team with null ID."""
        found = models.read_team_by_id(0)
        assert found is None
    
    def test_read_all_teams(self, sample_team_data):
        """Test reading all teams."""
        # Create multiple teams
        for i in range(3):
            team_data = sample_team_data.copy()
            team_data["id"] = 1000 + i
            team_data["name"] = f"Team {1000 + i}"
            team = models.Team(**team_data)
            models.create_team(team)
        
        teams = models.read_all_teams()
        assert len(teams) >= 3
    
    def test_update_team(self, sample_team_data):
        """Test updating team."""
        team = models.Team(**sample_team_data)
        models.create_team(team)
        
        team.nickname = "Updated Nickname"
        updated = models.update_team(team)
        
        assert updated is not None
        assert updated.nickname == "Updated Nickname"
    
    def test_delete_team(self, sample_team_data):
        """Test deleting team."""
        team = models.Team(**sample_team_data)
        models.create_team(team)
        
        models.delete_team(team.id)
        
        found = models.read_team_by_id(team.id)
        assert found is None


@pytest.mark.unit
class TestMatchModel:
    """Test Match model CRUD operations."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup database for each test."""
        create_db_and_tables()
        # Clean up matches table before each test
        models.truncate_matches()
        yield
    
    def test_create_match(self, sample_match_data):
        """Test creating a match."""
        match = models.Match(**sample_match_data)
        created = models.create_match(match)
        
        assert created is not None
        assert created.type == sample_match_data["type"]
        assert created.red1 == sample_match_data["red1"]
        assert created.blue1 == sample_match_data["blue1"]
    
    def test_read_match_by_id(self, sample_match_data):
        """Test reading match by ID."""
        match = models.Match(**sample_match_data)
        created = models.create_match(match)
        
        found = models.read_match_by_id(created.id)
        assert found is not None
        assert found.id == created.id
        assert found.red1 == sample_match_data["red1"]
    
    def test_update_match(self, sample_match_data):
        """Test updating match."""
        from game.score_summary import MatchStatus
        match = models.Match(**sample_match_data)
        created = models.create_match(match)
        
        created.status = MatchStatus.RED_WON_MATCH
        updated = models.update_match(created)
        
        assert updated is not None
        assert updated.status == MatchStatus.RED_WON_MATCH
    
    def test_delete_match(self, sample_match_data):
        """Test deleting match."""
        match = models.Match(**sample_match_data)
        created = models.create_match(match)
        
        success = models.delete_match(created.id)
        assert success is True
        
        found = models.read_match_by_id(created.id)
        assert found is None


@pytest.mark.unit
class TestRankingModel:
    """Test Ranking model CRUD operations."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup database for each test."""
        from sqlmodel import Session, select
        from models.base import engine
        
        create_db_and_tables()
        # Clean up rankings table before each test
        with Session(engine) as session:
            statement = select(models.Ranking)
            for ranking in session.exec(statement):
                session.delete(ranking)
            session.commit()
        yield
    
    def test_create_ranking(self):
        """Test creating a ranking."""
        # First ensure no existing ranking with this team_id
        with Session(engine) as session:
            existing = session.get(models.Ranking, 1234)
            if existing:
                session.delete(existing)
                session.commit()
        
        ranking = models.Ranking(
            team_id=1234,
            rank=1,
            ranking_points=100,
            wins=10,
            losses=2,
            ties=1,
        )
        created = models.create_ranking(ranking)
        
        assert created is not None
        assert created.team_id == 1234
        assert created.rank == 1
    
    def test_read_ranking_for_team(self):
        """Test reading ranking for team."""
        # Clean up first
        with Session(engine) as session:
            existing = session.get(models.Ranking, 5678)
            if existing:
                session.delete(existing)
                session.commit()
        
        ranking = models.Ranking(team_id=5678, rank=5)
        models.create_ranking(ranking)
        
        found = models.read_ranking_for_team(5678)
        assert found is not None
        assert found.team_id == 5678
        assert found.rank == 5
    
    def test_read_ranking_for_team_null(self):
        """Test reading ranking with null team_id."""
        found = models.read_ranking_for_team(0)
        assert found is None
    
    def test_update_ranking(self):
        """Test updating ranking."""
        ranking = models.Ranking(team_id=1234, rank=5, wins=3)
        models.create_ranking(ranking)
        
        ranking.wins = 10
        ranking.rank = 1
        updated = models.update_ranking(ranking)
        
        assert updated is not None
        assert updated.wins == 10
        assert updated.rank == 1
