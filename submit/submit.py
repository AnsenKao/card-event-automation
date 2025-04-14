from playwright.sync_api import Page

class SubmitEvent:
    def __init__(self, driver: Page):
        self.page = driver

    def check_all_radios_and_submit(self):
        # 找出所有 radio button
        radios = self.page.locator("//input[@type='radio']")
        count = radios.count()
        print(f"🔎 找到 {count} 個 radio 按鈕")

        for i in range(count):
            radio = radios.nth(i)
            try:
                is_visible = radio.is_visible()
                is_enabled = radio.is_enabled()
                print(f"👉 第 {i+1} 個 radio：Visible={is_visible}, Enabled={is_enabled}")
                if is_visible and is_enabled:
                    radio.click()
                    print(f"✅ 已點擊第 {i+1} 個 radio")
                else:
                    print(f"⚠️ 無法點擊第 {i+1} 個 radio（不可見或不可用）")
            except Exception as e:
                print(f"❌ 點擊第 {i+1} 個 radio 發生錯誤：{e}")

        # 點擊送出按鈕
        try:
            self.page.locator("#LoginAPI").click()
            print("🚀 已點擊提交按鈕 #LoginAPI")
        except Exception as e:
            print(f"❌ 點擊提交按鈕時發生錯誤：{e}")
