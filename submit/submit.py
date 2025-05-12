import os
import time
from playwright.sync_api import Page
from utils.log import setup_logger

logger = setup_logger(__name__)

class SubmitEvent:
    def __init__(self, driver: Page):
        self.page = driver

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
        try:
            self.page.locator(".logoBtn").nth(index).click()
            submitted = self.submit_radio_form()
            if submitted:
                self.close_modal_and_back()
            else:
                logger.warning(f"第 {index+1} 個活動未成功提交，跳過關閉與返回流程")
        except Exception as e:
            logger.error(f"第 {index+1} 個活動發生錯誤：{e}")
            self.capture_error(f"event_{index+1}")

    def submit_radio_form(self):
        try:
            self.page.wait_for_selector("input[type='radio']", timeout=3000)
        except Exception:
            logger.warning("radio 元素未出現，跳過提交")
            return False

        try:
            radios = self.page.locator("input[type='radio']")
            count = radios.count()

            for i in range(count):
                try:
                    r = radios.nth(i)
                    if r.is_visible() and r.is_enabled():
                        r.click()
                        break
                except Exception:
                    continue

            self.page.locator("#LoginAPI").click()
            return True
        except Exception as e:
            logger.error(f"表單提交失敗：{e}")
            self.capture_error("submit_radio_form")
            return False

    def close_modal_and_back(self):
        try:
            self.page.wait_for_selector("button:has-text('關閉')", timeout=10000)
            self.page.locator("button:has-text('關閉')").click()
            self.page.locator("#ActivityList-tab").click()
            self.page.wait_for_selector(".logoBtn")
        except Exception as e:
            logger.error(f"返回活動清單失敗：{e}")
            self.capture_error("close_modal_and_back")

    def capture_error(self, name: str):
        os.makedirs("screenshots", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/screenshot_{name}_{timestamp}.png"
        self.page.screenshot(path=filename, full_page=True)
        logger.info(f"已截圖：{filename}")
