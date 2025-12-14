#!/usr/bin/env python3
"""
股票資料爬蟲程式 (Stock Data Web Crawler)
使用 Playwright 進行網頁自動化與 API 資料擷取
適合教學用途 - 功能分離清楚、易於理解
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page, Response


# ============================================================================
# 1. 設定區 (Configuration Section)
# ============================================================================

class CrawlerConfig:
    """爬蟲設定類別 - 集中管理所有設定參數"""
    
    # 目標股票代碼列表
    STOCK_SYMBOLS: List[str] = ["2330", "2317", "2454"]
    
    # 爬取日期範圍
    START_DATE: str = "2024-01-01"
    END_DATE: str = "2024-01-10"
    
    # 目標網站 URL
    BASE_URL: str = "https://www.example-stock.com/chart"
    
    # 頁面選擇器 (Selectors)
    SELECTORS = {
        "stock_input": "#stock-symbol",
        "date_input": "#date-picker",
        "chart_tab": "#chart-tab",
        "submit_button": "#submit-btn"
    }
    
    # API 監聽設定
    API_ENDPOINT_PATTERN: str = "**/api/stock/data**"
    
    # 輸出檔案設定
    OUTPUT_DIR: str = "data"
    OUTPUT_FILENAME: str = "stock_data_{date}.json"


# ============================================================================
# 2. 瀏覽器管理 (Browser Management)
# ============================================================================

async def initialize_browser() -> tuple[Browser, Page]:
    """
    初始化瀏覽器與頁面
    
    Returns:
        tuple: (browser, page) 瀏覽器與頁面物件
    """
    print("🚀 正在啟動瀏覽器...")
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=False,  # 設為 True 可在背景執行
        slow_mo=100      # 放慢操作速度，方便觀察
    )
    
    # 建立新頁面
    page = await browser.new_page()
    
    # 設定視窗大小
    await page.set_viewport_size({"width": 1920, "height": 1080})
    
    print("✅ 瀏覽器啟動完成")
    return browser, page


async def close_browser(browser: Browser) -> None:
    """
    關閉瀏覽器
    
    Args:
        browser: 要關閉的瀏覽器物件
    """
    print("🔒 正在關閉瀏覽器...")
    await browser.close()
    print("✅ 瀏覽器已關閉")


# ============================================================================
# 3. 頁面操作 (Page Operations)
# ============================================================================

async def navigate_to_page(page: Page, url: str) -> None:
    """
    導航到指定頁面
    
    Args:
        page: Playwright 頁面物件
        url: 目標網址
    """
    print(f"🌐 正在前往頁面: {url}")
    await page.goto(url, wait_until="networkidle")
    print("✅ 頁面載入完成")


async def switch_to_chart_view(page: Page) -> None:
    """
    切換到圖表檢視模式
    
    Args:
        page: Playwright 頁面物件
    """
    print("📊 切換到圖表檢視...")
    chart_tab_selector = CrawlerConfig.SELECTORS["chart_tab"]
    
    # 等待元素出現並點擊
    await page.wait_for_selector(chart_tab_selector)
    await page.click(chart_tab_selector)
    
    # 等待切換完成
    await page.wait_for_timeout(1000)
    print("✅ 已切換到圖表檢視")


async def set_stock_symbol(page: Page, symbol: str) -> None:
    """
    設定股票代碼
    
    Args:
        page: Playwright 頁面物件
        symbol: 股票代碼
    """
    print(f"📝 設定股票代碼: {symbol}")
    stock_input_selector = CrawlerConfig.SELECTORS["stock_input"]
    
    # 清空輸入框並輸入新代碼
    await page.fill(stock_input_selector, "")
    await page.fill(stock_input_selector, symbol)
    print(f"✅ 已設定股票代碼: {symbol}")


async def set_target_date(page: Page, date_str: str) -> None:
    """
    設定目標日期
    
    Args:
        page: Playwright 頁面物件
        date_str: 日期字串 (格式: YYYY-MM-DD)
    """
    print(f"📅 設定日期: {date_str}")
    date_input_selector = CrawlerConfig.SELECTORS["date_input"]
    
    # 設定日期
    await page.fill(date_input_selector, date_str)
    
    # 點擊提交按鈕
    submit_button_selector = CrawlerConfig.SELECTORS["submit_button"]
    await page.click(submit_button_selector)
    
    # 等待資料載入
    await page.wait_for_timeout(2000)
    print(f"✅ 已設定日期: {date_str}")


# ============================================================================
# 4. Response 監聽與資料收集 (Response Monitoring & Data Collection)
# ============================================================================

class ResponseCollector:
    """Response 資料收集器"""
    
    def __init__(self):
        self.collected_data: List[Dict[str, Any]] = []
        self.is_collecting: bool = False
    
    async def start_monitoring(self, page: Page) -> None:
        """
        開始監聽 API Response
        
        Args:
            page: Playwright 頁面物件
        """
        print("👂 開始監聽 API Response...")
        self.is_collecting = True
        
        # 註冊 response 事件處理器
        page.on("response", self._handle_response)
    
    async def _handle_response(self, response: Response) -> None:
        """
        處理攔截到的 Response
        
        Args:
            response: Playwright Response 物件
        """
        if not self.is_collecting:
            return
        
        # 檢查是否為目標 API
        if CrawlerConfig.API_ENDPOINT_PATTERN.replace("**", "") in response.url:
            print(f"🎯 攔截到目標 API: {response.url}")
            
            try:
                # 解析 JSON 資料
                data = await response.json()
                self.collected_data.append({
                    "url": response.url,
                    "status": response.status,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                })
                print(f"✅ 資料收集成功 (共 {len(self.collected_data)} 筆)")
            except Exception as e:
                print(f"❌ 資料解析失敗: {e}")
    
    def stop_monitoring(self) -> None:
        """停止監聽"""
        self.is_collecting = False
        print("🛑 停止監聽 API Response")
    
    def get_collected_data(self) -> List[Dict[str, Any]]:
        """
        取得收集到的資料
        
        Returns:
            List: 收集到的資料列表
        """
        return self.collected_data
    
    def clear_data(self) -> None:
        """清空收集到的資料"""
        self.collected_data = []


# ============================================================================
# 5. 日期處理工具 (Date Utilities)
# ============================================================================

def parse_date(date_str: str) -> datetime:
    """
    解析日期字串
    
    Args:
        date_str: 日期字串 (格式: YYYY-MM-DD)
    
    Returns:
        datetime: 日期物件
    """
    return datetime.strptime(date_str, "%Y-%m-%d")


def is_weekend(date: datetime) -> bool:
    """
    判斷是否為週末
    
    Args:
        date: 日期物件
    
    Returns:
        bool: True 表示週末，False 表示平日
    """
    # weekday(): 0=Monday, 5=Saturday, 6=Sunday
    return date.weekday() >= 5


def generate_date_range(start_date: str, end_date: str, skip_weekends: bool = True) -> List[str]:
    """
    產生日期範圍列表（可選擇跳過週末）
    
    Args:
        start_date: 起始日期 (格式: YYYY-MM-DD)
        end_date: 結束日期 (格式: YYYY-MM-DD)
        skip_weekends: 是否跳過週末
    
    Returns:
        List[str]: 日期字串列表
    """
    print(f"📆 產生日期範圍: {start_date} 到 {end_date}")
    
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    date_list = []
    current = start
    
    while current <= end:
        # 如果需要跳過週末，且當天是週末，則跳過
        if skip_weekends and is_weekend(current):
            print(f"⏭️  跳過週末: {current.strftime('%Y-%m-%d')} ({current.strftime('%A')})")
        else:
            date_list.append(current.strftime("%Y-%m-%d"))
        
        # 移到下一天
        current += timedelta(days=1)
    
    print(f"✅ 共產生 {len(date_list)} 個有效日期")
    return date_list


# ============================================================================
# 6. 資料儲存 (Data Storage)
# ============================================================================

def ensure_output_directory() -> Path:
    """
    確保輸出目錄存在
    
    Returns:
        Path: 輸出目錄路徑
    """
    output_dir = Path(CrawlerConfig.OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)
    return output_dir


def save_to_json(data: Dict[str, Any], filename: str) -> None:
    """
    將資料儲存為 JSON 檔案
    
    Args:
        data: 要儲存的資料
        filename: 檔案名稱
    """
    print(f"💾 正在儲存資料到: {filename}")
    
    # 確保輸出目錄存在
    output_dir = ensure_output_directory()
    file_path = output_dir / filename
    
    try:
        # 寫入 JSON 檔案 (使用縮排讓檔案易讀)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 資料已儲存: {file_path}")
    except Exception as e:
        print(f"❌ 儲存失敗: {e}")


def save_daily_data(date: str, stock_data: List[Dict[str, Any]]) -> None:
    """
    儲存單日資料
    
    Args:
        date: 日期字串
        stock_data: 股票資料列表
    """
    filename = CrawlerConfig.OUTPUT_FILENAME.format(date=date)
    
    # 組織資料結構
    output_data = {
        "date": date,
        "crawled_at": datetime.now().isoformat(),
        "total_records": len(stock_data),
        "data": stock_data
    }
    
    save_to_json(output_data, filename)


# ============================================================================
# 7. 主流程控制 (Main Flow Control)
# ============================================================================

async def crawl_stock_data_for_date(
    page: Page,
    collector: ResponseCollector,
    stock_symbol: str,
    date: str
) -> List[Dict[str, Any]]:
    """
    爬取單一股票在特定日期的資料
    
    Args:
        page: Playwright 頁面物件
        collector: Response 收集器
        stock_symbol: 股票代碼
        date: 日期字串
    
    Returns:
        List: 收集到的資料
    """
    print(f"\n{'='*60}")
    print(f"📈 開始爬取: 股票 {stock_symbol} / 日期 {date}")
    print(f"{'='*60}")
    
    # 清空之前的資料
    collector.clear_data()
    
    # 設定股票代碼
    await set_stock_symbol(page, stock_symbol)
    
    # 設定日期（這會觸發 API 請求）
    await set_target_date(page, date)
    
    # 等待資料收集完成
    await page.wait_for_timeout(3000)
    
    # 取得收集到的資料
    collected = collector.get_collected_data()
    print(f"✅ 完成爬取: 收集到 {len(collected)} 筆資料")
    
    return collected


async def crawl_multiple_stocks(
    page: Page,
    collector: ResponseCollector,
    stock_symbols: List[str],
    dates: List[str]
) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    爬取多支股票在多個日期的資料
    
    Args:
        page: Playwright 頁面物件
        collector: Response 收集器
        stock_symbols: 股票代碼列表
        dates: 日期列表
    
    Returns:
        Dict: 整理後的資料 {date: {symbol: data}}
    """
    all_data = {}
    
    # 迴圈處理每個日期
    for date in dates:
        print(f"\n{'#'*60}")
        print(f"📅 處理日期: {date}")
        print(f"{'#'*60}")
        
        daily_data = {}
        
        # 迴圈處理每支股票
        for symbol in stock_symbols:
            stock_data = await crawl_stock_data_for_date(
                page, collector, symbol, date
            )
            daily_data[symbol] = stock_data
        
        all_data[date] = daily_data
        
        # 儲存當日資料
        save_daily_data(date, daily_data)
    
    return all_data


async def main():
    """
    主程式進入點 - 串接所有功能模組
    """
    print("="*60)
    print("🚀 股票資料爬蟲程式啟動")
    print("="*60)
    
    browser = None
    
    try:
        # 步驟 1: 初始化瀏覽器
        browser, page = await initialize_browser()
        
        # 步驟 2: 建立 Response 收集器
        collector = ResponseCollector()
        await collector.start_monitoring(page)
        
        # 步驟 3: 前往目標網站
        await navigate_to_page(page, CrawlerConfig.BASE_URL)
        
        # 步驟 4: 切換到圖表檢視
        await switch_to_chart_view(page)
        
        # 步驟 5: 產生日期範圍（跳過週末）
        dates = generate_date_range(
            CrawlerConfig.START_DATE,
            CrawlerConfig.END_DATE,
            skip_weekends=True
        )
        
        # 步驟 6: 執行爬蟲作業
        all_data = await crawl_multiple_stocks(
            page,
            collector,
            CrawlerConfig.STOCK_SYMBOLS,
            dates
        )
        
        # 步驟 7: 停止監聽
        collector.stop_monitoring()
        
        print("\n" + "="*60)
        print(f"✅ 爬蟲作業完成！")
        print(f"📊 共處理 {len(dates)} 個日期")
        print(f"📈 共處理 {len(CrawlerConfig.STOCK_SYMBOLS)} 支股票")
        print(f"💾 資料已儲存至 {CrawlerConfig.OUTPUT_DIR} 目錄")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 執行過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 步驟 8: 清理資源
        if browser:
            await close_browser(browser)


# ============================================================================
# 程式進入點
# ============================================================================

if __name__ == "__main__":
    # 執行主程式
    asyncio.run(main())
