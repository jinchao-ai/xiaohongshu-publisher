#!/usr/bin/env python3
"""
测试小红书首页登录页面
"""

import asyncio
from playwright.async_api import async_playwright


async def test_homepage_login():
    print("=" * 60)
    print("🧪 测试小红书首页登录页面")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 直接访问首页
        url = "https://www.xiaohongshu.com/explore"
        print(f"\n🌐 访问首页: {url}")

        await page.goto(url, timeout=30000)
        await asyncio.sleep(3)

        print(f"✅ 页面加载成功")
        print(f"📝 当前URL: {page.url}")
        print(f"📝 页面标题: {await page.title()}")

        # 截图
        await page.screenshot(path="/tmp/xhs_explore.png")
        print("📸 截图已保存")

        # 分析页面
        print("\n🔍 分析页面...")

        # 1. 查找登录相关元素
        print("\n🔘 查找登录相关元素:")
        elements_with_text = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                const found = [];
                const keywords = ['登录', '扫码', '二维码', '登录'];

                for (let el of all) {
                    if (el.offsetParent !== null) {
                        const text = el.textContent || '';
                        for (let keyword of keywords) {
                            if (text.includes(keyword) && text.length < 20) {
                                found.push({
                                    tag: el.tagName,
                                    class: el.className.substring(0, 80),
                                    text: text.substring(0, 30)
                                });
                                break;
                            }
                        }
                    }
                }
                return found.slice(0, 15);
            }
        """)

        for el in elements_with_text:
            print(f"  - <{el['tag']}> class='{el['class']}' text='{el['text']}'")

        # 2. 查找图片（二维码）
        print("\n🖼️  查找二维码:")
        images = await page.query_selector_all("img")
        for i, img in enumerate(images[:5]):
            try:
                src = await img.get_attribute("src")
                visible = await img.is_visible()
                if visible and src:
                    print(f"  {i + 1}. src={src[:60]}... visible={visible}")
            except:
                pass

        # 3. 查找按钮
        print("\n🔘 所有按钮:")
        buttons = await page.query_selector_all("button")
        for i, btn in enumerate(buttons[:5]):
            try:
                text = await btn.text_content()
                visible = await btn.is_visible()
                if visible:
                    print(f"  {i + 1}. text='{text}' visible={visible}")
            except:
                pass

        print("\n" + "=" * 60)
        print("💡 测试完成，请查看截图")
        print("=" * 60)

        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_homepage_login())
