"""
Arena broadcast helper functions.
用於替代原本的 notifier 系統，通過 IPC 廣播不同類型的訊息給 Web 端。
"""
import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from field.arena import Arena

logger = logging.getLogger(__name__)


class ArenaBroadcaster:
    """Helper class to broadcast different types of messages from Arena to Web clients."""
    
    def __init__(self, arena: 'Arena'):
        self.arena = arena
    
    def broadcast(self, message_type: str, data: Any = None):
        """Broadcast a message with optional data.
        
        Args:
            message_type: Type of message (e.g., 'match_time', 'realtime_score')
            data: Data to broadcast. If None, will call the corresponding generator method.
        """
        if data is None:
            # 自動調用對應的生成器方法
            generator_method = f"generate_{message_type}_message"
            if hasattr(self.arena, generator_method):
                data = getattr(self.arena, generator_method)()
            else:
                logger.warning(f"No generator method found for {message_type}")
                data = {}
        
        self.arena.broadcast_state(message_type, data)
    
    # 便捷方法對應原本的 notifier
    def notify_match_time(self):
        """Broadcast match time update."""
        self.broadcast('match_time')
    
    def notify_match_load(self):
        """Broadcast match load information."""
        self.broadcast('match_load')
    
    def notify_realtime_score(self):
        """Broadcast real-time score update."""
        self.broadcast('realtime_score')
    
    def notify_arena_status(self):
        """Broadcast arena status."""
        self.broadcast('arena_status')
    
    def notify_match_timing(self):
        """Broadcast match timing configuration."""
        self.broadcast('match_timing')
    
    def notify_audience_display_mode(self):
        """Broadcast audience display mode change."""
        self.broadcast('audience_display_mode', self.arena.audience_display_mode)
    
    def notify_alliance_station_display_mode(self):
        """Broadcast alliance station display mode change."""
        self.broadcast('alliance_station_display_mode', self.arena.alliance_station_display_mode)
    
    def notify_scoring_status(self):
        """Broadcast scoring status."""
        self.broadcast('scoring_status')
    
    def notify_score_posted(self):
        """Broadcast score posted notification."""
        self.broadcast('score_posted')
    
    def notify_play_sound(self, sound_name: str):
        """Broadcast play sound command."""
        self.broadcast('play_sound', {'sound': sound_name})
    
    def notify_lower_third(self):
        """Broadcast lower third display update."""
        self.broadcast('lower_third')
    
    def notify_event_status(self):
        """Broadcast event status update."""
        self.broadcast('event_status')
    
    def notify_display_configuration(self):
        """Broadcast display configuration."""
        self.broadcast('display_configuration')
    
    def notify_alliance_selection(self):
        """Broadcast alliance selection update."""
        self.broadcast('alliance_selection')
    
    def notify_reload_displays(self):
        """Broadcast reload displays command."""
        self.broadcast('reload_displays', {})
