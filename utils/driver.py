# utils/driver.py
from playwright.sync_api import sync_playwright, Browser, Page

class PlaywrightDriverManager:
    _playwright = None
    _browser: Browser = None
    _context = None
    _page: Page = None

    @classmethod
    def get_driver(cls, headless: bool = True) -> Page:
        """回傳已初始化的 Playwright Page（可重用）"""
        if cls._page is None:
            cls._playwright = sync_playwright().start()
            cls._browser = cls._playwright.chromium.launch(headless=headless)
            cls._context = cls._browser.new_context()
            cls._page = cls._context.new_page()
        return cls._page

    @classmethod
    def close(cls):
        """關閉資源"""
        if cls._context:
            cls._context.close()
            cls._context = None
        if cls._browser:
            cls._browser.close()
            cls._browser = None
        if cls._playwright:
            cls._playwright.stop()
            cls._playwright = None
        cls._page = None
