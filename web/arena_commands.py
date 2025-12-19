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


def set_alliance_station_display(mode: str):
    """
    Set the alliance station display mode.
    
    Args:
        mode: Display mode (e.g., 'match', 'logo', 'fieldReset', etc.)
    """
    APIArena.send_command('set_alliance_station_display', {'mode': mode})


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


def toggle_bypass(station: str):
    """
    Toggle bypass for an alliance station.
    
    Args:
        station: Station ID (e.g., 'R1', 'B2')
    """
    APIArena.send_command('toggle_bypass', {'station': station})


def signal_reset():
    """Signal field reset to alliance stations."""
    APIArena.send_command('signal_reset')


def start_timeout(duration_sec: int):
    """
    Start a timeout.
    
    Args:
        duration_sec: Timeout duration in seconds
    """
    APIArena.send_command('start_timeout', {'duration_sec': duration_sec})


def set_test_match_name(name: str):
    """
    Set the name of a test match.
    
    Args:
        name: Match name
    """
    APIArena.send_command('set_test_match_name', {'name': name})


def load_next_match(start_break: bool = True):
    """
    Load the next match.
    
    Args:
        start_break: Whether to start scheduled break if applicable
    """
    APIArena.send_command('load_next_match', {'start_break': start_break})


def reset_match():
    """Reset the current match state."""
    APIArena.send_command('reset_match')
