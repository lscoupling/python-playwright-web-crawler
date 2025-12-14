"""日期工具函数"""
from datetime import datetime, timedelta
from typing import Generator


def is_weekend(date: datetime) -> bool:
    """检查是否为周末
    
    Args:
        date: 要检查的日期
        
    Returns:
        True 如果是周末，否则 False
    """
    return date.weekday() >= 5


def generate_date_range(start_date: datetime, end_date: datetime) -> Generator[datetime, None, None]:
    """生成日期范围
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Yields:
        日期对象
    """
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)
