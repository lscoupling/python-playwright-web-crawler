"""CMoney 股票爬虫核心类"""
import asyncio
import json
import os
import re
from datetime import datetime
from typing import Dict

from playwright.async_api import Page, Response

from ..config import CrawlerSettings
from ..utils import is_weekend, generate_date_range


class CMoneyCrawler:
    """CMoney 股票数据爬虫"""
    
    def __init__(self, page: Page, settings: CrawlerSettings = None):
        """初始化爬虫
        
        Args:
            page: Playwright 页面对象
            settings: 配置对象，默认使用 CrawlerSettings
        """
        self.page = page
        self.settings = settings or CrawlerSettings()
        self.daily_content: Dict[str, str] = {}
        
    async def capture_stock(self, name: str, stock_id: str):
        """抓取单个股票数据
        
        Args:
            name: 股票名称
            stock_id: 股票代码
        """
        url = self.settings.get_stock_url(stock_id)
        api_pattern = self.settings.get_api_pattern(stock_id)
        
        # 创建保存目录
        save_dir = f"{self.settings.DATA_DIR}_{name}_{stock_id}"
        os.makedirs(save_dir, exist_ok=True)
        
        self.daily_content.clear()
        
        print(f"\n========== 開始抓 {name}({stock_id}) ==========")
        print(f"🌐 開啟 Cmoney 網頁: {url}")
        
        await self.page.goto(
            url, 
            wait_until="domcontentloaded", 
            timeout=self.settings.TIMEOUT
        )
        
        # 切换到日期视图
        await self._switch_to_date_view()
        
        # 切换回即时走势
        await self._switch_to_realtime_view()
        
        # 等待日期输入框出现
        await self.page.wait_for_selector(
            self.settings.DATE_INPUT_SELECTOR, 
            timeout=20000
        )
        print("✅ 日期輸入框已出現")
        
        # 设置响应监听
        self.page.on("response", lambda response: asyncio.create_task(
            self._handle_response(response, api_pattern)
        ))
        
        # 遍历日期范围
        for date in generate_date_range(self.settings.START_DATE, self.settings.END_DATE):
            if is_weekend(date):
                print(f"⏭️ 跳過週末 {date.strftime('%Y-%m-%d')}")
                continue
                
            await self._process_date(date, stock_id, save_dir)
        
        print(f"🎯 {name}({stock_id}) 完成！")
    
    async def _switch_to_date_view(self):
        """切换到日期视图"""
        await self.page.click("a[chartswitch='1']")
        print("📅 已切換到日期")
    
    async def _switch_to_realtime_view(self):
        """切换到即时走势"""
        await self.page.click("a[title='即時走勢']")
        print("📊 已切換到即時走勢")
    
    async def _handle_response(self, response: Response, api_pattern: str):
        """处理网络响应
        
        Args:
            response: 响应对象
            api_pattern: API 匹配模式
        """
        url = response.url
        if api_pattern in url and "date=" in url:
            match = re.search(r"date=(\d{8})", url)
            if match:
                date_str = match.group(1)
                text = await response.text()
                self.daily_content[date_str] = text
                print(f"📡 收到 {date_str} 回應")
    
    async def _process_date(self, date: datetime, stock_id: str, save_dir: str):
        """处理单个日期
        
        Args:
            date: 日期对象
            stock_id: 股票代码
            save_dir: 保存目录
        """
        date_str = date.strftime("%Y-%m-%d")
        date_key = date.strftime("%Y%m%d")
        print(f"\n📅 抓取日期: {date_str}")
        
        # 输入日期
        await self._input_date(date_str)
        
        # 等待响应
        await asyncio.sleep(self.settings.WAIT_AFTER_INPUT)
        
        # 保存数据
        if date_key in self.daily_content:
            self._save_data(stock_id, date_key, save_dir)
        else:
            print(f"⚠️ {date_str} 沒有收到任何回應")
    
    async def _input_date(self, date_str: str):
        """输入日期
        
        Args:
            date_str: 日期字符串 (格式: YYYY-MM-DD)
        """
        selector = self.settings.DATE_INPUT_SELECTOR
        
        await self.page.dblclick(selector)
        await self.page.keyboard.press("Delete")
        await self.page.fill(selector, date_str)
        await self.page.press(selector, "Enter")
        
        # 触发事件
        await self.page.evaluate(f"""
            const el = document.querySelector('{selector}');
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
        """)
    
    def _save_data(self, stock_id: str, date_key: str, save_dir: str):
        """保存数据到文件
        
        Args:
            stock_id: 股票代码
            date_key: 日期键 (格式: YYYYMMDD)
            save_dir: 保存目录
        """
        filename = f"{save_dir}/{stock_id}_{date_key}.json"
        content = self.daily_content[date_key]
        
        try:
            parsed = json.loads(content)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)
        except Exception:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
        
        print(f"💾 {filename} 已儲存")
