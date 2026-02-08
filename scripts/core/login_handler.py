"""
扫码登录处理器 - 自动检测登录状态并处理扫码登录流程
支持Cookie持久化，避免每次都扫码
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)


class LoginHandler:
    """处理小红书扫码登录"""

    def __init__(self, browser_controller, config: dict):
        self.browser = browser_controller
        self.config = config
        self.qr_code_path = Path("/tmp/xhs_qr_code.png")

        # Cookie持久化配置
        self.cookie_dir = Path.home() / ".xiaohongshu_publisher"
        self.cookie_dir.mkdir(exist_ok=True)
        self.cookie_file = self.cookie_dir / "cookies.json"

        self.root = None
        self.qr_label = None

    # ==================== Cookie持久化方法 ====================

    def get_cookies(self) -> list:
        """获取保存的cookies"""
        try:
            if self.cookie_file.exists():
                with open(self.cookie_file, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
                    logger.info(f"✅ 找到保存的cookies，共 {len(cookies)} 个")
                    return cookies
        except Exception as e:
            logger.warning(f"⚠️  读取cookies失败: {e}")
        return []

    def save_cookies(self, cookies: list):
        """保存cookies到本地"""
        try:
            # 过滤无效cookie
            valid_cookies = []
            for cookie in cookies:
                if cookie.get("name") and cookie.get("value"):
                    # 移除不需要的字段
                    clean_cookie = {
                        "name": cookie["name"],
                        "value": cookie["value"],
                        "domain": cookie.get("domain", ".xiaohongshu.com"),
                        "path": cookie.get("path", "/"),
                        "secure": cookie.get("secure", False),
                        "httpOnly": cookie.get("httpOnly", True),
                    }
                    # 处理expires字段
                    if cookie.get("expires"):
                        clean_cookie["expires"] = cookie["expires"]
                    valid_cookies.append(clean_cookie)

            if valid_cookies:
                self.cookie_dir.mkdir(parents=True, exist_ok=True)
                with open(self.cookie_file, "w", encoding="utf-8") as f:
                    json.dump(valid_cookies, f, indent=2, ensure_ascii=False)
                logger.info(
                    f"✅ 已保存 {len(valid_cookies)} 个cookies到: {self.cookie_file}"
                )
            return True
        except Exception as e:
            logger.error(f"❌ 保存cookies失败: {e}")
            return False

    def clear_cookies(self):
        """清除保存的cookies"""
        try:
            if self.cookie_file.exists():
                self.cookie_file.unlink()
                logger.info("🗑️  已清除保存的cookies")
        except Exception as e:
            logger.warning(f"⚠️  清除cookies失败: {e}")

    async def load_cookies_to_browser(self) -> bool:
        """将保存的cookies加载到浏览器"""
        cookies = self.get_cookies()
        if not cookies:
            logger.info("⚠️  没有找到保存的cookies")
            return False

        try:
            # 添加cookies到浏览器上下文
            await self.browser.context.add_cookies(cookies)
            logger.info("✅ 已加载cookies到浏览器")
            return True
        except Exception as e:
            logger.error(f"❌ 加载cookies失败: {e}")
            return False

    async def save_browser_cookies(self):
        """从浏览器保存cookies"""
        try:
            cookies = await self.browser.context.cookies()
            if cookies:
                self.save_cookies(cookies)
        except Exception as e:
            logger.warning(f"⚠️  保存浏览器cookies失败: {e}")

    def is_cookies_valid(self) -> bool:
        """检查保存的cookies是否有效"""
        cookies = self.get_cookies()
        if not cookies:
            return False

        # 检查是否有常用的登录态cookie
        login_cookies = ["web_session", "token", "user_id", "xhs_token_id"]
        cookie_names = [c.get("name", "") for c in cookies]

        for login_cookie in login_cookies:
            if any(login_cookie.lower() in name.lower() for name in cookie_names):
                return True

        return False

    # ==================== 登录状态检查 ====================

    async def check_login_status(self) -> bool:
        """检查是否已登录"""
        logger.info("🔍 检查登录状态...")
        try:
            # 访问创作平台首页
            await self.browser.navigate(self.config["platform"]["creator_url"])
            await asyncio.sleep(2)

            # 检查登录成功指示器
            login_success_selectors = [
                self.config["selectors"]["login_success_indicator"],
                ".user-avatar",
                ".user-name",
                '[class*="user-info"]',
                ".header-user",
            ]

            for selector in login_success_selectors:
                element = await self.browser.find_element(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        logger.info("✅ 已登录状态")
                        return True

            logger.info("⚠️  未登录状态")
            return False

        except Exception as e:
            logger.error(f"❌ 检查登录状态失败: {e}")
            return False

    async def login_with_qr(self) -> bool:
        """执行扫码登录流程"""
        print("\n" + "=" * 50)
        print("🔐 启动扫码登录流程")
        print("=" * 50)

        try:
            # 1. 点击登录按钮
            print("👆 第一步：点击登录按钮...")
            login_btn_selectors = [
                ".beer-login-btn",
                ".login-btn",
                'button:has-text("登 录")',
                '[class*="login-btn"]',
                ".css-1jgt0wa",
            ]

            login_success = False
            for selector in login_btn_selectors:
                element = await self.browser.find_element(selector)
                if element and await element.is_visible():
                    await element.click()
                    print(f"✅ 已点击登录按钮: {selector}")
                    login_success = True
                    await asyncio.sleep(3)
                    break

            if not login_success:
                print("❌ 未找到登录按钮")
                return False

            # 截图确认
            await self.browser.screenshot(path="/tmp/xhs_clicked_login.png")
            print("📸 已截图确认登录按钮点击")

            # 2. 等待登录对话框出现
            print("⏳ 第二步：等待登录对话框...")
            await asyncio.sleep(2)

            # 3. 点击下拉框选择登录方式
            print("👆 第三步：点击登录方式下拉框...")
            dropdown_clicked = await self.click_login_type_dropdown()

            if not dropdown_clicked:
                # 如果找不到下拉框，尝试截图分析
                await self.browser.screenshot(path="/tmp/xhs_dialog.png")
                print("⚠️  未找到下拉框，已截图请查看")
                print("💡 请在浏览器中手动选择扫码登录")

            # 4. 选择扫码登录
            print("👆 第四步：选择扫码登录...")
            qr_selected = await self.select_qr_login()

            if not qr_selected:
                print("⚠️  自动选择扫码登录失败")
                print("💡 请在浏览器中手动选择扫码登录")
                await self.browser.screenshot(path="/tmp/xhs_select_type.png")
                # 等待用户手动选择
                print("\n⏳ 请在浏览器中选择扫码登录，选择好后按Enter继续...")
                input()

            # 5. 等待二维码出现
            print("⏳ 第五步：等待二维码出现...")
            await asyncio.sleep(2)

            # 6. 获取并显示二维码
            print("📱 第六步：获取二维码...")
            qr_success = await self.capture_and_display_qr()

            if not qr_success:
                print("❌ 获取二维码失败")
                await self.browser.screenshot(path="/tmp/xhs_no_qr.png")
                print("💡 请查看截图，确认页面状态")

            # 7. 等待用户扫码
            print("\n⏳ 请使用小红书APP扫码登录...")
            print("⏱️  二维码有效期为2分钟，请尽快扫码")
            print("-" * 50)

            # 8. 轮询检测登录状态
            login_success = await self.wait_for_login(timeout=120)

            if login_success:
                print("\n" + "=" * 50)
                print("✅ 登录成功！欢迎回来~")
                print("=" * 50 + "\n")
                return True
            else:
                print("\n❌ 登录超时，请重新尝试")
                return False

        except Exception as e:
            logger.error(f"❌ 扫码登录失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def click_login_type_dropdown(self) -> bool:
        """点击登录方式下拉框"""
        try:
            print("   查找登录方式下拉框...")

            # 查找包含"请选择选项"的元素（这是下拉框）
            dropdown_selectors = [
                'input[placeholder="请选择选项"]',
                '.el-select:has-text("请选择选项")',
                '[class*="login-type"] input',
                '.login-type-select input',
            ]

            for selector in dropdown_selectors:
                element = await self.browser.find_element(selector)
                if element and await element.is_visible():
                    print(f"   ✅ 找到下拉框: {selector}")
                    await element.click()
                    await asyncio.sleep(1)
                    return True

            # 如果找不到，尝试查找下拉框容器
            print("   🔍 尝试查找下拉框容器...")
            containers = await self.browser.page.evaluate("""
                () => {
                    const all = document.querySelectorAll('*');
                    const found = [];
                    for (let el of all) {
                        if (el.textContent && el.textContent.includes('请选择选项') && el.offsetParent !== null) {
                            found.push({
                                tag: el.tagName,
                                class: el.className,
                                text: el.textContent.substring(0, 100)
                            });
                        }
                    }
                    return found.slice(0, 5);
                }
            """)

            if containers:
                print(f"   📍 找到包含'请选择选项'的元素:")
                for item in containers:
                    print(f"      <{item['tag']}> class='{item['class']}'")

                # 点击找到的元素
                if containers[0]:
                    tag = containers[0]['tag'].lower()
                    if tag == 'div' or tag == 'span':
                        js_click = f"""
                            () => {{
                                const elements = document.querySelectorAll('{tag}');
                                for (let el of elements) {{
                                    if (el.textContent && el.textContent.includes('请选择选项')) {{
                                        el.click();
                                        return true;
                                    }}
                                }}
                                return false;
                            }}
                        """
                        clicked = await self.browser.page.evaluate(js_click)
                        if clicked:
                            print("   ✅ 已点击下拉框")
                            await asyncio.sleep(1)
                            return True

            print("   ⚠️  未找到下拉框")
            return False

        except Exception as e:
            logger.error(f"❌ 点击下拉框失败: {e}")
            return False

    async def select_qr_login(self) -> bool:
        """选择扫码登录选项"""
        try:
            print("   查找扫码登录选项...")

            # 等待下拉选项出现
            await asyncio.sleep(1)

            # 查找包含"扫码登录"的选项
            qr_selectors = [
                'li:has-text("扫码登录")',
                '[class*="qrcode"]',
                '.login-type-qrcode',
                'text=扫码登录',
            ]

            for selector in qr_selectors:
                element = await self.browser.find_element(selector)
                if element and await element.is_visible():
                    print(f"   ✅ 找到扫码登录选项: {selector}")
                    await element.click()
                    await asyncio.sleep(2)
                    print("   ✅ 已选择扫码登录")
                    return True

            # 如果找不到，尝试JavaScript查找
            print("   🔍 尝试JavaScript查找...")
            options = await self.browser.page.evaluate("""
                () => {
                    const all = document.querySelectorAll('li, div, span');
                    const found = [];
                    for (let el of all) {
                        if (el.textContent && el.textContent.includes('扫码登录') && el.offsetParent !== null) {
                            found.push({
                                tag: el.tagName,
                                class: el.className,
                                text: el.textContent.substring(0, 50)
                            });
                        }
                    }
                    return found.slice(0, 5);
                }
            """)

            if options:
                print(f"   📍 找到扫码登录选项:")
                for item in options:
                    print(f"      <{item['tag']}> class='{item['class']}' text='{item['text']}'")

                # 点击找到的元素
                if options[0]:
                    tag = options[0]['tag'].lower()
                    js_click = f"""
                        () => {{
                            const elements = document.querySelectorAll('{tag}');
                            for (let el of elements) {{
                                if (el.textContent && el.textContent.includes('扫码登录')) {{
                                    el.click();
                                    return true;
                                }}
                            }}
                            return false;
                        }}
                    """
                    clicked = await self.browser.page.evaluate(js_click)
                    if clicked:
                        print("   ✅ 已点击扫码登录")
                        await asyncio.sleep(2)
                        return True

            print("   ⚠️  未找到扫码登录选项")
            return False

        except Exception as e:
            logger.error(f"❌ 选择扫码登录失败: {e}")
            return False

    async def switch_to_qr_mode(self) -> bool:
        """切换到扫码登录模式（兼容旧版本）"""
        # 新版本已经在login_with_qr中实现了
        return await self.select_qr_login()
            else:
                print("\n❌ 登录超时，请重新尝试")
                return False

        except Exception as e:
            logger.error(f"❌ 扫码登录失败: {e}")
            return False

    async def switch_to_qr_mode(self) -> bool:
        """切换到扫码登录模式"""
        print("📱 尝试切换到扫码登录模式...")
        try:
            # 先点击"请选择选项"下拉框
            dropdown_selectors = [
                '.el-select:has-text("请选择选项")',
                '[class*="login-type"]',
                ".login-type-selector",
                ".css-1ic7y4p",  # 下拉框常见class
            ]

            for selector in dropdown_selectors:
                element = await self.browser.find_element(selector)
                if element and await element.is_visible():
                    print(f"👆 点击登录方式下拉框: {selector}")
                    await element.click()
                    await asyncio.sleep(1)
                    break

            # 选择扫码登录选项
            qr_option_selectors = [
                'li:has-text("扫码登录")',
                '[class*="qrcode"]',
                ".login-type-qrcode",
                ".css-qrcode-option",
                'xpath=//li[contains(text(),"扫码")]',
            ]

            for selector in qr_option_selectors:
                element = await self.browser.find_element(selector)
                if element and await element.is_visible():
                    print(f"👆 选择扫码登录选项: {selector}")
                    await element.click()
                    await asyncio.sleep(2)
                    print("✅ 已切换到扫码登录模式")
                    return True

            # 如果找不到切换选项，可能已经是扫码模式
            print("ℹ️  已在扫码登录模式或无法找到切换选项")
            return True

        except Exception as e:
            logger.warning(f"⚠️  切换到扫码模式时出错: {e}")
            return True

    async def capture_and_display_qr(self) -> bool:
        """捕获并显示二维码"""
        try:
            # 尝试多种方式获取二维码
            qr_selectors = [
                self.config["selectors"]["qr_code_img"],
                ".qrcode-img img",
                '[class*="qrcode"] img',
                ".login-qrcode img",
                'img[alt*="qrcode"]',
            ]

            qr_element = None
            for selector in qr_selectors:
                element = await self.browser.find_element(selector)
                if element and await element.is_visible():
                    qr_element = element
                    break

            if qr_element:
                # 保存二维码
                await qr_element.screenshot(path=str(self.qr_code_path))
                print(f"📸 二维码已保存: {self.qr_code_path}")

                # 显示二维码窗口
                self.show_qr_window(str(self.qr_code_path))
                return True

            print("❌ 未找到二维码元素")
            return False

        except Exception as e:
            logger.error(f"❌ 捕获二维码失败: {e}")
            return False

    def show_qr_window(self, image_path: str):
        """显示二维码窗口"""
        try:
            # 创建窗口
            self.root = tk.Tk()
            self.root.title("📱 小红书扫码登录")
            self.root.geometry("350x420")
            self.root.resizable(False, False)

            # 居中显示
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - 350) // 2
            y = (screen_height - 420) // 2
            self.root.geometry(f"350x420+{x}+{y}")

            # 标题
            title_label = tk.Label(
                self.root,
                text="请使用小红书APP扫码登录",
                font=("Microsoft YaHei", 14, "bold"),
                pady=15,
            )
            title_label.pack()

            # 加载并显示图片
            img = Image.open(image_path)
            img = img.resize((280, 280), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            self.qr_label = tk.Label(
                self.root, image=photo, borderwidth=2, relief="solid"
            )
            self.qr_label.image = photo
            self.qr_label.pack(pady=10)

            # 提示文字
            tip_label = tk.Label(
                self.root,
                text="打开小红书 > 我的 > 右上角扫码",
                font=("Microsoft YaHei", 11),
                fg="#666666",
                pady=10,
            )
            tip_label.pack()

            # 状态标签
            self.status_label = tk.Label(
                self.root,
                text="等待扫码...",
                font=("Microsoft YaHei", 10),
                fg="#1890FF",
                pady=5,
            )
            self.status_label.pack()

            # 在新线程中运行Tkinter主循环
            def run_mainloop():
                self.root.mainloop()

            import threading

            threading.Thread(target=run_mainloop, daemon=True).start()

        except Exception as e:
            logger.error(f"❌ 显示二维码窗口失败: {e}")

    def update_qr_status(self, status: str, color: str = "#1890FF"):
        """更新二维码状态"""
        if self.root and self.status_label:
            self.status_label.config(text=status, fg=color)
            self.root.update()

    def close_qr_window(self):
        """关闭二维码窗口"""
        if self.root:
            try:
                self.root.destroy()
                self.root = None
            except:
                pass

    async def wait_for_login(self, timeout: int = 120) -> bool:
        """等待登录成功"""
        check_interval = 3  # 每3秒检查一次
        elapsed = 0

        while elapsed < timeout:
            try:
                # 检查是否有登录成功的元素
                success_selectors = [
                    ".user-avatar",
                    ".user-name",
                    '[class*="user-info"]',
                    ".header-user",
                    ".user-avatar img",
                ]

                for selector in success_selectors:
                    element = await self.browser.find_element(selector)
                    if element and await element.is_visible():
                        self.update_qr_status("✅ 登录成功！", "#52C41A")
                        self.close_qr_window()
                        return True

                # 检查是否有错误提示
                error_selectors = [".qrcode-error", '[class*="error"]']

                for selector in error_selectors:
                    element = await self.browser.find_element(selector)
                    if element and await element.is_visible():
                        error_text = await element.text_content()
                        if error_text:
                            print(f"⚠️  二维码状态: {error_text}")

                # 更新等待状态
                remaining = timeout - elapsed
                if remaining % 10 == 0 and remaining > 0:
                    print(f"⏳ 等待扫码... ({remaining}秒后超时)")

                self.update_qr_status(f"等待扫码... {remaining}秒")

                await asyncio.sleep(check_interval)
                elapsed += check_interval

            except Exception as e:
                logger.warning(f"⚠️  检查登录状态时出错: {e}")
                await asyncio.sleep(check_interval)
                elapsed += check_interval

        # 超时
        self.update_qr_status("❌ 二维码已过期", "#FF4D4F")
        return False

    async def handle_login(self) -> bool:
        """处理登录流程（优先Cookie + 扫码登录）"""
        print("\n" + "=" * 50)
        print("🔐 开始登录流程")
        print("=" * 50)

        # 方法1: 尝试使用保存的Cookie登录
        if self.is_cookies_valid():
            print("\n📂 尝试使用保存的Cookie登录...")
            await self.load_cookies_to_browser()
            await self.browser.navigate(self.config["platform"]["creator_url"])
            await asyncio.sleep(2)

            if await self.check_login_status():
                print("✅ Cookie登录成功！欢迎回来~")
                return True
            else:
                print("⚠️  Cookie已过期，需要重新登录")

        # 方法2: 扫码登录
        login_success = await self.login_with_qr()

        if login_success:
            # 登录成功后保存cookies
            print("💾 正在保存登录状态...")
            await self.save_browser_cookies()
            print("✅ 登录状态已保存，下次无需扫码")

        return login_success
