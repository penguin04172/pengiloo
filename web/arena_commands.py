"""
Helper functions for sending commands to Arena via IPC.
These functions provide a clean API for web routes to interact with the Arena process.
"""
from web.arena import APIArena


def load_match(match_id: int):
    """Load a match into the Arena."""
    APIArena.send_command('load_match', {'match_id': match_id})


def start_match():
    """Start the current match."""
    APIArena.send_command('start_match')


def abort_match():
    """Abort the current match."""
    APIArena.send_command('abort_match')


def commit_scores():
    """Commit scores for the current match."""
    APIArena.send_command('commit_scores')


def load_test_match():
    """Load a test match."""
    APIArena.send_command('load_test_match')


def set_audience_display(mode: str):
    """
    Set the audience display mode.
    
    Args:
        mode: Display mode (e.g., 'blank', 'match', 'logo', etc.)
    """
    APIArena.send_command('set_audience_display', {'mode': mode})


def substitute_teams(red1: int, red2: int, red3: int, blue1: int, blue2: int, blue3: int):
    """
    Substitute teams in the current match.
    
    Args:
        red1, red2, red3: Red alliance team IDs
        blue1, blue2, blue3: Blue alliance team IDs
    """
    APIArena.send_command('substitute_teams', {
        'red1': red1,
        'red2': red2,
        'red3': red3,
        'blue1': blue1,
        'blue2': blue2,
        'blue3': blue3
    })
