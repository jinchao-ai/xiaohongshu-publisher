#!/usr/bin/env python3
"""
小红书发布 - 快速测试版
直接打开发布页面，手动操作
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def main():
    print("\n" + "=" * 60)
    print("🚀 小红书发布测试")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 打开发布页面
        print("\n🌐 打开发布页面...")
        await page.goto("https://creator.xiaohongshu.com/publish")
        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_test_publish.png")

        print("\n" + "=" * 60)
        print("📝 请在浏览器中手动操作：")
        print("   1. 上传图片")
        print("   2. 填写标题和正文")
        print("   3. 添加标签")
        print("   4. 点击发布")
        print("=" * 60)

        print("\n⏳ 浏览器保持打开...")
        await asyncio.sleep(600)  # 10分钟

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
