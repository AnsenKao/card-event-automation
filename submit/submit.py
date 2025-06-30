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
            time.sleep(2)
            
            all_radios = self.page.locator("input[type='radio']").all()
            logger.info(f"找到 {len(all_radios)} 個 radio 元素（包括隱藏的）")
            
            if not all_radios:
                logger.warning("沒有找到任何 radio 元素")
                return False
                
            success_count = 0
            for i, radio in enumerate(all_radios):
                try:
                    is_enabled = radio.is_enabled()
                    radio_id = radio.get_attribute("id")
                    radio_value = radio.get_attribute("value")
                    
                    logger.info(f"Radio {i+1}: ID={radio_id}, Value={radio_value}, Enabled={is_enabled}")
                    
                    if is_enabled:
                        radio.click(force=True)
                        logger.info(f"已強制點擊 radio {i+1}")
                        
                        self.page.locator("#LoginAPI").click()
                        logger.info(f"已點擊提交按鈕 for radio {i+1}")
                        
                        self.handle_modal_after_submit(activity_name=f"Radio {i+1} (ID: {radio_id})")
                        success_count += 1
                        
                except Exception as e:
                    if "Element is not visible" not in str(e):
                        logger.warning(f"處理 radio {i+1} 時發生錯誤: {e}")
                    continue
                    
            return success_count > 0
            
        except Exception as e:
            logger.error(f"查找 radio 元素時發生錯誤: {e}")
            return False

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
            try:
                self.page.locator("button.close").first.click()
            except Exception as e:
                logger.warning(f"點擊關閉按鈕失敗: {e}")

        # 返回到當前活動頁面
        try:
            self.page.locator(".logoBtn").nth(self.current_index).click()
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception as e:
            if "Timeout" not in str(e):
                logger.warning(f"返回當前活動頁面時發生錯誤: {e}")

    def capture_error(self, name: str):
        os.makedirs("screenshots", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/screenshot_{name}_{timestamp}.png"
        self.page.screenshot(path=filename, full_page=True)
        logger.info(f"已截圖：{filename}")
