#!/usr/bin/env python3
"""
检查正确的发布页面URL
"""

import asyncio
from playwright.async_api import async_playwright


async def check_publish_url():
    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # 加载cookies
        import json

        if cookie_file.exists():
            with open(cookie_file, "r") as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)

        # 访问创作者中心首页
        print("\n🌐 访问创作者中心...")
        await page.goto("https://creator.xiaohongshu.com")
        await asyncio.sleep(3)

        # 查找发布按钮
        print("\n🔍 查找发布相关元素...")
        elements = await page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                const found = [];
                for (let el of elements) {
                    if (el.offsetParent !== null) {
                        const text = el.textContent || '';
                        if (text.includes('发布') || text.includes('笔记') || text.includes('创作')) {
                            found.push({
                                tag: el.tagName,
                                text: text.substring(0, 30),
                                href: el.href || 'no href'
                            });
                        }
                    }
                }
                return found.slice(0, 10);
            }
        """)

        print(f"\n找到 {len(elements)} 个发布相关元素:")
        for el in elements:
            print(f"  - <{el['tag']}> {el['text']} (href: {el['href']})")

        # 保存截图
        await page.screenshot(path="/tmp/creator_home.png")

        print("\n💡 截图已保存，请查看页面结构")

        await asyncio.sleep(60)
        await browser.close()


from pathlib import Path

if __name__ == "__main__":
    asyncio.run(check_publish_url())
