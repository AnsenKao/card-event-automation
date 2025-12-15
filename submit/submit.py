import os
import time
from playwright.sync_api import Page, Locator
from dotenv import load_dotenv
from utils.log import setup_logger
from utils.email_sender import EmailSender

load_dotenv()

logger = setup_logger(__name__)

class SubmitEvent:
    def __init__(self, driver: Page):
        self.page = driver
        self.current_index = -1
        
        # 選擇器配置化
        self.selectors = {
            "main_category_btn": ".logoBtn",
            "event_container": "li.formStyle",
            "submit_btn": "#LoginAPI",
            "modal_close_btn": "button:has-text('關閉')",
            "back_to_list_tab": "#ActivityList-tab"
        }

        # Email 初始化
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port_str = os.getenv("SMTP_PORT")
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")

        self.smtp_port = 587
        if self.smtp_port_str:
            try:
                self.smtp_port = int(self.smtp_port_str)
            except ValueError:
                self.smtp_port = 587

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

    def check_all_and_submit(self):
        try:
            self.page.wait_for_selector(self.selectors["main_category_btn"], timeout=10000)
            buttons = self.page.locator(self.selectors["main_category_btn"])
            total = buttons.count()
            logger.info(f"找到 {total} 個主分類")
        except Exception as e:
            logger.error("找不到主分類按鈕：%s", e)
            self.capture_error("no_category_found")
            return

        for i in range(total):
            self.process_single_event(i)

    def process_single_event(self, index: int):
        self.current_index = index
        try:
            self.page.locator(self.selectors["main_category_btn"]).nth(index).click()
            submitted = self.submit_all_radios()
            
            if submitted:
                self.page.locator(self.selectors["back_to_list_tab"]).click()
                self.page.wait_for_selector(self.selectors["main_category_btn"])
            else:
                logger.info(f"分類 {index+1} 無可提交項目")
                
        except Exception as e:
            logger.error(f"分類 {index+1} 錯誤：{e}")
            self.capture_error(f"event_{index+1}")

    def _find_event_rows(self):
        """
        智慧尋找 Rows
        """
        # 方法 A: 使用原本的 Class
        rows = self.page.locator(self.selectors["event_container"]).all()
        if rows:
            return rows

        # 方法 B (備援): 使用文字特徵定位
        logger.warning("找不到標準容器 Class，嘗試使用文字特徵定位...")
        try:
            anchors = self.page.get_by_text("起：").all()
            found_rows = []
            for anchor in anchors:
                row = anchor.locator("xpath=ancestor::li | ancestor::div[contains(@class, 'row')]").first
                if row.count() > 0:
                    found_rows.append(row)
            return found_rows
        except Exception as e:
            logger.warning(f"文字定位失敗: {e}")
            return []

    def submit_all_radios(self):
        try:
            time.sleep(2)
            activity_rows = self._find_event_rows()
            logger.info(f"找到 {len(activity_rows)} 個潛在活動區塊")
            
            if not activity_rows:
                return False

            success_count = 0
            for i, row in enumerate(activity_rows):
                try:
                    radio = row.locator("input[type='radio']").first
                    
                    if not radio.is_visible() or not radio.is_enabled():
                        continue

                    title, link = self._extract_info_safe(row)
                    
                    radio.click(force=True)
                    self.page.locator(self.selectors["submit_btn"]).click()
                    
                    self.handle_modal_after_submit(title, link)
                    success_count += 1

                except Exception as e:
                    logger.warning(f"Row {i+1} 處理失敗: {e}")
                    continue
            
            return success_count > 0

        except Exception as e:
            logger.error(f"submit_all_radios 全域錯誤: {e}")
            return False

    def _extract_info_safe(self, row_locator: Locator):
        title = "未命名活動"
        link = None
        try:
            if row_locator.locator("label").count() > 0:
                title = row_locator.locator("label").first.inner_text().strip()
            else:
                title = row_locator.locator("div[class*='col']").first.inner_text().replace("額滿", "").strip()
        except Exception:
            pass

        try:
            if row_locator.locator("a[href]").count() > 0:
                link = row_locator.locator("a[href]").first.get_attribute("href")
        except Exception:
            pass
        return title, link

    def handle_modal_after_submit(self, activity_name=None, activity_link=None):
        try:
            self.page.wait_for_selector(self.selectors["modal_close_btn"], timeout=20000)
            self.page.locator(self.selectors["modal_close_btn"]).click()
            self.page.locator(self.selectors["back_to_list_tab"]).click()
            
            if activity_name:
                self._send_notification(activity_name, activity_link)
        except Exception:
            # 備用關閉方案
            try:
                self.page.locator("button.close").first.click()
            except Exception:
                pass

        try:
            self.page.locator(self.selectors["main_category_btn"]).nth(self.current_index).click()
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

    def _send_notification(self, name, link):
        if not self.email_sender_instance or not self.recipient_email:
            return
        
        body = f"活動【{name}】已成功添加到 Ubot。"
        if link: body += f"\n連結：{link}"
        
        self.email_sender_instance.send_email(
            to_email=self.recipient_email,
            subject=f"活動【{name}】已成功添加",
            body=body
        )

    def capture_error(self, name: str):
        os.makedirs("screenshots", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.page.screenshot(path=f"screenshots/{name}_{timestamp}.png", full_page=True)