# WebSocket 重構後續修正檢查清單

## 執行日期
2025年12月20日

## 需要修正的部分

### ✅ 已完成
1. Arena 中所有 notifier 調用（45 處）已替換為 broadcaster
2. 測試套件全部通過（54/54）
3. 核心 WebSocket 系統已重構

---

### ⚠️ 需要修正

## 1. **field/display.py** - Display Notifier 相關

**問題**：Display 類還在使用舊的 `Notifier` 實例

**位置**：
- Line 4: `from ws.notifier import Notifier`
- Line 146: `display.notifier = Notifier(...)`
- Line 155, 167: `await display.notifier.notify()`
- Line 157, 168, 184, 199: `await self.display_configuration_notifier.notify()`

**影響**：
- Display 配置更新無法廣播到前端
- 顯示器註冊/更新功能受影響

**修正方案**：
```python
# 方案 1: 使用 broadcaster
def update_display(self, display_id: str, config: dict):
    # 更新 display 配置
    self.displays[display_id] = config
    # 廣播更新
    self.broadcaster.notify_display_configuration()

# 方案 2: 通過 IPC 直接廣播
def update_display(self, display_id: str, config: dict):
    self.displays[display_id] = config
    self.broadcast_state('display_configuration', {
        'display_id': display_id,
        'config': config
    })
```

---

## 2. **field/event_status.py** - Event Status Notifier

**問題**：EventStatusMixin 使用舊的 notifier

**位置**：
- Line 71: `await self.event_status_notifier.notify()`
- Line 77: `await self.event_status_notifier.notify()`

**影響**：
- 賽事狀態更新（提前/延遲訊息）無法廣播

**修正方案**：
```python
# 替換為 broadcaster
async def update_cycle_time(self, match_start_time: datetime):
    # ... 現有邏輯 ...
    self.broadcaster.notify_event_status()  # 替換 notifier

async def update_early_late_message(self):
    new_early_late_message = self.get_early_late_message()
    if new_early_late_message != self.event_status.early_late_message:
        self.event_status.early_late_message = new_early_late_message
        self.broadcaster.notify_event_status()  # 替換 notifier
```

---

## 3. **field/arena_notifiers.py** - Notifier 初始化

**問題**：ArenaNotifiersMixin.__init__ 還在創建 Notifier 實例

**位置**：
- Lines 61-87: 創建所有 notifier 實例

**影響**：
- 記憶體浪費（創建但不使用的物件）
- 程式碼混亂

**修正方案**：
```python
# 選項 1: 完全移除 __init__ 中的 notifier 創建
# 只保留訊息生成器方法，broadcaster 會調用它們

# 選項 2: 標記為 deprecated 並註釋
def __init__(self, *args, **kwargs):
    # DEPRECATED: These notifiers are no longer used.
    # Message generation methods are called directly by ArenaBroadcaster.
    # TODO: Remove in next major version
    super().__init__(*args, **kwargs)
```

---

## 4. **前端 JavaScript** - WebSocket 端點路徑

**問題**：前端 JS 連接到舊的 API WebSocket 端點

**受影響文件**：
- `static/js/display_audience.js` (Line 781)
- `static/js/display_alliance_station.js` (Line 127)
- `static/js/match_control.js` (Line 390-391)
- 其他顯示和設置頁面

**當前路徑**：
```javascript
// 觀眾顯示
websocket = new wsHandler("/api/displays/audience/websocket", {...});

// 聯盟站顯示
websocket = new wsHandler("/api/displays/alliance_station/websocket", {...});

// 比賽控制
websocket = new wsHandler('/api/match/control/websocket', {...});
```

**問題分析**：
1. `/api/displays/audience/websocket` 仍存在但只是簡單的連接，不發送狀態更新
2. 真正的狀態更新來自 `/ws/displays/audience`（新端點）
3. 前端需要同時連接兩個 WebSocket：
   - `/api/...` 用於發送命令（設置、控制）
   - `/ws/...` 用於接收狀態更新

**修正方案**：

### 方案 A：保持雙連接（推薦）
```javascript
// display_audience.js
// 連接 1: 接收狀態更新
const stateWebSocket = new WebSocket('ws://localhost:8080/ws/displays/audience');
stateWebSocket.onmessage = function(event) {
    const msg = JSON.parse(event.data);
    // { type: 'match_time', data: {...} }
    
    // 根據 type 調用對應的 handler
    const handlers = {
        'alliance_selection': handleAllianceSelection,
        'audience_display_mode': handleAudienceDisplayMode,
        'lower_third': handleLowerThird,
        'match_load': handleMatchLoad,
        'match_time': handleMatchTime,
        'match_timing': handleMatchTiming,
        'play_sound': handlePlaySound,
        'realtime_score': handleRealtimeScore,
        'score_posted': handleScorePosted,
    };
    
    if (handlers[msg.type]) {
        handlers[msg.type](msg.data);
    }
};

// 連接 2: 發送命令和註冊顯示（保持原有）
const cmdWebSocket = new wsHandler("/api/displays/audience/websocket", {});
```

### 方案 B：合併為單一連接
修改 `/api/displays/audience/websocket` 以訂閱 WebSocketManager：

```python
# web/api/displays_audience.py
@router.websocket('/websocket')
async def websocket_endpoint(websocket: WebSocket, request: Request):
    await websocket.accept()
    display = await register_display(websocket)
    
    # 訂閱狀態更新
    ws_manager = request.app.state.ws_manager
    await ws_manager.connect(websocket, [
        'audience_display_mode', 'match_time', 'match_load',
        'realtime_score', 'score_posted', 'play_sound', 'lower_third'
    ])
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
```

---

## 5. **Web API 路由** - 其他 WebSocket 端點

**需要檢查的文件**：

### 顯示端點：
- ✅ `displays_audience.py` - 簡單連接，但不發送狀態
- ✅ `displays_alliance_station.py` - 簡單連接
- ⚠️ `displays_rankings.py` - 需要檢查是否需要狀態更新
- ⚠️ `displays_queueing.py` - 可能需要隊列更新
- ⚠️ `displays_announcer.py` - 可能需要比賽訊息

### 控制/設置端點：
- `match_control.py` - **沒有 WebSocket**（註釋提到用 WebSocket 更新）
- `setup_displays.py` - 用於配置顯示
- `setup_lower_thirds.py` - 用於管理字幕
- `setup_field_testing.py` - 用於測試功能

**問題**：
- 某些端點可能需要接收狀態更新
- 控制頁面需要看到即時狀態

---

## 6. **ws/__init__.py** - 導出清理

**問題**：仍然導出舊的 notifier 函數

**位置**：
- Line 1: `from .notifier import Notifier, handle_notifiers, write_notifier`

**影響**：
- 程式碼引用混亂
- 暗示這些功能仍在使用

**修正方案**：
```python
# ws/__init__.py
# DEPRECATED: Notifier system has been replaced by ArenaBroadcaster
# These are kept for backward compatibility only
from .notifier import Notifier, handle_notifiers, write_notifier

__all__ = []  # 不導出任何東西，標記為廢棄
```

---

## 7. **static/js/wsHandler** - WebSocket 輔助類

**問題**：需要確認 wsHandler 類的實現

**可能需要**：
- 確認是否支持新的訊息格式 `{type: '', data: {}}`
- 可能需要適配器模式

**檢查清單**：
```javascript
// 確認 wsHandler 是否正確處理新格式
class wsHandler {
    constructor(url, handlers) {
        this.ws = new WebSocket(url);
        this.handlers = handlers;
        
        this.ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            
            // 支持舊格式：直接是 event object
            if (msg.type && this.handlers[msg.type]) {
                this.handlers[msg.type]({ data: msg.data });
            }
            
            // 支持新格式：{type, data}
            else if (msg.type && msg.data) {
                if (this.handlers[msg.type]) {
                    this.handlers[msg.type](msg.data);
                }
            }
        };
    }
}
```

---

## 修正優先級

### P0 - 高優先級（影響核心功能）
1. ✅ **field/arena.py** - Arena notifier 替換（已完成）
2. **field/display.py** - Display 配置廣播
3. **field/event_status.py** - 賽事狀態廣播
4. **前端 JavaScript** - WebSocket 連接適配

### P1 - 中優先級（改善體驗）
5. **Web API 路由** - 統一 WebSocket 處理
6. **field/arena_notifiers.py** - 清理舊 notifier 初始化

### P2 - 低優先級（程式碼清理）
7. **ws/__init__.py** - 導出清理
8. **文檔更新** - API 文檔同步

---

## 測試計劃

### 單元測試
- ✅ Arena API 測試（已通過）
- ⏳ Display 配置測試（待添加）
- ⏳ Event Status 測試（待添加）

### 集成測試
- ⏳ 前端 WebSocket 連接測試
- ⏳ 多顯示器同步測試
- ⏳ 比賽控制流程測試

### 手動測試
- [ ] 觀眾顯示更新
- [ ] 聯盟站顯示更新
- [ ] 比賽控制面板
- [ ] 顯示器配置
- [ ] 下三分字幕

---

## 預估工作量

| 項目 | 工作量 | 狀態 |
|------|--------|------|
| Display 配置廣播 | 2小時 | ⏳ 待處理 |
| Event Status 廣播 | 1小時 | ⏳ 待處理 |
| 前端 JS 適配 | 4小時 | ⏳ 待處理 |
| API 路由統一 | 3小時 | ⏳ 待處理 |
| 程式碼清理 | 1小時 | ⏳ 待處理 |
| 測試驗證 | 3小時 | ⏳ 待處理 |
| **總計** | **14小時** | |

---

## 風險評估

### 高風險
- 前端 JS 修改可能破壞現有功能
- 需要仔細測試每個顯示頁面

### 中風險
- Display 配置可能影響顯示器註冊流程
- 需要確保向後兼容

### 低風險
- 程式碼清理不影響功能
- 可以逐步進行

---

## 建議執行順序

1. **階段 1：修正 Display 和 Event Status**
   - 修正 `field/display.py`
   - 修正 `field/event_status.py`
   - 運行測試確保不破壞功能

2. **階段 2：前端適配（最重要）**
   - 更新 `display_audience.js`
   - 更新 `display_alliance_station.js`
   - 更新 `match_control.js`
   - 測試所有顯示頁面

3. **階段 3：API 路由統一**
   - 更新各個 display 路由
   - 實現統一的狀態訂閱

4. **階段 4：清理和文檔**
   - 清理舊的 notifier 初始化
   - 更新 API 文檔
   - 添加使用範例

---

## 完成標準

- [ ] 所有顯示頁面能正確接收狀態更新
- [ ] 比賽控制面板功能正常
- [ ] 顯示器配置可以動態更新
- [ ] 賽事狀態訊息正確顯示
- [ ] 所有測試通過
- [ ] 無 console 錯誤
- [ ] 文檔更新完成
