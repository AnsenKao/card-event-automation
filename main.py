import argparse
import traceback
from login.login import UbotLogin
from submit.submit import SubmitEvent
from utils.driver import PlaywrightDriverManager

def main(driver):
    login_flow = UbotLogin(driver)
    login_flow.run()

    submit_flow = SubmitEvent(driver)
    submit_flow.check_all_and_submit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Ubot automation.")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Run browser with UI")
    parser.set_defaults(headless=True)

    args = parser.parse_args()

    try:
        driver = PlaywrightDriverManager.get_driver(headless=args.headless)
        main(driver)
    except Exception as e:
        print("❌ 發生錯誤：", e)
        traceback.print_exc()
    finally:
        PlaywrightDriverManager.close()
