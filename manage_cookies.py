#!/usr/bin/env python3
"""
小红书Cookie管理工具
用于查看、清除保存的cookies
"""

import json
from pathlib import Path


def show_cookies():
    """显示保存的cookies"""
    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"

    if not cookie_file.exists():
        print("❌ 没有找到保存的cookies")
        return

    try:
        with open(cookie_file, "r", encoding="utf-8") as f:
            cookies = json.load(f)

        print(f"\n📂 保存的cookies: {cookie_file}")
        print(f"数量: {len(cookies)} 个\n")

        # 显示主要cookie名称
        print("主要Cookies:")
        important = ["web_session", "token", "user_id", "xhs_token_id", "a1"]
        for cookie in cookies:
            name = cookie.get("name", "")
            value = cookie.get("value", "")
            domain = cookie.get("domain", "")

            is_important = any(imp.lower() in name.lower() for imp in important)
            prefix = "⭐" if is_important else "  "

            # 显示部分value，避免太长
            display_value = value[:20] + "..." if len(value) > 20 else value

            print(f"  {prefix} {name}: {display_value}")
            print(f"      域名: {domain}")

    except Exception as e:
        print(f"❌ 读取cookies失败: {e}")


def clear_cookies():
    """清除保存的cookies"""
    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"

    if cookie_file.exists():
        cookie_file.unlink()
        print("✅ 已清除保存的cookies")
    else:
        print("⚠️  没有找到保存的cookies")


def check_cookies_valid():
    """检查cookies是否有效"""
    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"

    if not cookie_file.exists():
        print("❌ 没有保存的cookies")
        return False

    try:
        with open(cookie_file, "r", encoding="utf-8") as f:
            cookies = json.load(f)

        # 检查是否有登录态cookie
        login_cookies = ["web_session", "token", "user_id", "xhs_token_id"]
        cookie_names = [c.get("name", "") for c in cookies]

        has_valid = False
        for login_cookie in login_cookies:
            if any(login_cookie.lower() in name.lower() for name in cookie_names):
                has_valid = True
                break

        if has_valid:
            print("✅ Cookies看起来有效")
            return True
        else:
            print("⚠️  Cookies可能已失效（没有找到登录态cookie）")
            return False

    except Exception as e:
        print(f"❌ 检查cookies失败: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="小红书Cookie管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python manage_cookies.py           # 显示cookies信息
  python manage_cookies.py --show   # 显示cookies
  python manage_cookies.py --check  # 检查cookies有效性
  python manage_cookies.py --clear # 清除cookies
        """,
    )

    parser.add_argument("--show", action="store_true", help="显示保存的cookies")
    parser.add_argument("--check", action="store_true", help="检查cookies是否有效")
    parser.add_argument("--clear", action="store_true", help="清除保存的cookies")

    args = parser.parse_args()

    # 如果没有指定参数，默认显示
    if not any([args.show, args.check, args.clear]):
        args.show = True

    if args.show:
        show_cookies()

    if args.check:
        check_cookies_valid()

    if args.clear:
        confirm = input("确定要清除保存的cookies吗? (y/n): ").strip().lower()
        if confirm == "y":
            clear_cookies()
        else:
            print("已取消")


if __name__ == "__main__":
    main()
