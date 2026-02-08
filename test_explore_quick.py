#!/usr/bin/env python3
"""
测试小红书首页 - 找到登录方式
"""

import asyncio
from playwright.async_api import async_playwright


async def test():
    print("=" * 60)
    print("🧪 测试小红书首页")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("\n🌐 访问首页...")
        await page.goto("https://www.xiaohongshu.com/explore")
        await asyncio.sleep(3)

        await page.screenshot(path="/tmp/xhs_explore.png")
        print("📸 截图已保存")

        # 查找包含特定文本的元素
        print("\n🔍 查找登录相关元素...")
        elements = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                const found = [];
                const keywords = ['登录', '扫码', '我的'];

                for (let el of all) {
                    if (el.offsetParent !== null) {
                        const text = el.textContent || '';
                        for (let keyword of keywords) {
                            if (text.includes(keyword) && text.length < 15) {
                                found.push({
                                    tag: el.tagName,
                                    class: el.className.substring(0, 60),
                                    text: text.substring(0, 20)
                                });
                                break;
                            }
                        }
                    }
                }
                return [...new Set(found.map(JSON.stringify))].map(JSON.parse).slice(0, 20);
            }
        """)

        print(f"\n找到 {len(elements)} 个相关元素:")
        for el in elements:
            print(f"  <{el['tag']}> class='{el['class']}' text='{el['text']}'")

        print("\n" + "=" * 60)
        print("💡 请查看截图确认页面结构")
        print("=" * 60)

        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test())
