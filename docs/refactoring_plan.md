# Refactoring Plan: Decoupling and Multiprocessing for Pengiloo

## 1. Architecture Overview

### Current State
- **Monolithic:** `Arena` class acts as a "God Object" managing game state, hardware, and logic.
- **Coupled:** Web layer directly accesses the `Arena` singleton instance.
- **Concurrency Issues:** `Uvicorn` with multiple workers fails because `Arena` state is not shared across processes.

### Target Architecture
- **Multi-Process:**
    1.  **Game Engine Process:** Runs the `Arena` loop, handles hardware I/O, and manages game rules.
    2.  **Web Server Process:** Runs FastAPI/Uvicorn, handles HTTP requests and WebSocket connections.
- **Communication (IPC):**
    -   **`multiprocessing.Queue`:** For sending commands (Web -> Arena).
    -   **`multiprocessing.Queue` / `Pipe`:** For broadcasting state updates (Arena -> Web).
    -   **`multiprocessing.Manager`:** For sharing simple state flags or dictionaries if needed without external dependencies.
- **Data Layer:**
    -   **SQLModel:** Replaces PonyORM for database interaction and Pydantic integration.
- **Project Management:**
    -   **uv:** Used for dependency management and script execution.

## 2. Implementation Steps

### Phase 1: Database Migration (SQLModel)
1.  **Replace PonyORM:** Rewrite `models/` using `SQLModel`.
2.  **Pydantic Integration:** Leverage SQLModel's dual nature (ORM + Pydantic) to define schemas for API responses directly.
3.  **Migration Script:** Create a script to initialize the SQLite DB using SQLModel.

### Phase 2: Interface & IPC Design
1.  **Command Queue:** Create a `multiprocessing.Queue` for the Web layer to send actions (`start_match`, `abort`) to the Arena.
2.  **State Broadcast:** Create a mechanism (e.g., a separate Queue or Pipe) where `Arena` pushes state updates. The Web process consumes this and pushes to WebSockets.
3.  **Dependency Injection:** Inject these queues into the FastAPI app state (`app.state`) so endpoints can use them.

### Phase 3: Process Separation & Execution
1.  **Refactor `main.py`:**
    -   Initialize `multiprocessing` resources (Queues, Managers).
    -   Spawn the `Arena` process, passing the queues.
    -   Spawn the `Uvicorn` process (programmatically via `uvicorn.Config` and `Server`), passing the queues to the FastAPI app factory or context.
2.  **`uv` Integration:** Update `pyproject.toml` to use `uv` standards and ensure `uv run main.py` works correctly.

### Phase 4: Testing & Optimization
1.  **Integration Tests:** Verify that web buttons correctly trigger hardware events via the Queue.
2.  **Latency Check:** Measure the delay between a hardware event and the WebSocket update on the client.

## 3. Technology Stack Changes
-   **Remove:** `pony`.
-   **Add:** `sqlmodel`.
-   **Tooling:** `uv` for package management.
-   **IPC:** Native `multiprocessing` (No Redis).
