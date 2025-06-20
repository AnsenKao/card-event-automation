import os
import time
from playwright.sync_api import Page
from dotenv import load_dotenv
from utils.log import setup_logger
from utils.email_sender import EmailSender # Changed import

load_dotenv()

logger = setup_logger(__name__)

class SubmitEvent:
    def __init__(self, driver: Page):
        self.page = driver
        self.current_index = -1
        # Initialize EmailSender instance
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port_str = os.getenv("SMTP_PORT")
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL") # Also get recipient here for checking

        self.smtp_port = None
        if self.smtp_port_str:
            try:
                self.smtp_port = int(self.smtp_port_str)
            except ValueError:
                logger.error("Invalid SMTP_PORT in .env file. Must be an integer.")

        if all([self.sender_email, self.smtp_server, self.smtp_port, self.smtp_user, self.smtp_password]):
            self.email_sender_instance = EmailSender(
                smtp_server=self.smtp_server,
                smtp_port=self.smtp_port,
                smtp_user=self.smtp_user,
                smtp_password=self.smtp_password,
                from_email=self.sender_email
            )
        else:
            self.email_sender_instance = None
            logger.error("Email sender not initialized due to missing configuration in .env file.")

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
            try:
                li = radio.locator("xpath=ancestor::li")
                label_text = li.locator("label").inner_text()
                link = li.locator("a").get_attribute("href")
            except Exception:
                label_text = f"Radio {i+1}"
                link = None

            if self.click_and_submit_radio(radio, i):
                self.handle_modal_after_submit(activity_name=label_text, activity_link=link)
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

    def handle_modal_after_submit(self, activity_name=None, activity_link=None):
        try:
            self.page.wait_for_selector("button:has-text('關閉')", timeout=20000)
            self.page.locator("button:has-text('關閉')").click()
            self.page.locator("#ActivityList-tab").click()
            if activity_name:
                logger.info(f"已成功添加活動【{activity_name}】")
                # Send email notification using the EmailSender instance
                if self.email_sender_instance and self.recipient_email:
                    email_subject = f"活動【{activity_name}】已成功添加"
                    if activity_link:
                        email_body = f"活動【{activity_name}】已成功添加到 Ubot。\n連結：{activity_link}"
                    else:
                        email_body = f"活動【{activity_name}】已成功添加到 Ubot。"
                    self.email_sender_instance.send_email(
                        to_email=self.recipient_email,
                        subject=email_subject,
                        body=email_body
                    )
                elif not self.recipient_email:
                    logger.error("Recipient email (RECIPIENT_EMAIL) is missing in .env file. Email not sent.")
                else:
                    logger.error("Email not sent because EmailSender was not initialized (check .env configuration).")
            else:
                logger.info("已成功添加活動")
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
