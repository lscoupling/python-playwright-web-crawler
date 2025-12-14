"""CMoney 股票爬虫主程序"""
import asyncio
from playwright.async_api import async_playwright

from src.config import CrawlerSettings
from src.crawlers import CMoneyCrawler


async def main():
    """主程序入口"""
    async with async_playwright() as p:
        # 启动浏览器 (非无头模式)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 创建爬虫实例
        crawler = CMoneyCrawler(page)
        
        # 遍历所有股票
        for name, stock_id in CrawlerSettings.STOCKS.items():
            await crawler.capture_stock(name, stock_id)
        
        # 关闭浏览器
        await browser.close()
        print("\n🔥 所有股票已下載完成 🔥")


if __name__ == "__main__":
    asyncio.run(main())
