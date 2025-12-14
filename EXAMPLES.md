# 使用範例 / Usage Examples

## 範例 1：基本使用
直接執行程式，使用預設設定：
```bash
python stock_crawler.py
```

## 範例 2：自訂股票代碼
修改 `CrawlerConfig` 類別中的 `STOCK_SYMBOLS`：
```python
STOCK_SYMBOLS: List[str] = ["2330", "2454", "2603", "1301"]
```

## 範例 3：修改日期範圍
```python
START_DATE: str = "2024-03-01"
END_DATE: str = "2024-03-31"
```

## 範例 4：無頭模式執行（背景執行）
在 `initialize_browser()` 函式中修改：
```python
browser = await playwright.chromium.launch(
    headless=True,  # 改為 True
    slow_mo=0       # 設為 0 加快速度
)
```

## 範例 5：針對不同網站調整選擇器
根據目標網站的 HTML 結構，修改選擇器：
```python
SELECTORS = {
    "stock_input": "input[name='symbol']",      # CSS Selector
    "date_input": "#date",                       # ID Selector
    "chart_tab": "button.chart-view",            # Class Selector
    "submit_button": "//button[text()='查詢']"  # XPath
}
```

## 範例 6：調整 API 監聽模式
如果目標 API 路徑不同，修改模式：
```python
# 完整路徑匹配
API_ENDPOINT_PATTERN: str = "**/api/v2/market/stock/data**"

# 或使用部分路徑
API_ENDPOINT_PATTERN: str = "**/stock/quotes**"
```

## 範例 7：包含週末日期
如果需要爬取週末資料，修改 `main()` 函式：
```python
dates = generate_date_range(
    CrawlerConfig.START_DATE,
    CrawlerConfig.END_DATE,
    skip_weekends=False  # 改為 False
)
```

## 範例 8：單一股票單一日期爬取
可以直接呼叫單一函式進行測試：
```python
async def test_single():
    playwright, browser, page = await initialize_browser()
    collector = ResponseCollector()
    await collector.start_monitoring(page)
    
    await navigate_to_page(page, CrawlerConfig.BASE_URL)
    data = await crawl_stock_data_for_date(page, collector, "2330", "2024-01-02")
    
    collector.stop_monitoring()
    await close_browser(playwright, browser)
    
    print(f"收集到的資料: {data}")

# 執行測試
# asyncio.run(test_single())
```

## 範例 9：加入等待時間避免過快
如果網站有速率限制，可以在迴圈中加入等待：
```python
# 在 crawl_multiple_stocks() 函式中，每支股票之間加入延遲
for symbol in stock_symbols:
    stock_data = await crawl_stock_data_for_date(
        page, collector, symbol, date
    )
    daily_data[symbol] = stock_data
    
    # 加入 3 秒延遲
    await page.wait_for_timeout(3000)
```

## 範例 10：客製化輸出格式
修改 `save_daily_data()` 函式以改變輸出結構：
```python
def save_daily_data(date: str, stock_data: List[Dict[str, Any]]) -> None:
    # 自訂檔名格式
    filename = f"stocks_{date.replace('-', '')}.json"
    
    # 自訂資料結構
    output_data = {
        "trading_date": date,
        "market": "TWS",
        "stocks": stock_data,
        "metadata": {
            "crawled_at": datetime.now().isoformat(),
            "version": "1.0"
        }
    }
    
    save_to_json(output_data, filename)
```

## 進階：錯誤重試機制
如果需要在失敗時重試：
```python
async def crawl_with_retry(page, collector, symbol, date, max_retries=3):
    """帶重試機制的爬蟲"""
    for attempt in range(max_retries):
        try:
            data = await crawl_stock_data_for_date(page, collector, symbol, date)
            if data:
                return data
        except Exception as e:
            print(f"❌ 第 {attempt + 1} 次嘗試失敗: {e}")
            if attempt < max_retries - 1:
                await page.wait_for_timeout(5000)  # 等待 5 秒再重試
    
    print(f"❌ 已達最大重試次數，放棄 {symbol} @ {date}")
    return []
```

## 疑難排解

### 問題 1：找不到元素
- 檢查選擇器是否正確
- 增加 `wait_for_selector()` 的等待時間
- 使用瀏覽器開發者工具確認元素存在

### 問題 2：無法攔截 API
- 確認 API 路徑模式是否正確
- 使用瀏覽器開發者工具的 Network 面板查看實際 API 路徑
- 確保在操作觸發前就已開始監聽

### 問題 3：資料未儲存
- 檢查是否有寫入權限
- 確認輸出目錄是否正確建立
- 查看錯誤訊息

### 問題 4：執行速度太慢
- 將 `headless` 改為 `True`
- 將 `slow_mo` 改為 `0`
- 減少不必要的等待時間
