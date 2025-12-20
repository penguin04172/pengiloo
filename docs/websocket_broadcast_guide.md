# WebSocket 廣播系統使用指南

## 概述

新的多進程架構使用 **IPC（Inter-Process Communication）** 來在 Arena 進程和 Web 進程之間傳遞訊息，然後通過 **WebSocket** 推送給前端。

## 架構流程

```
Arena 進程 → IPC → Web 進程 → WebSocket → 前端頁面
```

1. **Arena 進程**：比賽邏輯處理，生成狀態更新
2. **IPC**：使用 multiprocessing.Queue 在進程間傳遞訊息
3. **Web 進程**：FastAPI 服務器，管理 WebSocket 連接
4. **WebSocket**：實時推送到不同的顯示頁面

## 在 Arena 中廣播訊息

### 方法 1: 使用 ArenaBroadcaster（推薦）

```python
# Arena 類中已有 self.broadcaster 實例

# 廣播比賽時間
self.broadcaster.notify_match_time()

# 廣播即時分數
self.broadcaster.notify_realtime_score()

# 廣播比賽載入資訊
self.broadcaster.notify_match_load()

# 廣播聲音播放
self.broadcaster.notify_play_sound('match_start')

# 廣播競技場狀態
self.broadcaster.notify_arena_status()
```

### 方法 2: 直接使用 broadcast_state

```python
# 自訂訊息類型和資料
self.broadcast_state('custom_message', {
    'field1': 'value1',
    'field2': 123
})
```

## 訊息類型

### 比賽相關
- `match_time`: 比賽計時器更新
- `match_load`: 比賽載入（隊伍資訊等）
- `match_timing`: 比賽時間配置
- `match_state`: 比賽狀態變更

### 分數相關
- `realtime_score`: 即時分數更新
- `score_posted`: 比賽結果公布
- `scoring_status`: 計分面板狀態

### 顯示相關
- `audience_display_mode`: 觀眾顯示模式
- `alliance_station_display_mode`: 聯盟站顯示模式
- `lower_third`: 下三分之一字幕
- `display_configuration`: 顯示配置

### 系統相關
- `arena_status`: 競技場狀態（連接、Ready 等）
- `event_status`: 賽事狀態
- `play_sound`: 播放聲音指令
- `reload_displays`: 重新載入顯示

## WebSocket 端點

### 前端連接方式

#### 1. 觀眾顯示 (`/ws/displays/audience`)
接收訊息：
- audience_display_mode
- match_time
- match_load
- realtime_score
- score_posted
- play_sound
- lower_third

```javascript
// audience.html
const ws = new WebSocket('ws://localhost:8080/ws/displays/audience');
ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    console.log('Type:', msg.type, 'Data:', msg.data);
    
    if (msg.type === 'realtime_score') {
        updateScore(msg.data);
    } else if (msg.type === 'match_time') {
        updateTimer(msg.data);
    }
};
```

#### 2. 聯盟站顯示 (`/ws/displays/alliance_station`)
接收訊息：
- alliance_station_display_mode
- match_load
- match_time
- realtime_score
- scoring_status

```javascript
// alliance_station.html
const ws = new WebSocket('ws://localhost:8080/ws/displays/alliance_station');
```

#### 3. 排名顯示 (`/ws/displays/ranking`)
接收訊息：
- rankings
- lower_third

#### 4. 比賽控制 (`/ws/match_control`)
接收訊息：
- arena_status
- match_load
- match_time
- realtime_score
- scoring_status

```javascript
// match_control.html
const ws = new WebSocket('ws://localhost:8080/ws/match_control');
```

#### 5. 通用端點 (`/ws/arena`)
接收所有類型的訊息

## 訊息格式

所有 WebSocket 訊息使用統一格式：

```json
{
    "type": "message_type",
    "data": {
        // 訊息內容
    }
}
```

### 範例

#### match_time
```json
{
    "type": "match_time",
    "data": {
        "match_state": "AUTO_PERIOD",
        "match_time_sec": 15
    }
}
```

#### realtime_score
```json
{
    "type": "realtime_score",
    "data": {
        "red": {
            "score": { /* Score object */ },
            "score_summary": { /* ScoreSummary object */ }
        },
        "blue": {
            "score": { /* Score object */ },
            "score_summary": { /* ScoreSummary object */ }
        },
        "match_state": "TELEOP_PERIOD"
    }
}
```

#### play_sound
```json
{
    "type": "play_sound",
    "data": {
        "sound": "match_start"
    }
}
```

## 在 Arena 中替換舊的 notifier

### 舊代碼（使用 notifier）
```python
await self.match_time_notifier.notify()
await self.realtime_score_notifier.notify()
await self.audience_display_mode_notifier.notify()
```

### 新代碼（使用 broadcaster）
```python
self.broadcaster.notify_match_time()
self.broadcaster.notify_realtime_score()
self.broadcaster.notify_audience_display_mode()
```

## 添加新的訊息類型

### 1. 在 Arena 中添加生成器方法

```python
# field/arena_notifiers.py
def generate_custom_message(self):
    return {
        'field1': self.some_value,
        'field2': self.another_value
    }
```

### 2. 在 ArenaBroadcaster 添加便捷方法

```python
# field/arena_broadcast.py
def notify_custom(self):
    """Broadcast custom message."""
    self.broadcast('custom_message')
```

### 3. 在 WebSocket 路由添加訂閱

```python
# web/websocket_routes.py
@router.websocket("/ws/displays/custom")
async def websocket_custom_display(websocket: WebSocket, request: Request):
    ws_manager = request.app.state.ws_manager
    await ws_manager.connect(websocket, ['custom_message'])
    # ...
```

### 4. 在前端處理訊息

```javascript
ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.type === 'custom_message') {
        // 處理自訂訊息
        handleCustomMessage(msg.data);
    }
};
```

## 測試 WebSocket 連接

使用 Chrome DevTools 或 websocat：

```bash
# 安裝 websocat
cargo install websocat

# 測試連接
websocat ws://localhost:8080/ws/arena

# 或使用 wscat
npm install -g wscat
wscat -c ws://localhost:8080/ws/displays/audience
```

## 注意事項

1. **訊息頻率**：避免過於頻繁發送相同訊息（如 match_time 每 100ms 一次就夠了）
2. **錯誤處理**：WebSocket 可能斷線，前端需實現重連機制
3. **訂閱管理**：選擇合適的 WebSocket 端點，避免接收不需要的訊息
4. **資料序列化**：確保廣播的資料可以 JSON 序列化（使用 Pydantic model.model_dump()）

## 完整範例

### Arena 中廣播比賽開始

```python
async def start_match(self):
    """開始比賽"""
    self.match_state = MatchState.AUTO_PERIOD
    self.match_start_time = datetime.now()
    
    # 廣播比賽載入資訊
    self.broadcaster.notify_match_load()
    
    # 廣播顯示模式切換
    self.audience_display_mode = 'match'
    self.broadcaster.notify_audience_display_mode()
    
    # 播放開始聲音
    self.broadcaster.notify_play_sound('match_start')
    
    # 開始計時器循環（會定期廣播 match_time）
    logger.info(f"Match {self.current_match.display_name} started")
```

### 前端處理多種訊息

```html
<!-- audience_display.html -->
<script>
const ws = new WebSocket('ws://localhost:8080/ws/displays/audience');

ws.onopen = () => console.log('Connected to Arena');
ws.onerror = (error) => console.error('WebSocket error:', error);
ws.onclose = () => {
    console.log('Disconnected, reconnecting...');
    setTimeout(() => location.reload(), 3000);
};

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    
    switch (msg.type) {
        case 'match_time':
            updateMatchTimer(msg.data.match_time_sec);
            break;
        case 'realtime_score':
            updateScores(msg.data.red, msg.data.blue);
            break;
        case 'play_sound':
            playSound(msg.data.sound);
            break;
        case 'audience_display_mode':
            switchDisplayMode(msg.data);
            break;
        default:
            console.log('Unknown message type:', msg.type);
    }
};
</script>
```
