from selenium import webdriver
import time

class SubmitEvent:
    def __init__(self, driver:webdriver):
        self.driver = driver

    def check_all_radios_and_submit(self):
        radios = self.driver.find_elements(webdriver.common.by.By.XPATH, "//input[@type='radio']")
        for radio in radios:
            self.driver.execute_script("arguments[0].click();", radio)

        submit_button = self.driver.find_element(webdriver.common.by.By.ID, "LoginAPI")
        self.driver.execute_script("arguments[0].click();", submit_button)

