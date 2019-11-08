from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC


class WaitForMessage(object):
    def __init__(self, message_log):
        self.message_log = message_log
        self.log_len = len(self.message_log.find_elements_by_xpath("./*"))

    def __call__(self, driver):
        log_len = len(self.message_log.find_elements_by_xpath("./*"))
        return log_len != self.log_len
