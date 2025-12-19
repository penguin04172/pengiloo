# IPC Integration Guide

## Overview
This document tracks the integration of IPC (Inter-Process Communication) between the Arena process and Web process.

## Architecture

### Arena Process (Game Engine)
- Runs the main game loop
- Handles hardware I/O
- Publishes state updates to the Web process via `state_queue`
- Consumes commands from `command_queue`

### Web Process (API Server)
- Runs FastAPI with Uvicorn
- Sends commands to Arena via `command_queue`
- Receives state updates from `state_queue`
- Broadcasts updates to WebSocket clients

## Implementation Status

### ✅ Completed
1. IPC Manager created (`ipc.py`)
2. Main.py refactored for multiprocessing
3. All models migrated to SQLModel
4. Arena modified to accept IPC and process commands
5. Arena broadcasts state at key transition points
6. WebSocketManager created for state distribution
7. WebSocket route created (`/ws/arena`)
8. Helper functions created (`web/arena_commands.py`)

### 🔄 In Progress
1. Update web routes to use IPC commands instead of direct Arena access
2. Testing and debugging

### ⏳ Pending
1. Full integration testing
2. Performance tuning
3. Error handling improvements

## Key Changes Needed

### Arena (`field/arena.py`)
- Add `ipc: IPCManager` parameter to `__init__` and `new_arena()`
- Check `command_queue` in the main loop
- Broadcast state changes via `state_queue`

### Web (`web/arena.py`)
- Replace singleton pattern with IPC-based communication
- Create command sending functions
- Setup state listener for WebSocket updates

## Command Protocol

Commands sent from Web to Arena:
```python
{
    "command": "load_match",
    "payload": {"match_id": 123}
}
```

State updates from Arena to Web:
```python
{
    "type": "match_state",
    "data": {"state": "MATCH_STARTED", ...}
}
```
