# FRC FMS 系統開發路線圖 (Roadmap)

本文件規劃了基於 Python (FastAPI + Multiprocessing) 的 FRC 競賽管理系統開發流程。

## 系統架構概觀

*   **後端框架**: FastAPI (非同步 Web 服務)
*   **資料庫**: SQLite + SQLModel (ORM)
*   **即時通訊**: Websockets
*   **進程管理**: Python `multiprocessing` (用於隔離 Web 服務、場地控制、硬體通訊)
*   **套件管理**: uv

## 階段一：基礎建設與核心架構 (Foundation & Core)
**目標**: 建立專案結構，設定資料庫，並完成基礎的 Web 服務與即時通訊機制。

1.  **專案初始化**
    *   [x] 建立目錄結構 (`backend/`, `docs/`, `scripts/`)
    *   [x] 設定 `pyproject.toml` 依賴 (FastAPI, SQLModel, Uvicorn, Websockets, Loguru)
    *   [ ] 設定環境變數管理 (`.env`, `pydantic-settings`)

2.  **資料庫設計 (Database Schema)**
    *   [x] 設計 `Event` (賽事資訊)
    *   [x] 設計 `Team` (隊伍資料)
    *   [x] 設計 `Match` (賽程表: 資格賽/淘汰賽)
    *   [x] 設計 `MatchResult` (比賽結果、分數)

3.  **即時通訊核心 (Notifier System)**
    *   [x] 實作 WebSocket Manager (管理連線用戶：裁判、計分員、觀眾顯示器)
    *   [x] 設計 Pub/Sub 機制 (用於不同 Process 間的訊息傳遞，例如：場地狀態改變 -> 推播給前端)

## 階段二：場地與比賽控制核心 (Arena & Match Control)
**目標**: 實作 FRC 比賽的核心流程控制 (狀態機)。

1.  **場地狀態機 (Arena State Machine)**
    *   [x] 定義狀態: `Idle`, `PreStart`, `Auto`, `Pause`, `Teleop`, `End`, `PostMatch`, `Timeout`, `E-Stop`
    *   [x] 實作狀態轉換邏輯與安全檢查
    *   [x] 實作場地控制 API (Start/Abort/Reset)

2.  **計時器與音效 (Timer & Audio)**
    *   [x] 實作高精度比賽計時器
    *   [ ] 整合音效觸發 (Start, End, Abort, Last 20s)

3.  **多進程整合 (Multiprocessing)**
    *   [x] 將場地控制邏輯獨立為單獨的 Process (避免 Web Request 阻塞比賽邏輯)
    *   [x] 建立 Process 間通訊管道 (Queue/Pipe)

## 階段三：賽事管理與排程 (Tournament Management)
**目標**: 管理隊伍、產生賽程表與排名。

1.  **隊伍管理**
    *   [x] 實作隊伍 CRUD API
    *   [x] 匯入/匯出隊伍清單 (CSV/TBA API 整合)
    *   [x] 實作隊伍列表與匯入頁面

2.  **賽程管理**
    *   [x] 實作賽程 CRUD API
    *   [x] 實作賽事資訊 CRUD API
    *   [x] 實作賽程列表頁面
    *   [x] 實作賽程時段管理 (Schedule Blocks)

3.  **資格賽 (Qualification)**
    *   [x] 實作賽程產生演算法 (確保隊伍間隔、聯盟平衡)
    *   [x] 實作排名計算 (Ranking Points, Tiebreakers)
    *   [x] 實作排名列表頁面

4.  **淘汰賽 (Playoffs)**
    *   [x] 聯盟選拔系統 (Alliance Selection)
    *   [x] 單淘汰/雙淘汰 (Double Elimination) 賽程樹產生
    *   [x] 賽程推進邏輯 (Advancement)

## 階段四：硬體與網路控制 (Hardware & Network)
**目標**: 控制場地硬體與網路環境。

1.  **網路控制 (OpenWRT)**
    *   [ ] 使用 `paramiko` 實作 SSH 連線
    *   [ ] 自動切換 VLAN/SSID (根據賽程表自動設定場地網路)

2.  **周邊硬體 (Peripherals)**
    *   [ ] 整合 FMS Light (場地燈號)
    *   [ ] 整合 E-Stop 訊號輸入
    *   [ ] 整合裁判控制器 (計分板輸入)

## 階段五：前端介面與整合 (Frontend & Integration)
**目標**: 提供使用者操作介面。

1.  **管理後台**
    *   [x] 建立基礎 Dashboard (HTML/JS/Bootstrap)
    *   [x] 整合 Websocket 即時狀態顯示
    *   [x] 整合場地控制按鈕 (Start/Abort/Reset)
    *   [x] 實作賽程產生與管理介面
    *   [x] 實作淘汰賽產生與推進介面
    *   [ ] 賽事設定、狀態監控、手動控制面板

2.  **裁判/計分介面**
    *   [ ] 即時計分頁面 (RWD 設計，支援平板)

3.  **現場顯示 (Audience Display)**
    *   [ ] 大螢幕計分板、排名顯示、選拔畫面

## 階段六：測試與部署 (Testing & Deployment)
1.  單元測試 (Unit Tests)
2.  模擬測試 (Simulation Mode - 不連接硬體也能跑流程)
3.  Windows/Linux 跨平台相容性測試
