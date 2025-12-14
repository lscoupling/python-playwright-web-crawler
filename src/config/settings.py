"""CMoney 股票爬虫配置设置"""
from datetime import datetime
from typing import Dict


class CrawlerSettings:
    """爬虫配置类"""
    
    # 要抓取的股票
    STOCKS: Dict[str, str] = {
        "萬海": "2615",
    }
    
    # 日期范围
    START_DATE = datetime(2025, 11, 1)
    END_DATE = datetime(2025, 11, 28)
    
    # CMoney 相关设置
    BASE_URL = "https://www.cmoney.tw/finance/{stock_id}/f00025"
    API_PATTERN = "stock-chart-service.ashx?action=r&id={stock_id}"
    
    # 选择器
    DATE_INPUT_SELECTOR = 'time#instantTimePicker input[name="utctime"]'
    
    # 数据存储
    DATA_DIR = "./data"
    
    # 浏览器设置
    HEADLESS = False
    TIMEOUT = 60000
    
    # 等待时间 (秒)
    WAIT_AFTER_INPUT = 5
    
    @classmethod
    def get_stock_url(cls, stock_id: str) -> str:
        """获取股票URL"""
        return cls.BASE_URL.format(stock_id=stock_id)
    
    @classmethod
    def get_api_pattern(cls, stock_id: str) -> str:
        """获取API模式"""
        return cls.API_PATTERN.format(stock_id=stock_id)
