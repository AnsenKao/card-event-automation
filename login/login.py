import os
import base64
import time
from io import BytesIO
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from detector.captcha import CaptchaSolver
from utils.driver import WebDriverManager

class UbotLogin:
    BASE_URL = "https://cardweb.ubot.com.tw/register_extra"

    def __init__(self, driver:WebDriverManager):
        self.sid = os.getenv("SID")
        self.birth = os.getenv("BIRTH")
        self.driver = driver

    def get_captcha(self):
        """獲取驗證碼並解析"""
        self.driver.get(self.BASE_URL)
        time.sleep(2)  # 等待網頁載入
        
        # 找到驗證碼圖片
        captcha_img = self.driver.find_element(By.ID, "imgV")
        img_src = captcha_img.get_attribute("src")

        if not img_src.startswith("data:image/png;base64,"):
            raise Exception("❌ 驗證碼圖片未載入，請確認網站是否有變更")

        # 解析 Base64 圖片
        img_base64 = img_src.split(",")[1]
        img_bytes = base64.b64decode(img_base64)
        img = Image.open(BytesIO(img_bytes))
        img_path = "captcha.png"
        img.save(img_path)

        # 解析驗證碼
        solver = CaptchaSolver()
        captcha_text = solver.decode_captcha(img_path)
        print("🔢 Decoded CAPTCHA:", captcha_text)
        return captcha_text

    def login(self, captcha_text):
        """模擬填寫表單並登入"""
        sid_input = self.driver.find_element(By.ID, "tbSID")
        year_input = self.driver.find_element(By.ID, "dataYEAR")
        month_input = self.driver.find_element(By.ID, "dataMONTH")
        day_input = self.driver.find_element(By.ID, "dataDAY")
        captcha_input = self.driver.find_element(By.ID, "code_input")

        # 解析出生年月日
        birth_year, birth_month, birth_day = self.birth[:4], self.birth[4:6], self.birth[6:]

        # 填入表單
        sid_input.send_keys(self.sid)
        year_input.send_keys(birth_year)
        month_input.send_keys(birth_month)
        day_input.send_keys(birth_day)
        captcha_input.send_keys(captcha_text)

        # 按 Enter 或找到登入按鈕點擊
        submit_btn = self.driver.find_element(By.ID, "btnAjaxPost")
        submit_btn.click()
        time.sleep(10)  # 等待登入處理

    def run(self):
        """執行完整流程"""
        captcha_text = self.get_captcha()
        self.login(captcha_text)
        print("🎉 成功獲取活動頁面！")
        

# **執行程式**
if __name__ == "__main__":
    driver = WebDriverManager.get_driver()
    UbotLogin(driver).run()