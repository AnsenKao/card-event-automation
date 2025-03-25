from login.login import UbotLogin
from submit.submit import SubmitEvent
from utils.driver import WebDriverManager

import dotenv

dotenv.load_dotenv()

def main(driver:WebDriverManager):
    login_flow = UbotLogin(driver)
    login_flow.run()

    submit_flow = SubmitEvent(driver)
    submit_flow.check_all_radios_and_submit()

if __name__=="__main__":
    driver = WebDriverManager().get_driver()
    try:
        main(driver)
    except Exception as e:
        print