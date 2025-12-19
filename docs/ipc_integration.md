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
8. Helper functions created (`web/arena_commands.py` - 17 commands)
9. StateManager created (`web/state_manager.py`) for caching Arena state
10. API refactored: `web/api/match_control.py` (WebSocket → REST)
11. Reports updated: `web/reports.py` (removed get_arena calls)

### 🔄 In Progress
1. Expand Arena.broadcast_state() to include all needed state
2. Create arena_state.py helper functions for state access
3. Update remaining 23+ API files to use IPC pattern

### ⏳ Pending
1. alliance_selection.py refactoring
2. panels_scoring.py refactoring (WebSocket endpoint)
3. Batch refactor setup_*.py and displays_*.py files
4. Full integration testing
5. Performance tuning and error handling

## Next Steps Plan

### Phase 1: State Broadcasting (Priority P0)
**Goal**: Make all Arena state accessible to Web process

1. **Expand broadcast_state()** in `field/arena.py`
   - Include: match_state, current_match, alliance_stations
   - Include: realtime_scores (red/blue)
   - Include: alliance_selection data
   - Include: display modes and event info

2. **Create arena_state.py** helper module
   - Functions: get_match_state(), get_realtime_score(), etc.
   - Type-safe access to StateManager
   - Fallback values for missing state

### Phase 2: API Refactoring (Priority P1)
**Pattern**: Remove get_arena() → Use StateManager + arena_commands

**Categories**:
- **A-Class** (Simple reads): setup_*.py files → Use database or arena_state
- **B-Class** (Commands): alliance_selection.py → StateManager + arena_commands  
- **C-Class** (WebSocket): panels_scoring.py → Split into REST + unified WebSocket

**Refactoring Checklist** per file:
- [ ] Remove `from web.arena import get_arena`
- [ ] Replace get_arena() calls with arena_state/database
- [ ] Use arena_commands for Arena operations
- [ ] Add proper error handling for IPC failures

### Phase 3: Testing & Optimization (Priority P2)
- Test full match workflow
- Test alliance selection
- Verify WebSocket state broadcasting
- Performance profiling
- Error handling improvements

## Files Requiring Updates

### High Priority (Direct Arena Access)
- `web/api/alliance_selection.py` - 20+ get_arena() calls
- `web/api/panels_scoring.py` - WebSocket with Arena access
- Other web/api/*.py files (23+ files total)

### Current Refactoring Progress
- ✅ match_control.py (407 lines → ~100 lines, REST API)
- ✅ reports.py (10 get_arena() calls replaced)
- 🔄 Remaining: 23 files in web/api/

## Risk Mitigation

1. **State sync delays**: Return confirmations, optimistic UI updates
2. **State consistency**: Atomic snapshots in broadcast_state()
3. **Process crashes**: Persist critical state to database
4. **WebSocket scale**: Connection limits, heartbeat cleanup

## Estimated Effort

| Task | Time | Priority |
|------|------|----------|
| Expand state broadcasting | 2-3h | P0 |
| Create helper functions | 1h | P0 |
| Refactor A-class files (10) | 3-4h | P1 |
| Refactor B-class files (5) | 3-4h | P1 |
| Refactor C-class files (3) | 4-5h | P2 |
| Other files (5) | 2h | P2 |
| Integration testing | 3-4h | P1 |
| Debug & optimize | 2-3h | P2 |
| **Total** | **20-28h** | |

---

**Last Updated**: 2025-12-20  
**Current Phase**: Preparing Phase 1 (State Broadcasting)
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
