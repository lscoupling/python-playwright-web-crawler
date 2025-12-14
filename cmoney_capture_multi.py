# cmoney_capture_multi.py
import asyncio, re, json, calendar, os
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# === 要抓的股票 ===
STOCKS = {
   
    "萬海": "2615",

}


SEL = 'time#instantTimePicker input[name="utctime"]'
START_DATE = datetime(2025, 11, 1)
END_DATE   = datetime(2025, 11, 28)

async def capture_stock(page, name, sid):
    URL = f"https://www.cmoney.tw/finance/{sid}/f00025"
    TARGET = f"stock-chart-service.ashx?action=r&id={sid}"

    save_dir = f"./data_{name}_{sid}"
    os.makedirs(save_dir, exist_ok=True)

    daily_content = {}

    print(f"\n========== 開始抓 {name}({sid}) ==========")
    print(f"🌐 開啟 Cmoney 網頁: {URL}")
    await page.goto(URL, wait_until="domcontentloaded", timeout=60000)

    # 必須先切換到日期
    await page.click("a[chartswitch='1']")
    print("📅 已切換到日期")

    # 再切換回即時走勢避免資料異常
    await page.click("a[title='即時走勢']")
    print("📊 已切換到即時走勢")

    await page.wait_for_selector(SEL, timeout=20000)
    print("✅ 日期輸入框已出現")

    async def handle_response(response):
        url = response.url
        if TARGET in url and "date=" in url:
            match = re.search(r"date=(\d{8})", url)
            if match:
                date_str = match.group(1)
                text = await response.text()
                daily_content[date_str] = text
                print(f"📡 收到 {date_str} 回應")

    page.on("response", handle_response)

    current = START_DATE

    while current <= END_DATE:
        if current.weekday() >= 5:
            print(f"⏭️ 跳過週末 {current.strftime('%Y-%m-%d')}")
            current += timedelta(days=1)
            continue

        date_str = current.strftime("%Y-%m-%d")
        date_key = current.strftime("%Y%m%d")
        print(f"\n📅 抓取日期: {date_str}")

        await page.dblclick(SEL)
        await page.keyboard.press("Delete")
        await page.fill(SEL, date_str)
        await page.press(SEL, "Enter")
        await page.evaluate(f"""
            const el = document.querySelector('{SEL}');
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
        """)

        await asyncio.sleep(5)

        if date_key in daily_content:
            filename = f"{save_dir}/{sid}_{date_key}.json"
            content  = daily_content[date_key]
            try:
                parsed = json.loads(content)
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, ensure_ascii=False, indent=2)
            except Exception:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
            print(f"💾 {filename} 已儲存")
        else:
            print(f"⚠️ {date_str} 沒有收到任何回應")

        current += timedelta(days=1)

    print(f"🎯 {name}({sid}) 完成！")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        for name, sid in STOCKS.items():
            await capture_stock(page, name, sid)

        await browser.close()
        print("\n🔥 所有股票已下載完成 🔥")

asyncio.run(main())
