# DEPRECATED: The Notifier system has been replaced by ArenaBroadcaster and WebSocketManager.
# This module is kept for backward compatibility only.
# New code should use web.websocket_manager.WebSocketManager and field.arena_broadcast.ArenaBroadcaster
# TODO: Remove in next major version

from .notifier import Notifier, handle_notifiers, write_notifier

# Do not export by default - mark as deprecated
__all__ = []
