#!/usr/bin/env python3
"""简单版发布测试"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def test():
    print("🚀 开始测试")

    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # 加载cookies
        if cookie_file.exists():
            with open(cookie_file) as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print("✅ cookies加载成功")

        # 访问创作者中心
        print("🌐 访问创作者中心...")
        await page.goto("https://creator.xiaohongshu.com")
        await asyncio.sleep(3)

        # 截图
        await page.screenshot(path="/tmp/test_1.png")
        print("📸 截图已保存")

        # 保持打开
        print("⏳ 浏览器保持打开...")
        await asyncio.sleep(600)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test())
