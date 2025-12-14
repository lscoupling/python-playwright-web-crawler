# Python Playwright Web Crawler

一個結構清晰、適合教學的 Python + Playwright 股票資料爬蟲程式

## 功能特色

- ✅ **清楚的功能分離**：每個函式只負責一件事
- ✅ **非同步架構**：使用 async/await 提升效能
- ✅ **Response 監聽**：攔截 API Response 取得資料
- ✅ **智慧日期處理**：自動跳過週末
- ✅ **完整註解**：適合初學者學習
- ✅ **資料儲存**：自動儲存為 JSON 格式

## 程式結構

```
stock_crawler.py
├── 1. 設定區 (Configuration Section)
│   └── CrawlerConfig 類別：集中管理所有設定
├── 2. 瀏覽器管理 (Browser Management)
│   ├── initialize_browser()：初始化瀏覽器
│   └── close_browser()：關閉瀏覽器
├── 3. 頁面操作 (Page Operations)
│   ├── navigate_to_page()：導航到頁面
│   ├── switch_to_chart_view()：切換圖表檢視
│   ├── set_stock_symbol()：設定股票代碼
│   └── set_target_date()：設定日期
├── 4. Response 監聽與資料收集 (Response Monitoring)
│   └── ResponseCollector 類別：監聽並收集 API 資料
├── 5. 日期處理工具 (Date Utilities)
│   ├── parse_date()：解析日期
│   ├── is_weekend()：判斷週末
│   └── generate_date_range()：產生日期範圍（跳過週末）
├── 6. 資料儲存 (Data Storage)
│   ├── ensure_output_directory()：確保輸出目錄存在
│   ├── save_to_json()：儲存 JSON 檔案
│   └── save_daily_data()：儲存單日資料
└── 7. 主流程控制 (Main Flow Control)
    ├── crawl_stock_data_for_date()：爬取單一股票資料
    ├── crawl_multiple_stocks()：爬取多支股票資料
    └── main()：主程式進入點
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

直接執行程式：
```bash
python stock_crawler.py
```

### 自訂設定

修改 `stock_crawler.py` 中的 `CrawlerConfig` 類別：

```python
class CrawlerConfig:
    # 修改股票代碼
    STOCK_SYMBOLS = ["2330", "2317", "2454"]
    
    # 修改日期範圍
    START_DATE = "2024-01-01"
    END_DATE = "2024-01-10"
    
    # 修改目標網站
    BASE_URL = "https://www.example-stock.com/chart"
    
    # 修改選擇器
    SELECTORS = {
        "stock_input": "#stock-symbol",
        "date_input": "#date-picker",
        "chart_tab": "#chart-tab",
        "submit_button": "#submit-btn"
    }
```

## 輸出結果

資料會儲存在 `data/` 目錄下，每個日期一個 JSON 檔案：

```
data/
├── stock_data_2024-01-01.json
├── stock_data_2024-01-02.json
└── stock_data_2024-01-03.json
```

每個 JSON 檔案格式：
```json
{
  "date": "2024-01-01",
  "crawled_at": "2024-01-01T10:30:00.123456",
  "total_records": 3,
  "data": {
    "2330": [...],
    "2317": [...],
    "2454": [...]
  }
}
```

## 程式設計特點

### 1. 功能分離
每個函式都有單一職責，易於理解和維護。

### 2. Response 監聽
使用 Playwright 的 `page.on("response")` 監聽 API 回應：
```python
page.on("response", self._handle_response)
```

### 3. 週末跳過
自動判斷並跳過週六、週日：
```python
def is_weekend(date: datetime) -> bool:
    return date.weekday() >= 5  # 5=Saturday, 6=Sunday
```

### 4. 非同步架構
全程使用 async/await 提升效能：
```python
async def main():
    browser, page = await initialize_browser()
    await navigate_to_page(page, url)
    # ...
```

## 學習重點

適合學習以下概念：
- 🎯 Python 非同步程式設計 (async/await)
- 🎯 Playwright 網頁自動化
- 🎯 API Response 攔截與監聽
- 🎯 日期處理與迴圈控制
- 🎯 JSON 資料儲存
- 🎯 程式碼組織與結構設計

## 注意事項

1. 請將 `BASE_URL` 和 `SELECTORS` 修改為實際目標網站的設定
2. 程式預設以非無頭模式執行（可看到瀏覽器），方便觀察過程
3. 若要在背景執行，請將 `headless=False` 改為 `headless=True`
4. 請遵守目標網站的使用條款和爬蟲規範

## 授權

MIT License
