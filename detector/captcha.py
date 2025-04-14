import os
from twocaptcha import TwoCaptcha

class CaptchaSolver:
    def __init__(self):
        self.api_key = os.getenv("API_KEY_2CAPTCHA")
        self.solver = TwoCaptcha(self.api_key)

    def decode_captcha(self, img_path):
        try:
            print("🔄 提交驗證碼至 2Captcha...")
            result = self.solver.normal(img_path)
            captcha_text = result["code"]
            print(f"✅ 2Captcha 解析結果：{captcha_text}")
            return captcha_text
        except Exception as e:
            print(f"❌ 驗證碼解析失敗：{e}")
            return None

# 測試用
if __name__ == "__main__":
    img_path = "captcha.png"
    solver = CaptchaSolver()
    solver.decode_captcha(img_path)