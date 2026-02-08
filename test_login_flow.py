#!/usr/bin/env python3
"""
测试改进后的扫码登录流程
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scripts.core.login_handler import LoginHandler
from scripts.core.browser_controller import BrowserController
import yaml


async def test_login_flow():
    print("=" * 60)
    print("🧪 测试扫码登录流程")
    print("=" * 60)

    # 加载配置
    config_path = Path(__file__).parent / "config" / "xiaohongshu.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 初始化浏览器和登录处理器
    browser = BrowserController(config)
    login_handler = LoginHandler(browser, config)

    print("\n🚀 启动浏览器...")
    if not await browser.init():
        print("❌ 浏览器启动失败")
        return

    try:
        # 测试登录流程
        success = await login_handler.login_with_qr()

        if success:
            print("\n" + "=" * 60)
            print("✅ 登录成功！")
            print("=" * 60)

            # 保存cookies
            await login_handler.save_browser_cookies()
            print("💾 Cookies已保存")

        else:
            print("\n❌ 登录失败")

    finally:
        print("\n⏳ 浏览器保持打开...")
        print("   请查看浏览器窗口")
        print("   按 Ctrl+C 退出")

        try:
            await asyncio.sleep(300)  # 保持5分钟
        except KeyboardInterrupt:
            print("\n👋 用户退出")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_login_flow())
