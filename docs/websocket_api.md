# Websocket API
## Format
```json
{
    "type": command,
    "data": {
        "p1": d1,
        "p2": d2,
    }
}
```

## API List
### /api/alliance_selection/websocket
#### command
> * `set_timer(time_limit_sec: float)`
> * `start_timer()`
> * `stop_timer()`
### /api/displays/alliance_station/websocket
### /api/displays/announcer/websocket
### /api/displays/audience/websocket
### /api/displays/bracket/websocket
### /api/displays/field_monitor/websocket
### /api/displays/logo/websocket
### /api/displays/placeholder/websocket
### /api/displays/queueing/websocket
### /api/displays/rankings/websocket
### /api/displays/twitch/websocket
### /api/displays/wall/websocket
### /api/displays/webpage/websocket
### /api/match_play/websocket
#### command
> * `load_match(match_id: int)`
> * `show_result(match_id: int)`
> * `substitude_teams(red1, red2, red3, blue1, blue2, blue3: int)`
> * `toggle_bypass(station: str)`
> * `start_match(mute_match_sound: bool)`
> * `abort_match()`
> * `signal_reset()`
> * `commit_results()`
> * `discard_results()`
> * `set_audience_display(mode: str)`
> * `start_timeout(duration_sec: int)`
> * `set_test_match_name(name: str)`
### /api/panels/referee/websocket
> * `add_foul(alliance: str, is_major: bool)`
> * `toggle_foul_type(alliance: str, index: int)`
> * `update_foul_team(alliance: str, index: int, team_id: int)`
> * `update_foul_rule(alliance: str, index: int, rule_id: int)`
> * `delete_foul(alliance: str, index: int)`
> * `card(alliance: str, team_id: int, card: str)`
> * `signal_reset()`
> * `commit_match()`
### /api/panels/scoring/&lt;alliance&gt;/websocket
> * `leave(position: int)`
> * `cage(position: int)`
> * `endgame(position: int)`
> * `trough_auto(action: str)`
> * `trough_teleop(action: str)`
> * `processor_auto(action: str)`
> * `processor_teleop(action: str)`
> * `net_auto(action: str)`
> * `net_teleop(action: str)`
> * `branches_auto(position: int, level: int)`
> * `branches(position: int, level: int)`
> * `branches_algaes(position: int, level: int)`
> * `commit_match()`
### /api/setup/displays/websocket
> * `configure_display(id: str, nickname: str, type: int, configuration: dict[str, str])`
> * `reload_display(display_id: int)`
> * `reload_all_displays()`
### /api/setup/lower_thirds/websocket
> * `update_lower_third(id: int, top_text: str, bottom_text: str, display_order: int, award_id: int)`
> * `delete_lower_third(id: int, top_text: str, bottom_text: str, display_order: int, award_id: int)`
> * `show_lower_third(id: int, top_text: str, bottom_text: str, display_order: int, award_id: int)`
> * `hide_lower_third(id: int, top_text: str, bottom_text: str, display_order: int, award_id: int)`
> * `reorder_lower_thirds(id: int, top_text: str, bottom_text: str, display_order: int, award_id: int)`
> * `set_audience_display()`