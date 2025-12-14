# CMoney 股票爬蟲

基於 Playwright 的 CMoney 股票資料爬蟲，採用清晰的多資料夾架構組織程式碼。

## 功能特色

- ✅ **模組化設計**：配置、爬蟲、工具完全分離
- ✅ **非同步架構**：使用 async/await 提升效能
- ✅ **Response 監聽**：攔截 API Response 取得資料
- ✅ **自動跳過週末**：智慧日期處理
- ✅ **非無頭模式**：可視化瀏覽器操作
- ✅ **批次處理**：支援多股票同時抓取
- ✅ **資料儲存**：自動儲存為 JSON 格式

## 專案架構

```
.
├── src/
│   ├── config/              # 配置模組
│   │   ├── __init__.py
│   │   └── settings.py      # 爬蟲配置設定
│   ├── crawlers/            # 爬蟲模組
│   │   ├── __init__.py
│   │   └── cmoney_crawler.py  # CMoney 爬蟲核心類別
│   ├── utils/               # 工具模組
│   │   ├── __init__.py
│   │   └── date_utils.py    # 日期處理工具
│   └── __init__.py
├── data/                    # 資料儲存目錄
├── main.py                  # 主程式入口
└── requirements.txt         # 相依套件
```

## 安裝步驟

1. **安裝相依套件**：
```bash
pip install -r requirements.txt
```

2. **安裝 Playwright 瀏覽器**：
```bash
playwright install chromium
```

## 使用方式

### 基本使用

2. **安裝 Playwright 瀏覽器**：
```bash
playwright install chromium
```

## 使用方法

### 設定配置

編輯 [src/config/settings.py](src/config/settings.py) 修改配置：

```python
class CrawlerSettings:
    # 要抓取的股票
    STOCKS = {
        "萬海": "2615",
        "台積電": "2330",
        # 新增更多股票...
    }
    
    # 日期範圍
    START_DATE = datetime(2025, 11, 1)
    END_DATE = datetime(2025, 11, 28)
    
    # 等待時間 (秒)
    WAIT_AFTER_INPUT = 5
```

### 執行程式

直接執行主程式：
```bash
python main.py
```

程式會自動：
1. 開啟瀏覽器（非無頭模式）
2. 依序抓取設定的股票資料
3. 自動跳過週末日期
4. 將資料儲存為 JSON 格式

## 輸出結果

資料會儲存在以下格式的目錄中：
```
data_股票名稱_股票代碼/
  └── 股票代碼_日期.json
```

例如：
```
data_萬海_2615/
  ├── 2615_20251101.json
  ├── 2615_20251104.json
  ├── 2615_20251105.json
  └── ...
```

每個 JSON 檔案包含該日期的完整股票資料。

## 模組說明

### 1. 配置模組 (src/config/)
- **settings.py**：集中管理所有配置參數
  - 股票清單
  - 日期範圍
  - URL 和選擇器
  - 超時設定

### 2. 爬蟲模組 (src/crawlers/)
- **cmoney_crawler.py**：CMoney 爬蟲核心類別
  - `capture_stock()`：抓取單一股票資料
  - `_handle_response()`：處理網路回應
  - `_process_date()`：處理單一日期
  - `_save_data()`：儲存資料

### 3. 工具模組 (src/utils/)
- **date_utils.py**：日期處理工具
  - `is_weekend()`：判斷是否為週末
  - `generate_date_range()`：產生日期範圍

## 程式設計特點

### 🎯 清晰的類別設計
```python
class CMoneyCrawler:
    """CMoney 股票資料爬蟲"""
    
    async def capture_stock(self, name: str, stock_id: str):
        """抓取單一股票資料"""
```

### 🎯 Response 監聽機制
自動攔截並儲存 API 回應：
```python
self.page.on("response", lambda response: asyncio.create_task(
    self._handle_response(response, api_pattern)
))
```

### 🎯 智慧日期處理
自動跳過週末：
```python
for date in generate_date_range(START_DATE, END_DATE):
    if is_weekend(date):
        continue
```

### 🎯 模組化架構
- 配置與邏輯分離
- 易於維護和擴充
- 可重複使用的工具函式

## 自訂設定範例

### 新增更多股票
編輯 [src/config/settings.py](src/config/settings.py)：
```python
STOCKS = {
    "台積電": "2330",
    "聯發科": "2454",
    "鴻海": "2317",
    "萬海": "2615",
}
```

### 調整日期範圍
```python
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)
```

### 修改等待時間
如果網路較慢，可增加等待時間：
```python
WAIT_AFTER_INPUT = 8  # 增加到 8 秒
```

## 注意事項

1. ⚠️ 程式使用非無頭模式，會顯示瀏覽器視窗
2. ⚠️ 請確保網路連線穩定
3. ⚠️ 抓取大量資料時請注意對方伺服器負載
4. ⚠️ 請遵守 CMoney 網站使用條款
5. ⚠️ 週末不會有股市交易資料

## 常見問題

### Q: 如何改為無頭模式？
A: 在 [src/config/settings.py](src/config/settings.py) 中修改：
```python
HEADLESS = True
```

### Q: 程式執行很慢怎麼辦？
A: 減少等待時間：
```python
WAIT_AFTER_INPUT = 3
```

### Q: 如何只抓取特定日期？
A: 設定相同的開始和結束日期：
```python
START_DATE = datetime(2025, 11, 5)
END_DATE = datetime(2025, 11, 5)
```

## 授權

MIT License
