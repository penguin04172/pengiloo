# Pengiloo 專案架構優化方案

## 執行日期
2025年12月20日

## 專案概述

**Pengiloo** 是一個 FRC（FIRST Robotics Competition）競技場管理系統，靈感來自 Cheesy-Arena 和 JMS。

### 當前技術棧
- **語言**: Python 3.10+
- **Web框架**: FastAPI + Uvicorn
- **資料庫**: SQLite + SQLModel
- **架構**: 多進程（Arena + Web）
- **通訊**: multiprocessing.Queue (IPC)
- **前端**: Jinja2 模板 + WebSocket
- **測試**: pytest + pytest-asyncio

---

## 架構現狀分析

### ✅ 已完成的改進
1. **多進程架構** - Arena 與 Web 進程分離
2. **IPC 通訊機制** - 使用 multiprocessing.Queue
3. **WebSocket 廣播系統** - 從舊 notifier 遷移到新 broadcaster
4. **資料庫遷移** - 從 PonyORM 遷移到 SQLModel
5. **測試覆蓋** - 54 個單元測試通過（覆蓋率 23%）

### 📊 模組結構
```
pengiloo/
├── field/              # 競技場核心邏輯 (Arena)
├── game/               # 比賽規則與計分
├── models/             # 資料模型 (SQLModel)
├── web/                # Web API 與路由
│   ├── api/            # REST API 端點
│   ├── pages/          # 頁面路由
│   └── websocket_*.py  # WebSocket 管理
├── ws/                 # WebSocket 基礎設施
├── network/            # 網路管理 (AP, Switch)
├── playoff/            # 季後賽邏輯
├── tournament/         # 賽事管理
├── third_party/        # 第三方集成 (TBA)
└── tests/              # 測試套件
```

---

## 🎯 優化目標

### 1. 代碼品質提升
- 提高測試覆蓋率至 80%+
- 減少代碼重複
- 改善錯誤處理機制

### 2. 性能優化
- WebSocket 訊息傳輸效率
- 資料庫查詢優化
- IPC 通訊延遲降低

### 3. 可維護性
- 模組邊界清晰化
- 文檔完整性
- 配置管理標準化

### 4. 可擴展性
- 插件式比賽規則
- 多語言支援
- 雲端部署準備

---

## 📋 優化方案

## Phase 1: 架構穩定性強化 (高優先級)

### 1.1 錯誤處理與日誌系統 ⭐⭐⭐
**問題**: 缺乏統一的錯誤處理和日誌框架

**方案**:
```python
# utils/exceptions.py - 自定義異常體系
class PengilooException(Exception):
    """基礎異常"""
    pass

class IPCCommunicationError(PengilooException):
    """IPC 通訊錯誤"""
    pass

class ArenaStateError(PengilooException):
    """競技場狀態錯誤"""
    pass

class MatchControlError(PengilooException):
    """比賽控制錯誤"""
    pass

# utils/logging_config.py - 統一日誌配置
import logging
from rich.logging import RichHandler

def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
```

**行動項目**:
- [ ] 建立異常類別體系
- [ ] 在 IPC 層加入錯誤重試機制
- [ ] WebSocket 斷線自動重連
- [ ] Arena 狀態不一致檢測

**預期效益**: 降低 80% 的無聲失敗（silent failure）

---

### 1.2 配置管理系統 ⭐⭐⭐
**問題**: 硬編碼配置散落各處，缺乏環境管理

**方案**:
```python
# config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 環境配置
    environment: str = "development"
    debug: bool = True
    
    # 資料庫
    database_url: str = "sqlite:///database.db"
    
    # 網路
    web_host: str = "0.0.0.0"
    web_port: int = 8000
    
    # Arena
    arena_loop_period_ms: int = 10
    ds_packet_period_ms: int = 20
    
    # WebSocket
    ws_heartbeat_interval: int = 30
    ws_message_queue_size: int = 100
    
    # TBA 集成
    tba_api_key: str = ""
    tba_event_key: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

**行動項目**:
- [ ] 建立 `config/` 目錄
- [ ] 使用 pydantic-settings
- [ ] 移除 `field/specs.py` 的硬編碼
- [ ] 支援 .env.development, .env.production

**預期效益**: 簡化部署，提高可配置性

---

### 1.3 IPC 通訊增強 ⭐⭐⭐
**問題**: 
- 無超時機制
- 無訊息確認（ACK）
- 無錯誤恢復

**方案**:
```python
# ipc/enhanced_ipc.py
import multiprocessing
from typing import Any, Optional
from dataclasses import dataclass
import uuid
import time

@dataclass
class IPCMessage:
    id: str
    command: str
    payload: Any
    timestamp: float
    requires_ack: bool = False

class EnhancedIPCManager:
    def __init__(self, timeout: float = 5.0):
        self.command_queue = multiprocessing.Queue()
        self.state_queue = multiprocessing.Queue()
        self.ack_queue = multiprocessing.Queue()
        self.timeout = timeout
        
    def send_command_with_ack(self, command: str, payload: Any) -> bool:
        """發送命令並等待確認"""
        msg = IPCMessage(
            id=str(uuid.uuid4()),
            command=command,
            payload=payload,
            timestamp=time.time(),
            requires_ack=True
        )
        self.command_queue.put(msg)
        
        # 等待 ACK
        try:
            ack = self.ack_queue.get(timeout=self.timeout)
            return ack.get('id') == msg.id
        except multiprocessing.queues.Empty:
            return False
```

**行動項目**:
- [ ] 實現訊息 ID 追蹤
- [ ] 加入超時處理
- [ ] 實現命令優先級
- [ ] 加入訊息統計監控

**預期效益**: IPC 可靠性提升至 99.9%

---

## Phase 2: 代碼品質與測試 (高優先級)

### 2.1 測試覆蓋率提升 ⭐⭐⭐
**現狀**: 23% 覆蓋率，主要測試 IPC 和 Models

**目標**: 80% 覆蓋率

**待補充測試**:
```
未覆蓋模組                    優先級
────────────────────────────────────
field/arena.py               ⭐⭐⭐ (核心邏輯)
game/score.py                ⭐⭐⭐
game/ranking.py              ⭐⭐⭐
web/websocket_manager.py     ⭐⭐
playoff/playoff_tournament.py ⭐⭐
network/access_point.py      ⭐
tournament/schedule.py       ⭐
```

**測試策略**:
1. **單元測試**: 每個模組的獨立功能
2. **集成測試**: Arena ↔ Web ↔ WebSocket
3. **端到端測試**: 完整比賽流程模擬

**行動項目**:
- [ ] 建立 Arena 單元測試（mock IPC）
- [ ] WebSocket 集成測試
- [ ] 比賽流程端到端測試
- [ ] 建立測試數據 fixtures

**預期效益**: 減少 70% 的回歸錯誤

---

### 2.2 代碼規範化 ⭐⭐
**問題**: 
- 缺乏型別註解
- 代碼風格不一致
- 缺乏 docstrings

**方案**:
```python
# 使用 mypy 進行型別檢查
# pyproject.toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

# 使用 ruff 統一格式化
[tool.ruff]
line-length = 120
target-version = "py310"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
]
```

**行動項目**:
- [ ] 啟用 mypy strict mode
- [ ] 為所有公開 API 添加型別註解
- [ ] 使用 ruff format 統一格式
- [ ] 建立 pre-commit hooks

**預期效益**: 在編譯期捕獲 50% 的型別錯誤

---

## Phase 3: 性能優化 (中優先級)

### 3.1 WebSocket 性能優化 ⭐⭐
**問題**: 
- 每條訊息都經過 JSON 序列化
- 無訊息批次處理
- 無壓縮

**方案**:
```python
# web/websocket_optimized.py
import orjson  # 更快的 JSON
import asyncio
from collections import defaultdict

class OptimizedWebSocketManager:
    def __init__(self):
        self.message_buffer = defaultdict(list)
        self.flush_interval = 0.05  # 50ms
        
    async def buffered_broadcast(self):
        """批次發送訊息"""
        while True:
            await asyncio.sleep(self.flush_interval)
            for ws, messages in self.message_buffer.items():
                if messages:
                    # 批次發送
                    batch = orjson.dumps({"batch": messages})
                    await ws.send_bytes(batch)
                    messages.clear()
```

**行動項目**:
- [ ] 實現訊息批次處理
- [ ] 使用 orjson 替代標準 json
- [ ] 大訊息使用 gzip 壓縮
- [ ] 實現訊息優先級隊列

**預期效益**: WebSocket 吞吐量提升 3-5x

---

### 3.2 資料庫查詢優化 ⭐⭐
**問題**: N+1 查詢問題

**方案**:
```python
# models/optimized_queries.py
from sqlmodel import select, Session
from sqlalchemy.orm import selectinload

def get_matches_with_teams(session: Session, match_type: str):
    """使用 eager loading 避免 N+1"""
    stmt = (
        select(Match)
        .options(
            selectinload(Match.red_alliance_teams),
            selectinload(Match.blue_alliance_teams),
        )
        .where(Match.type == match_type)
    )
    return session.exec(stmt).all()
```

**行動項目**:
- [ ] 識別並修復所有 N+1 查詢
- [ ] 為常用查詢添加索引
- [ ] 實現查詢結果快取
- [ ] 使用 SQLAlchemy 的 relationship lazy loading

**預期效益**: 資料庫查詢時間減少 60%

---

## Phase 4: 功能擴展 (中低優先級)

### 4.1 插件系統 ⭐⭐
**目標**: 支援不同比賽規則（如 FRC 不同年度遊戲）

**方案**:
```python
# game/plugin_system.py
from abc import ABC, abstractmethod

class GamePlugin(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def get_score_elements(self) -> list:
        pass
    
    @abstractmethod
    def calculate_score(self, match_data: dict) -> int:
        pass

# game/plugins/crescendo_2024.py
class Crescendo2024Plugin(GamePlugin):
    def get_name(self) -> str:
        return "CRESCENDO 2024"
    
    # 實現具體規則...
```

**行動項目**:
- [ ] 設計插件接口
- [ ] 將當前規則重構為插件
- [ ] 實現插件加載機制
- [ ] 支援動態切換規則

---

### 4.2 API 文檔與版本化 ⭐⭐
**問題**: 缺乏 API 文檔，無版本控制

**方案**:
```python
# main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Pengiloo FMS API",
    version="1.0.0",
    description="Field Management System for FRC",
)

# 自動生成 OpenAPI 文檔
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# API 版本化
app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(api_v2_router, prefix="/api/v2")
```

**行動項目**:
- [ ] 啟用 FastAPI 自動文檔 (/docs)
- [ ] 為所有端點添加描述和範例
- [ ] 實現 API 版本控制
- [ ] 建立 API 變更日誌

---

### 4.3 監控與可觀察性 ⭐
**目標**: 了解系統運行狀況

**方案**:
```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# 定義指標
ipc_messages_sent = Counter('ipc_messages_sent_total', 'IPC messages sent')
websocket_connections = Gauge('websocket_active_connections', 'Active WebSocket')
match_duration = Histogram('match_duration_seconds', 'Match duration')

# monitoring/healthcheck.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "arena_process": arena_process.is_alive(),
        "web_process": True,
        "database": await check_db_connection(),
    }
```

**行動項目**:
- [ ] 整合 Prometheus 指標
- [ ] 實現健康檢查端點
- [ ] 加入 structured logging
- [ ] 建立性能儀表板

---

## Phase 5: 部署與運維 (低優先級)

### 5.1 容器化 ⭐
**方案**:
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]

# docker-compose.yml
version: '3.8'
services:
  pengiloo:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./database.db:/app/database.db
    environment:
      - ENVIRONMENT=production
```

**行動項目**:
- [ ] 建立 Dockerfile
- [ ] 建立 docker-compose.yml
- [ ] 支援環境變數配置
- [ ] 建立 CI/CD pipeline

---

### 5.2 文檔完善 ⭐
**待補充文檔**:
- [ ] 架構設計文檔（Architecture.md）
- [ ] API 使用指南（API_GUIDE.md）
- [ ] 部署指南（DEPLOYMENT.md）
- [ ] 故障排除手冊（TROUBLESHOOTING.md）
- [ ] 貢獻指南（CONTRIBUTING.md）

---

## 📊 優化優先級矩陣

| 項目 | 影響 | 複雜度 | 優先級 | 預估時間 |
|------|------|--------|--------|----------|
| 錯誤處理與日誌 | 高 | 低 | ⭐⭐⭐ | 2天 |
| 配置管理 | 高 | 低 | ⭐⭐⭐ | 1天 |
| IPC 增強 | 高 | 中 | ⭐⭐⭐ | 3天 |
| 測試覆蓋率 | 高 | 高 | ⭐⭐⭐ | 5天 |
| 代碼規範化 | 中 | 低 | ⭐⭐ | 2天 |
| WebSocket 優化 | 中 | 中 | ⭐⭐ | 3天 |
| 資料庫優化 | 中 | 中 | ⭐⭐ | 2天 |
| 插件系統 | 中 | 高 | ⭐⭐ | 5天 |
| API 文檔 | 中 | 低 | ⭐⭐ | 2天 |
| 監控系統 | 低 | 中 | ⭐ | 3天 |
| 容器化 | 低 | 低 | ⭐ | 1天 |
| 文檔完善 | 低 | 低 | ⭐ | 3天 |

**總預估時間**: 32 天（~6-7 週）

---

## 🚀 立即行動建議

### 快速修復（本週可完成）
1. ✅ 建立統一的異常處理體系
2. ✅ 實現配置管理系統
3. ✅ 為關鍵路徑添加日誌
4. ✅ 啟用 mypy 型別檢查

### 短期目標（1個月內）
1. ✅ IPC 通訊增強（超時、重試）
2. ✅ 測試覆蓋率提升至 50%+
3. ✅ WebSocket 訊息批次處理
4. ✅ 資料庫查詢優化

### 中期目標（2-3個月）
1. ✅ 測試覆蓋率達到 80%
2. ✅ 實現插件系統
3. ✅ API 完整文檔
4. ✅ 監控系統上線

---

## 📝 技術債務清單

### 高優先級
- [ ] TODO in [web/reports.py:624] - Playoff tournament state via IPC
- [ ] TODO in [web/reports.py:644] - Playoff tournament via IPC
- [ ] TODO in [web/api/bracket_svg.py:47] - Serialize playoff_tournament
- [ ] TODO in [ws/__init__.py:4] - Remove deprecated notifier in next version

### 中優先級
- [ ] field/arena.py 過大（1246行）- 需拆分
- [ ] 缺乏前端代碼組織（static/js 混亂）
- [ ] 硬編碼的時間常數（field/specs.py）

### 低優先級
- [ ] README.md 內容過少
- [ ] requirements.txt 與 pyproject.toml 重複
- [ ] 缺乏 CHANGELOG.md

---

## 🎯 成功指標

### 代碼品質
- ✅ 測試覆蓋率 ≥ 80%
- ✅ mypy 嚴格模式通過
- ✅ ruff 零警告
- ✅ 所有 TODO 清除

### 性能指標
- ✅ WebSocket 延遲 < 50ms (p99)
- ✅ API 響應時間 < 100ms (p95)
- ✅ IPC 訊息丟失率 < 0.1%
- ✅ 資料庫查詢時間 < 50ms (平均)

### 可靠性
- ✅ 系統正常運行時間 > 99.9%
- ✅ 無關鍵錯誤運行 > 24小時
- ✅ 自動恢復錯誤率 > 95%

---

## 📚 參考資源

### 類似專案
- [Cheesy Arena](https://github.com/Team254/cheesy-arena) - FRC 競技場管理
- [FMS-Clone](https://github.com/MechMania/FMS-Clone) - 比賽管理系統

### 技術文檔
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Multiprocessing Guide](https://docs.python.org/3/library/multiprocessing.html)

---

## 結論

Pengiloo 已完成核心架構重構（多進程、IPC、WebSocket），為進一步優化打下良好基礎。

**建議執行順序**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5

透過系統性的優化，可在 2-3 個月內將 Pengiloo 提升至生產級穩定性和可維護性。

---

**文件版本**: 1.0  
**最後更新**: 2025年12月20日  
**負責人**: GitHub Copilot  
**審核者**: [待填寫]
