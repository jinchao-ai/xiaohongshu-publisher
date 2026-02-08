#!/usr/bin/env python3
"""
Xiaohongshu Login - QR Code Login
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def login():
    print("🚀 Xiaohongshu QR Login")
    print("=" * 50)
    print("Please scan the QR code with Xiaohongshu app")
    print("=" * 50)

    cookie_dir = Path.home() / ".xiaohongshu_publisher"
    cookie_dir.mkdir(parents=True, exist_ok=True)
    cookie_file = cookie_dir / "cookies.json"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # Go to login page
        print("\n🌐 Opening login page...")
        await page.goto("https://creator.xiaohongshu.com/login")
        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_login_1.png")

        # Check for QR code
        print("\n🔍 Looking for QR code...")
        qr_found = await page.evaluate("""
            () => {
                const iframes = document.querySelectorAll('iframe');
                for (const iframe of iframes) {
                    if (iframe.src.includes('qr')) {
                        return 'QR iframe found';
                    }
                }
                // Look for QR code image or canvas
                const qr = document.querySelector('[class*="qr"], canvas, img[src*="qr"]');
                if (qr) return 'QR element found';
                return 'QR not visible';
            }
        """)
        print(f"   {qr_found}")
        await page.screenshot(path="/tmp/xhs_login_2.png")

        # Wait for login
        print("\n⏳ Waiting for QR scan (60 seconds)...")
        try:
            await page.wait_for_url(
                "**/creator.xiaohongshu.com/new/home**", timeout=60000
            )
            print("✅ Login successful!")
        except Exception as e:
            print(f"⚠️  Timeout waiting for login: {e}")
            print("   Please scan QR code manually...")
            # Wait longer for manual scan
            await asyncio.sleep(120)

        # Check current URL
        print(f"\n📄 Current URL: {page.url}")

        if "creator.xiaohongshu.com" in page.url:
            # Save cookies
            cookies = await context.cookies()
            with open(cookie_file, "w") as f:
                json.dump(cookies, f, indent=2)
            print(f"✅ Cookies saved to: {cookie_file}")
            print(f"   Cookie count: {len(cookies)}")

        await page.screenshot(path="/tmp/xhs_login_3.png")

        print("\n" + "=" * 50)
        print("✅ Login complete!")
        print("=" * 50)

        await asyncio.sleep(10)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(login())
