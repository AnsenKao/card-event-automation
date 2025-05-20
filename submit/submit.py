import os
import time
from playwright.sync_api import Page
from utils.log import setup_logger

logger = setup_logger(__name__)

class SubmitEvent:
    def __init__(self, driver: Page):
        self.page = driver
        self.current_index = -1

    def check_all_and_submit(self):
        try:
            self.page.wait_for_selector(".logoBtn", timeout=5000)
            buttons = self.page.locator(".logoBtn")
            total = buttons.count()
            logger.info(f"找到 {total} 個 .logoBtn")
        except Exception as e:
            logger.error("找不到 .logoBtn：%s", e)
            self.capture_error("no_logoBtn_found")
            return

        for i in range(total):
            logger.info(f"處理第 {i+1} 個活動")
            self.process_single_event(i)

    def process_single_event(self, index: int):
        self.current_index = index
        try:
            self.page.locator(".logoBtn").nth(index).click()
            submitted = self.submit_all_radios()
            if submitted:
                self.page.locator("#ActivityList-tab").click()
                self.page.wait_for_selector(".logoBtn")
            else:
                logger.warning(f"第 {index+1} 個活動未成功提交")
        except Exception as e:
            logger.error(f"第 {index+1} 個活動發生錯誤：{e}")
            self.capture_error(f"event_{index+1}")

    def submit_all_radios(self):
        try:
            self.page.wait_for_selector("input[type='radio']", timeout=3000)
        except Exception:
            logger.warning("radio 元素未出現，跳過提交")
            return False

        radios = self.page.locator("input[type='radio']")
        count = radios.count()
        success_count = 0

        for i in range(count):
            radio = radios.nth(i)
            if self.click_and_submit_radio(radio, i):
                self.handle_modal_after_submit()
                success_count += 1

        return success_count > 0

    def click_and_submit_radio(self, radio, index: int) -> bool:
        try:
            if radio.is_visible() and radio.is_enabled():
                radio.click()
                self.page.locator("#LoginAPI").click()
                return True
        except Exception as e:
            logger.warning(f"第 {index+1} 個 radio 提交失敗：{e}")
        return False

    def handle_modal_after_submit(self):
        try:
            self.page.wait_for_selector("button:has-text('關閉')", timeout=20000)
            self.page.locator("button:has-text('關閉')").click()
            self.page.locator("#ActivityList-tab").click()
        except Exception:
            logger.info("未出現完整關閉按鈕，嘗試點擊 modal 的 ×")
            self.page.locator("button.close").first.click()

        self.page.locator(".logoBtn").nth(self.current_index).click()
        self.page.wait_for_selector("input[type='radio']", timeout=3000)

    def capture_error(self, name: str):
        os.makedirs("screenshots", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/screenshot_{name}_{timestamp}.png"
        self.page.screenshot(path=filename, full_page=True)
        logger.info(f"已截圖：{filename}")
