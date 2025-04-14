import os
import base64
import time
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from detector.captcha import CaptchaSolver
from playwright.sync_api import Page

load_dotenv()

class UbotLogin:
    BASE_URL = "https://cardweb.ubot.com.tw/register_extra"

    def __init__(self, driver: Page):
        self.sid = os.getenv("SID")
        self.birth = os.getenv("BIRTH")
        self.page = driver

    def get_captcha(self):
        self.page.goto(self.BASE_URL)
        self.page.wait_for_selector("#imgV")
        time.sleep(2)

        img_src = self.page.locator("#imgV").get_attribute("src")
        if not img_src.startswith("data:image/png;base64,"):
            raise Exception("❌ 驗證碼圖片未載入，請確認網站是否有變更")

        img_base64 = img_src.split(",")[1]
        img_bytes = base64.b64decode(img_base64)
        img = Image.open(BytesIO(img_bytes))
        img_path = "captcha.png"
        img.save(img_path)

        solver = CaptchaSolver()
        captcha_text = solver.decode_captcha(img_path)
        print("🔢 Decoded CAPTCHA:", captcha_text)
        return captcha_text

    def login(self, captcha_text):
        birth_year, birth_month, birth_day = self.birth[:4], self.birth[4:6], self.birth[6:]

        self.page.fill("#tbSID", self.sid)
        
        self.page.select_option("#dataYEAR", birth_year)
        self.page.select_option("#dataMONTH", birth_month)
        self.page.select_option("#dataDAY", birth_day)

        self.page.fill("#code_input", captcha_text)

        self.page.click("#btnAjaxPost")


    def run(self):
        captcha = self.get_captcha()
        self.login(captcha)
        print("🎉 成功獲取活動頁面！")
