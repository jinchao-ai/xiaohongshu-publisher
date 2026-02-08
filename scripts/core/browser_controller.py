"""
浏览器控制器 - 基于 Playwright 实现浏览器自动化
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import logging

logger = logging.getLogger(__name__)


class BrowserController:
    """浏览器控制器，管理浏览器生命周期和基本操作"""

    def __init__(self, config: dict):
        self.config = config
        self.playwright: Browser = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.current_step = ""

    async def init(self) -> bool:
        """初始化浏览器"""
        try:
            logger.info("🚀 正在启动浏览器...")
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # 强制非无头模式，用户可见
                args=[
                    "--window-size=1440,900",
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled",
                ],
            )
            self.context = await self.browser.new_context(
                viewport={"width": 1440, "height": 900},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            )
            self.page = await self.context.new_page()

            # 防止被检测为自动化
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)

            logger.info("✅ 浏览器启动成功")
            return True

        except Exception as e:
            logger.error(f"❌ 浏览器启动失败: {e}")
            return False

    async def navigate(self, url: str, wait_until: str = "networkidle") -> bool:
        """导航到指定页面"""
        try:
            self.current_step = f"访问页面: {url}"
            logger.info(f"🌐 {self.current_step}")
            await self.page.goto(
                url, wait_until=wait_until, timeout=self.config["timeouts"]["page_load"]
            )
            await self.random_delay(1, 2)
            return True
        except Exception as e:
            logger.error(f"❌ 页面导航失败: {e}")
            return False

    async def find_element(self, selector: str, timeout: int = None) -> Page:
        """查找元素"""
        if timeout is None:
            timeout = self.config["timeouts"]["element_wait"]

        try:
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            return element
        except Exception as e:
            logger.warning(f"⚠️  未找到元素: {selector}, 错误: {e}")
            return None

    async def find_elements(self, selector: str) -> list:
        """查找多个元素"""
        try:
            elements = await self.page.query_selector_all(selector)
            return elements
        except Exception as e:
            logger.warning(f"⚠️  查找元素失败: {selector}, 错误: {e}")
            return []

    async def click(self, selector: str, timeout: int = None) -> bool:
        """点击元素"""
        element = await self.find_element(selector, timeout)
        if element:
            try:
                self.current_step = f"点击: {selector}"
                logger.info(f"👆 {self.current_step}")
                await element.click()
                await self.random_delay(0.5, 1)
                return True
            except Exception as e:
                logger.error(f"❌ 点击失败: {selector}, 错误: {e}")
        return False

    async def fill(self, selector: str, text: str, timeout: int = None) -> bool:
        """填写表单"""
        element = await self.find_element(selector, timeout)
        if element:
            try:
                self.current_step = f"填写: {selector}"
                logger.info(f"📝 {self.current_step}")
                await element.fill(text)
                await self.random_delay(0.3, 0.5)
                return True
            except Exception as e:
                logger.error(f"❌ 填写失败: {selector}, 错误: {e}")
        return False

    async def type_text(self, selector: str, text: str, delay: int = 100) -> bool:
        """逐字输入文本（模拟真人打字）"""
        element = await self.find_element(selector)
        if element:
            try:
                self.current_step = f"输入文本: {text[:20]}..."
                logger.info(f"⌨️  {self.current_step}")
                await element.clear()
                for char in text:
                    await element.type(char, delay=delay)
                await self.random_delay(0.5, 1)
                return True
            except Exception as e:
                logger.error(f"❌ 输入失败: {e}")
        return False

    async def upload_file(self, selector: str, file_path: str) -> bool:
        """上传文件"""
        element = await self.find_element(selector)
        if element:
            try:
                path = Path(file_path)
                if not path.exists():
                    logger.error(f"❌ 文件不存在: {file_path}")
                    return False

                self.current_step = f"上传文件: {path.name}"
                logger.info(f"📤 {self.current_step}")
                await element.set_input_files(str(path.absolute()))
                await self.random_delay(1, 2)
                return True
            except Exception as e:
                logger.error(f"❌ 上传失败: {e}")
        return False

    async def screenshot(self, selector: str = None, path: str = None) -> str:
        """截图"""
        try:
            if path is None:
                path = f"/tmp/screenshot_{self.current_step.replace(' ', '_')}.png"

            if selector:
                element = await self.find_element(selector)
                if element:
                    await element.screenshot(path=path)
            else:
                await self.page.screenshot(path=path)

            if self.config.get("logging", {}).get("show_screenshot", True):
                logger.info(f"📸 截图已保存: {path}")

            return path
        except Exception as e:
            logger.error(f"❌ 截图失败: {e}")
            return None

    async def get_text(self, selector: str) -> str:
        """获取元素文本"""
        element = await self.find_element(selector)
        if element:
            try:
                return await element.text_content()
            except:
                pass
        return ""

    async def is_visible(self, selector: str) -> bool:
        """检查元素是否可见"""
        element = await self.find_element(selector)
        if element:
            try:
                return await element.is_visible()
            except:
                pass
        return False

    async def scroll_down(self, pixels: int = 500):
        """向下滚动页面"""
        await self.page.evaluate(f"window.scrollBy(0, {pixels})")
        await self.random_delay(0.5, 1)

    async def scroll_up(self, pixels: int = 500):
        """向上滚动页面"""
        await self.page.evaluate(f"window.scrollBy(0, -{pixels})")
        await self.random_delay(0.5, 1)

    async def wait_for_selector(self, selector: str, timeout: int = None) -> bool:
        """等待元素出现"""
        if timeout is None:
            timeout = self.config["timeouts"]["element_wait"]

        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False

    async def random_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """随机延时（模拟人类操作）"""
        import random

        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def human_like_delay(self):
        """人类般的随机延时"""
        import random

        delays = [
            (0.5, 1.5),  # 快速操作
            (1, 2),  # 普通操作
            (2, 4),  # 复杂操作
        ]
        min_d, max_d = random.choice(delays)
        await self.random_delay(min_d, max_d)

    async def close(self):
        """关闭浏览器"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("👋 浏览器已关闭")
        except Exception as e:
            logger.error(f"❌ 关闭浏览器失败: {e}")

    async def get_current_url(self) -> str:
        """获取当前页面URL"""
        return self.page.url

    async def refresh_page(self):
        """刷新页面"""
        await self.page.reload()
        await self.random_delay(1, 2)
