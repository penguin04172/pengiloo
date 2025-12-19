"""
Helper functions for accessing Arena state from Web process.
Provides type-safe access to cached Arena state via StateManager.
"""
from typing import Optional, Any
from web.state_manager import get_state_manager


def get_match_state() -> str:
    """Get current match state (PRE_MATCH, AUTO_PERIOD, etc.)."""
    return get_state_manager().get_state('match_state', 'PRE_MATCH')


def get_match_id() -> Optional[int]:
    """Get current match ID, or None if no match is loaded."""
    return get_state_manager().get_state('match_id')


def get_match_type() -> Optional[str]:
    """Get current match type (QUALIFICATION, PLAYOFF, TEST)."""
    return get_state_manager().get_state('match_type')


def get_match_name() -> Optional[str]:
    """Get current match name."""
    return get_state_manager().get_state('match_name')


def get_match_time_sec() -> float:
    """Get current match time in seconds."""
    return get_state_manager().get_state('match_time_sec', 0.0)


def get_field_reset() -> bool:
    """Get field reset status."""
    return get_state_manager().get_state('field_reset', False)


def get_audience_display_mode() -> str:
    """Get audience display mode."""
    return get_state_manager().get_state('audience_display_mode', 'blank')


def get_alliance_station_display_mode() -> str:
    """Get alliance station display mode."""
    return get_state_manager().get_state('alliance_station_display_mode', 'logo')


def get_event_name() -> str:
    """Get event name."""
    return get_state_manager().get_state('event_name', 'Unknown Event')


def get_event_code() -> str:
    """Get event code."""
    return get_state_manager().get_state('event_code', '')


def get_alliance_stations() -> dict[str, dict[str, Any]]:
    """
    Get all alliance stations status.
    Returns dict with keys like 'R1', 'R2', 'R3', 'B1', 'B2', 'B3'.
    Each value is a dict with: team_id, bypass, ethernet, ds_linked, wifi_status.
    """
    return get_state_manager().get_state('alliance_stations', {})


def get_alliance_station(station: str) -> Optional[dict[str, Any]]:
    """Get specific alliance station status."""
    stations = get_alliance_stations()
    return stations.get(station)


def get_realtime_score(alliance: str) -> dict[str, Any]:
    """
    Get realtime score for an alliance ('red' or 'blue').
    Returns dict with score data.
    """
    key = f'{alliance}_score'
    return get_state_manager().get_state(key, {})


def get_red_score() -> dict[str, Any]:
    """Get red alliance realtime score."""
    return get_realtime_score('red')


def get_blue_score() -> dict[str, Any]:
    """Get blue alliance realtime score."""
    return get_realtime_score('blue')


def get_alliance_selection_alliances() -> list[dict[str, Any]]:
    """Get alliance selection alliances data."""
    return get_state_manager().get_state('alliance_selection_alliances', [])


def get_alliance_selection_ranked_teams() -> list[dict[str, Any]]:
    """Get alliance selection ranked teams data."""
    return get_state_manager().get_state('alliance_selection_ranked_teams', [])


def get_alliance_selection_show_timer() -> bool:
    """Get alliance selection timer visibility."""
    return get_state_manager().get_state('alliance_selection_show_timer', False)


def get_alliance_selection_time_remaining_sec() -> int:
    """Get alliance selection time remaining in seconds."""
    return get_state_manager().get_state('alliance_selection_time_remaining_sec', 0)


def get_lower_third() -> Optional[dict[str, Any]]:
    """Get lower third data."""
    return get_state_manager().get_state('lower_third')


def get_show_lower_third() -> bool:
    """Get lower third visibility."""
    return get_state_manager().get_state('show_lower_third', False)


def get_full_state() -> dict[str, Any]:
    """Get all cached Arena state."""
    return get_state_manager().get_all_state()
