from playwright.sync_api import Page
from utils.log import setup_logger

logger = setup_logger(__name__)

class SubmitEvent:
    def __init__(self, driver: Page):
        self.page = driver

    def check_all_and_submit(self):
        print("⏳ 等待 logoBtn 出現中...")
        try:
            self.page.wait_for_selector(".logoBtn", timeout=5000)
            logo_buttons = self.page.locator(".logoBtn")
            total = logo_buttons.count()
            print(f"🔍 實際找到了 {total} 個 .logoBtn")
        except Exception as e:
            print("❌ 完全找不到 .logoBt`n：", e)

        for i in range(total):
            logger.info(f"處理第 {i+1} 個活動")
            self.process_single_event(i)

    def process_single_event(self, index: int):
        try:
            self.page.locator(".logoBtn").nth(index).click()
            logger.info(f"點擊第 {index+1} 個 .logoBtn")

            self.submit_radio_form()
            self.close_modal_and_back()

        except Exception as e:
            logger.error(f"第 {index+1} 個活動發生錯誤：{e}")

    def submit_radio_form(self):
        self.page.wait_for_selector("input[type='radio']", timeout=5000)
        radios = self.page.locator("input[type='radio']")
        count = radios.count()

        if count == 0:
            logger.warning("沒有找到任何 radio，跳過本次提交")
            return

        logger.info(f"找到 {count} 個 radio")

        for i in range(count):
            r = radios.nth(i)
            if r.is_visible() and r.is_enabled():
                r.click()
                logger.info(f"點擊第 {i+1} 個 radio")
            else:
                logger.warning(f"跳過第 {i+1} 個 radio（無法點擊）")

        self.page.locator("#LoginAPI").click()
        logger.info("點擊 LoginAPI 提交")

    def close_modal_and_back(self):
        self.page.wait_for_selector("button:has-text('關閉')", timeout=10000)
        self.page.locator("button:has-text('關閉')").click()
        logger.info("關閉成功彈窗")

        self.page.locator("#ActivityList-tab").click()
        logger.info("回到活動清單頁")
        self.page.wait_for_timeout(1000)
