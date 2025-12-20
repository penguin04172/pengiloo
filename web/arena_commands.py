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


def update_alliance_selection(alliances: list, ranked_teams: list):
    """
    Update alliance selection data in Arena.
    
    Args:
        alliances: List of alliance dictionaries
        ranked_teams: List of ranked team dictionaries
    """
    APIArena.send_command('update_alliance_selection', {
        'alliances': alliances,
        'ranked_teams': ranked_teams
    })


def reset_alliance_selection():
    """Reset alliance selection to initial state."""
    APIArena.send_command('reset_alliance_selection', {})


def create_playoff_matches(start_time: str):
    """
    Create playoff matches.
    
    Args:
        start_time: ISO format datetime string
    """
    APIArena.send_command('create_playoff_matches', {'start_time': start_time})


def start_alliance_selection_timer(time_limit_sec: int):
    """
    Start alliance selection timer.
    
    Args:
        time_limit_sec: Timer duration in seconds
    """
    APIArena.send_command('start_alliance_selection_timer', {'time_limit_sec': time_limit_sec})


def stop_alliance_selection_timer():
    """Stop alliance selection timer."""
    APIArena.send_command('stop_alliance_selection_timer', {})


def register_scoring_panel(alliance: str, panel_id: str = None):
    """
    Register a scoring panel for an alliance.
    
    Args:
        alliance: 'red' or 'blue'
        panel_id: Unique panel identifier (optional)
    """
    if panel_id is None:
        panel_id = f"panel_{alliance}"
    APIArena.send_command('register_scoring_panel', {'alliance': alliance, 'panel_id': panel_id})


def unregister_scoring_panel(alliance: str, panel_id: str = None):
    """
    Unregister a scoring panel for an alliance.
    
    Args:
        alliance: 'red' or 'blue'
        panel_id: Unique panel identifier (optional)
    """
    if panel_id is None:
        panel_id = f"panel_{alliance}"
    APIArena.send_command('unregister_scoring_panel', {'alliance': alliance, 'panel_id': panel_id})


def commit_panel_score(alliance: str, panel_id: str = None):
    """
    Commit score from a scoring panel.
    
    Args:
        alliance: 'red' or 'blue'
        panel_id: Unique panel identifier (optional)
    """
    if panel_id is None:
        panel_id = f"panel_{alliance}"
    APIArena.send_command('commit_panel_score', {'alliance': alliance, 'panel_id': panel_id})


def update_scoring(alliance: str, command: str, position: int = None, level: int = None, 
                   action: str = None, state = None):
    """
    Update score for an alliance.
    
    Args:
        alliance: 'red' or 'blue'
        command: Scoring command type (leave, cage, endgame, etc.)
        position: Position index for multi-position elements
        level: Level index for multi-level elements
        action: Action type ('plus', 'minus', etc.)
        state: New state value
    """
    APIArena.send_command('update_scoring', {
        'alliance': alliance,
        'command': command,
        'position': position,
        'level': level,
        'action': action,
        'state': state
    })


def play_sound(sound_name: str):
    """
    Play a sound through the Arena.
    
    Args:
        sound_name: Name of the sound to play
    """
    APIArena.send_command('play_sound', {'sound_name': sound_name})


def update_display(display_config: dict):
    """
    Update display configuration.
    
    Args:
        display_config: Display configuration dictionary with id, type, nickname, configuration
    """
    APIArena.send_command('update_display', {'display_config': display_config})


def reload_displays(display_id: str = None):
    """
    Reload displays. If display_id is provided, only that display is reloaded.
    
    Args:
        display_id: Optional specific display ID to reload
    """
    APIArena.send_command('reload_displays', {'display_id': display_id})


def show_lower_third(lower_third: dict):
    """
    Show a lower third on audience displays.
    
    Args:
        lower_third: Lower third data dictionary
    """
    APIArena.send_command('show_lower_third', {'lower_third': lower_third})


def hide_lower_third():
    """Hide the currently displayed lower third."""
    APIArena.send_command('hide_lower_third', {})


def load_settings():
    """Reload Arena settings from database."""
    APIArena.send_command('load_settings', {})


def register_display(display_config: dict, ip_address: str):
    """
    Register a display with the Arena.
    
    Args:
        display_config: Display configuration dictionary
        ip_address: IP address of the display
    """
    APIArena.send_command('register_display', {
        'display_config': display_config,
        'ip_address': ip_address
    })


def add_foul(alliance: str, is_major: bool):
    """
    Add a foul to an alliance.
    
    Args:
        alliance: 'red' or 'blue'
        is_major: True for major foul, False for minor
    """
    APIArena.send_command('add_foul', {
        'alliance': alliance,
        'is_major': is_major
    })


def update_foul(alliance: str, command: str, index: int, team_id: int = 0, rule_id: int = 0):
    """
    Update a foul (toggle type, update team, update rule, or delete).
    
    Args:
        alliance: 'red' or 'blue'
        command: 'toggle_foul_type', 'update_foul_team', 'update_foul_rule', 'delete_foul'
        index: Index of the foul to modify
        team_id: Team ID for update_foul_team command
        rule_id: Rule ID for update_foul_rule command
    """
    APIArena.send_command('update_foul', {
        'alliance': alliance,
        'command': command,
        'index': index,
        'team_id': team_id,
        'rule_id': rule_id
    })


def assign_card(alliance: str, team_id: int, card: str):
    """
    Assign a card (yellow/red) to a team or alliance.
    
    Args:
        alliance: 'red' or 'blue'
        team_id: Team ID to assign card to
        card: Card type ('yellow', 'red', or empty string to clear)
    """
    APIArena.send_command('assign_card', {
        'alliance': alliance,
        'team_id': team_id,
        'card': card
    })


def commit_fouls():
    """Commit fouls for the current match (marks fouls as committed)."""
    APIArena.send_command('commit_fouls', {})

