# Pengiloo 快速優化實施指南

> 本指南提供可立即執行的改進方案，每個步驟都包含具體代碼和執行指令

## 📋 目錄
1. [錯誤處理系統](#1-錯誤處理系統)
2. [配置管理](#2-配置管理)
3. [代碼品質工具](#3-代碼品質工具)
4. [測試改進](#4-測試改進)
5. [性能監控](#5-性能監控)

---

## 1. 錯誤處理系統

### 1.1 建立異常體系

建立 `utils/exceptions.py`:
```python
"""自定義異常類別"""

class PengilooException(Exception):
    """所有 Pengiloo 異常的基類"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class IPCError(PengilooException):
    """IPC 通訊相關錯誤"""
    pass

class IPCTimeoutError(IPCError):
    """IPC 通訊超時"""
    pass

class IPCQueueFullError(IPCError):
    """IPC 隊列已滿"""
    pass

class ArenaError(PengilooException):
    """競技場相關錯誤"""
    pass

class InvalidMatchStateError(ArenaError):
    """無效的比賽狀態"""
    pass

class MatchAlreadyRunningError(ArenaError):
    """比賽已在進行中"""
    pass

class DatabaseError(PengilooException):
    """資料庫操作錯誤"""
    pass

class TeamNotFoundError(DatabaseError):
    """隊伍不存在"""
    pass

class MatchNotFoundError(DatabaseError):
    """比賽不存在"""
    pass

class WebSocketError(PengilooException):
    """WebSocket 相關錯誤"""
    pass

class NetworkError(PengilooException):
    """網路設備錯誤"""
    pass
```

### 1.2 統一日誌配置

建立 `utils/logging_config.py`:
```python
"""統一的日誌配置"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler

def setup_logging(
    level: str = "INFO",
    log_file: str = "logs/pengiloo.log",
    console: bool = True,
    file: bool = True
):
    """
    配置應用程式的日誌系統
    
    Args:
        level: 日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日誌檔案路徑
        console: 是否輸出到控制台
        file: 是否寫入檔案
    """
    # 建立日誌目錄
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 基礎配置
    handlers = []
    
    # 控制台處理器（使用 Rich 美化）
    if console:
        console_handler = RichHandler(
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            show_time=True,
            show_path=True
        )
        console_handler.setLevel(level)
        handlers.append(console_handler)
    
    # 檔案處理器（輪轉日誌）
    if file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # 配置根日誌記錄器
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True
    )
    
    # 設置第三方庫的日誌級別
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging system initialized (level={level})")
    
    return logger


class LoggerMixin:
    """為類別提供日誌功能的 Mixin"""
    
    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
```

### 1.3 在 main.py 中應用

修改 `main.py`:
```python
import asyncio
import multiprocessing
import sys
import uvicorn
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 新增：導入日誌和異常
from utils.logging_config import setup_logging
from utils.exceptions import IPCError, ArenaError

import web
from field.arena import Arena
from models.base import create_db_and_tables
from web.arena import APIArena
from web.websocket_manager import WebSocketManager
from ipc import IPCManager

# 設置日誌
logger = setup_logging(level="INFO")

def run_arena(command_queue, state_queue):
    """Arena process entry point"""
    # 在子進程中也設置日誌
    setup_logging(level="INFO", log_file="logs/arena.log")
    logger = logging.getLogger("Arena")
    
    async def _run():
        try:
            logger.info("Initializing Arena process...")
            create_db_and_tables()
            
            ipc = IPCManager()
            ipc.command_queue = command_queue
            ipc.state_queue = state_queue
            
            arena = await Arena.new_arena(ipc)
            logger.info("Arena initialized successfully")
            await arena.run()
        except Exception as e:
            logger.exception(f"Arena process fatal error: {e}")
            raise ArenaError(f"Arena initialization failed: {e}")
    
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.info("Arena process shutting down...")
    except Exception as e:
        logger.exception(f"Arena process crashed: {e}")
        sys.exit(1)

def run_web(command_queue, state_queue):
    """Web process entry point"""
    setup_logging(level="INFO", log_file="logs/web.log")
    logger = logging.getLogger("Web")
    
    try:
        logger.info("Initializing Web process...")
        
        ipc = IPCManager()
        ipc.command_queue = command_queue
        ipc.state_queue = state_queue
        
        app = fastapi.FastAPI(
            title="Pengiloo FMS",
            version="0.1.0",
            description="Field Management System for FRC"
        )
        
        APIArena.set_ipc(ipc)
        ws_manager = WebSocketManager(ipc)
        app.state.ipc = ipc
        app.state.ws_manager = ws_manager
        
        @app.on_event("startup")
        async def startup_event():
            logger.info("Starting WebSocket listener...")
            asyncio.create_task(ws_manager.listen_for_state_updates())
        
        @app.on_event("shutdown")
        async def shutdown_event():
            logger.info("Shutting down WebSocket manager...")
            ws_manager.stop()
        
        app.mount('/static', StaticFiles(directory='static'), name='static')
        app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
        app.include_router(web.router)
        
        logger.info("Web server starting on 0.0.0.0:8000")
        config = uvicorn.Config(app, '0.0.0.0', 8000, workers=1)
        server = uvicorn.Server(config)
        server.run()
        
    except Exception as e:
        logger.exception(f"Web process fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    logger.info("Starting Pengiloo FMS...")
    logger.info("=" * 60)
    
    try:
        command_queue = multiprocessing.Queue()
        state_queue = multiprocessing.Queue()
        
        arena_process = multiprocessing.Process(
            target=run_arena, 
            args=(command_queue, state_queue),
            name="ArenaProcess"
        )
        web_process = multiprocessing.Process(
            target=run_web, 
            args=(command_queue, state_queue),
            name="WebProcess"
        )
        
        arena_process.start()
        logger.info(f"Arena process started (PID: {arena_process.pid})")
        
        web_process.start()
        logger.info(f"Web process started (PID: {web_process.pid})")
        
        arena_process.join()
        web_process.join()
        
    except KeyboardInterrupt:
        logger.info("\nReceived shutdown signal...")
        arena_process.terminate()
        web_process.terminate()
        arena_process.join(timeout=5)
        web_process.join(timeout=5)
        logger.info("Pengiloo FMS stopped")
    except Exception as e:
        logger.exception(f"Main process error: {e}")
        sys.exit(1)
```

**執行測試**:
```bash
# 建立必要目錄
mkdir -p utils logs

# 測試日誌系統
python main.py
```

---

## 2. 配置管理

### 2.1 安裝依賴

更新 `pyproject.toml`:
```toml
dependencies = [
    # ... 現有依賴
    "pydantic-settings>=2.0.0",
]
```

執行:
```bash
pip install pydantic-settings
# 或使用 uv
uv pip install pydantic-settings
```

### 2.2 建立配置檔案

建立 `config/settings.py`:
```python
"""應用程式配置管理"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    """應用程式配置"""
    
    # 環境設定
    environment: str = "development"
    debug: bool = True
    
    # 應用程式
    app_name: str = "Pengiloo FMS"
    app_version: str = "0.1.0"
    
    # 資料庫
    database_url: str = "sqlite:///database.db"
    database_echo: bool = False
    
    # Web 伺服器
    web_host: str = "0.0.0.0"
    web_port: int = 8000
    web_workers: int = 1
    
    # Arena 設定
    arena_loop_period_ms: int = 10
    ds_packet_period_ms: int = 20
    ds_packet_warning_ms: int = 40
    match_end_score_dwell_sec: float = 3.0
    pre_load_next_match_delay_sec: float = 3.0
    
    # WebSocket 設定
    ws_heartbeat_interval: int = 30
    ws_message_queue_size: int = 100
    ws_max_connections: int = 100
    
    # IPC 設定
    ipc_timeout_sec: float = 5.0
    ipc_queue_maxsize: int = 0  # 0 = 無限制
    
    # 日誌設定
    log_level: str = "INFO"
    log_file: str = "logs/pengiloo.log"
    log_rotation_size: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5
    
    # 網路設定
    access_point_ip: str = "10.0.100.2"
    switch_ip: str = "10.0.100.3"
    
    # TBA 集成
    tba_api_key: str = ""
    tba_event_key: str = ""
    tba_base_url: str = "https://www.thebluealliance.com/api/v3"
    
    # 安全性
    cors_origins: list[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# 全域設定實例
settings = Settings()

def get_settings() -> Settings:
    """獲取設定實例（用於依賴注入）"""
    return settings
```

### 2.3 建立環境檔案範本

建立 `.env.example`:
```env
# 環境設定
ENVIRONMENT=development
DEBUG=true

# 資料庫
DATABASE_URL=sqlite:///database.db

# Web 伺服器
WEB_HOST=0.0.0.0
WEB_PORT=8000

# Arena 設定
ARENA_LOOP_PERIOD_MS=10
DS_PACKET_PERIOD_MS=20

# WebSocket 設定
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS=100

# 日誌
LOG_LEVEL=INFO
LOG_FILE=logs/pengiloo.log

# TBA 集成
TBA_API_KEY=your_api_key_here
TBA_EVENT_KEY=2024cmptx

# 網路設備
ACCESS_POINT_IP=10.0.100.2
SWITCH_IP=10.0.100.3
```

### 2.4 在代碼中使用配置

更新 `main.py`:
```python
from config.settings import settings

# 使用配置
config = uvicorn.Config(
    app, 
    settings.web_host, 
    settings.web_port, 
    workers=settings.web_workers
)
```

更新 `field/specs.py`（將硬編碼改為從配置讀取）:
```python
from config.settings import settings

# 原本的硬編碼
# ARENA_LOOP_PERIOD_MS = 10

# 改為從配置讀取
ARENA_LOOP_PERIOD_MS = settings.arena_loop_period_ms
DS_PACKET_PERIOD_MS = settings.ds_packet_period_ms
# ... 其他配置
```

**執行測試**:
```bash
# 複製環境範本
cp .env.example .env

# 編輯配置
# vim .env

# 測試配置載入
python -c "from config.settings import settings; print(settings.model_dump_json(indent=2))"
```

---

## 3. 代碼品質工具

### 3.1 更新 pyproject.toml

```toml
[tool.ruff]
line-length = 120
target-version = "py310"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "SIM",  # flake8-simplify
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.format]
quote-style = "single"
indent-style = "space"

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "uvicorn.*",
    "fpdf.*",
]
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
    "--strict-markers",
    "--tb=short",
    "--cov=.",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=json",
]
```

### 3.2 安裝工具

```bash
pip install mypy ruff
# 或
uv pip install mypy ruff
```

### 3.3 建立 pre-commit 配置

建立 `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### 3.4 執行檢查

```bash
# 安裝 pre-commit
pip install pre-commit
pre-commit install

# 手動執行所有檢查
pre-commit run --all-files

# 運行 ruff 格式化
ruff format .

# 運行 ruff lint
ruff check . --fix

# 運行 mypy 型別檢查
mypy .
```

---

## 4. 測試改進

### 4.1 建立測試輔助工具

建立 `tests/helpers.py`:
```python
"""測試輔助工具"""
import multiprocessing
from typing import Any
from unittest.mock import Mock
from ipc import IPCManager

class MockIPCManager(IPCManager):
    """模擬的 IPC Manager（用於測試）"""
    
    def __init__(self):
        self.commands_sent = []
        self.states_sent = []
        self.mock_state_responses = []
        
    def send_command(self, command: str, payload: Any = None):
        self.commands_sent.append({"command": command, "payload": payload})
        
    def get_command(self):
        if self.commands_sent:
            return self.commands_sent.pop(0)
        return None
        
    def broadcast_state(self, state_type: str, data: Any):
        self.states_sent.append({"type": state_type, "data": data})
        
    def get_state_update(self):
        if self.mock_state_responses:
            return self.mock_state_responses.pop(0)
        return None
        
    def add_mock_state(self, state_type: str, data: Any):
        """添加模擬狀態（測試用）"""
        self.mock_state_responses.append({"type": state_type, "data": data})

class DatabaseTestMixin:
    """資料庫測試 Mixin"""
    
    @staticmethod
    def create_test_team(team_id: int = 254):
        from models.team import Team
        return Team(
            id=team_id,
            nickname=f"Test Team {team_id}",
            name=f"Test Team {team_id}",
            city="Test City",
            state_prov="CA",
            country="USA"
        )
    
    @staticmethod
    def create_test_match(match_type: str = "test", match_number: int = 1):
        from models.match import Match, MatchType
        return Match(
            type=MatchType(match_type),
            type_order=match_number,
        )
```

### 4.2 建立 Arena 單元測試範本

建立 `tests/test_arena_core.py`:
```python
"""Arena 核心功能測試"""
import pytest
from unittest.mock import Mock, patch
from field.arena import Arena, AllianceStation
from tests.helpers import MockIPCManager

class TestArenaCore:
    """測試 Arena 核心功能"""
    
    @pytest.fixture
    async def mock_arena(self):
        """建立模擬 Arena"""
        ipc = MockIPCManager()
        arena = await Arena.new_arena(ipc)
        yield arena
    
    @pytest.mark.asyncio
    async def test_arena_initialization(self, mock_arena):
        """測試 Arena 初始化"""
        assert mock_arena is not None
        assert len(mock_arena.alliance_stations) == 6
        assert 'R1' in mock_arena.alliance_stations
        assert 'B3' in mock_arena.alliance_stations
    
    @pytest.mark.asyncio
    async def test_alliance_station_creation(self, mock_arena):
        """測試聯盟站位建立"""
        station = mock_arena.alliance_stations['R1']
        assert isinstance(station, AllianceStation)
        assert station.station_id == 0
        assert not station.a_stop
        assert not station.e_stop
    
    # 添加更多測試...
```

### 4.3 執行測試並生成報告

```bash
# 執行所有測試
pytest

# 執行特定測試並顯示詳細輸出
pytest tests/test_arena_core.py -v

# 執行測試並生成覆蓋率報告
pytest --cov=. --cov-report=html --cov-report=term-missing

# 只執行標記為 "unit" 的測試
pytest -m unit

# 並行執行測試（需要 pytest-xdist）
pytest -n auto
```

---

## 5. 性能監控

### 5.1 建立簡單的性能追蹤

建立 `utils/performance.py`:
```python
"""性能監控工具"""
import time
import logging
from functools import wraps
from typing import Callable
from contextlib import contextmanager

logger = logging.getLogger(__name__)

def measure_time(func: Callable) -> Callable:
    """裝飾器：測量函數執行時間"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        logger.debug(f"{func.__name__} took {elapsed:.2f}ms")
        return result
    return wrapper

def measure_time_async(func: Callable) -> Callable:
    """裝飾器：測量異步函數執行時間"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        logger.debug(f"{func.__name__} took {elapsed:.2f}ms")
        return result
    return wrapper

@contextmanager
def timer(name: str = "Operation"):
    """上下文管理器：測量代碼塊執行時間"""
    start = time.perf_counter()
    yield
    elapsed = (time.perf_counter() - start) * 1000
    logger.info(f"{name} took {elapsed:.2f}ms")

class PerformanceMonitor:
    """性能監控器"""
    
    def __init__(self):
        self.metrics = {}
        
    def record(self, name: str, value: float):
        """記錄指標"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)
        
    def get_stats(self, name: str) -> dict:
        """獲取指標統計"""
        if name not in self.metrics:
            return {}
        
        values = self.metrics[name]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "total": sum(values)
        }
        
    def reset(self, name: str = None):
        """重置指標"""
        if name:
            self.metrics[name] = []
        else:
            self.metrics = {}

# 全域監控器實例
monitor = PerformanceMonitor()
```

### 5.2 使用範例

在 `field/arena.py` 中:
```python
from utils.performance import measure_time_async, timer, monitor

@measure_time_async
async def load_match(self, match: models.Match):
    """載入比賽"""
    with timer("Load teams"):
        # 載入隊伍代碼...
        pass
    
    with timer("Configure network"):
        # 配置網路代碼...
        pass
    
    monitor.record("matches_loaded", 1)
```

### 5.3 建立健康檢查端點

在 `web/routes.py` 中添加:
```python
from fastapi import APIRouter
from utils.performance import monitor

router = APIRouter()

@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": time.time() - start_time,
    }

@router.get("/metrics")
async def metrics():
    """性能指標端點"""
    return {
        metric_name: monitor.get_stats(metric_name)
        for metric_name in monitor.metrics.keys()
    }
```

---

## 執行檢查清單

### ✅ 立即執行（今天）
- [ ] 建立 `utils/exceptions.py`
- [ ] 建立 `utils/logging_config.py`
- [ ] 更新 `main.py` 加入日誌
- [ ] 建立 `logs/` 目錄

### ✅ 本週內
- [ ] 安裝 `pydantic-settings`
- [ ] 建立 `config/settings.py`
- [ ] 建立 `.env.example`
- [ ] 複製 `.env.example` 為 `.env`
- [ ] 更新代碼使用新配置

### ✅ 下週內
- [ ] 安裝 `ruff` 和 `mypy`
- [ ] 建立 `.pre-commit-config.yaml`
- [ ] 運行 `ruff format .`
- [ ] 修復 `mypy` 錯誤
- [ ] 建立 `tests/helpers.py`

### ✅ 兩週內
- [ ] 建立 Arena 單元測試
- [ ] 提高測試覆蓋率至 50%
- [ ] 建立性能監控工具
- [ ] 添加健康檢查端點

---

## 驗證測試

所有改進完成後，運行以下命令驗證：

```bash
# 1. 代碼格式化
ruff format .

# 2. Lint 檢查
ruff check . --fix

# 3. 型別檢查
mypy .

# 4. 測試
pytest --cov=. --cov-report=html

# 5. 啟動應用
python main.py

# 6. 檢查健康
curl http://localhost:8000/health

# 7. 查看指標
curl http://localhost:8000/metrics
```

---

## 常見問題

### Q: 日誌檔案太大怎麼辦？
A: 已使用 `RotatingFileHandler`，會自動輪轉。可在 `config/settings.py` 調整 `log_rotation_size`。

### Q: 如何在生產環境中使用？
A: 
1. 複製 `.env.example` 為 `.env.production`
2. 設置 `ENVIRONMENT=production`
3. 設置 `DEBUG=false`
4. 設置 `LOG_LEVEL=WARNING`

### Q: 測試覆蓋率如何達到 80%？
A: 參考 `docs/architecture_optimization_plan.md` 的 Phase 2 測試策略。

---

**最後更新**: 2025年12月20日
