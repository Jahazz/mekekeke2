import os
import threading

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Event import Event
from Message import Message
from User import User
from WaitForMessage import WaitForMessage


class Client:
    def __init__(self, driver):
        self.driver = driver
        self.send_message_button = WebDriverWait(self.driver, 100).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="box-interface-input"]')))
        self.local_user = User()
        self.remote_user = None
        self.wait_until_next_message_driver = None
        self.wait_until_disconnect_driver = None
        self.send_message_box = self.driver.find_element_by_id("box-interface-input")
        self.message_log = self.driver.find_element_by_id("log-dynamic")
        self.on_message = Event()
        self.on_disconnect = Event()
        self.is_started = True

    def end_conversation(self):
        self.is_started = False
        self.wait_until_next_message_driver = None
        self.wait_until_disconnect_driver = None
        self.driver.close()

    def initialize(self):

        threading.Thread(target=self.wait_until_next_message).start()
        threading.Thread(target=self.wait_until_disconnect).start()
        threading.Thread(target=self.wait_for_prompt).start()



    def send_message(self, message):
        if self.is_started:
            self.send_message_box.send_keys(message)
            self.send_message_box.send_keys(Keys.RETURN)

    def get_last_message(self):
        last_msg = self.message_log.find_elements_by_xpath("./*")[-1]
        sender = last_msg.find_element_by_class_name("nick")
        message = last_msg.find_element_by_class_name("log-msg-text")
        if sender.text == "Ty:":
            sender = self.remote_user
        else:
            sender = self.local_user
        message_text = message.text

        return Message(sender, message_text, sender is self.remote_user)

        pass

    def wait_until_next_message(self):
        if self.is_started:
            try:
                self.wait_until_next_message_driver = WebDriverWait(self.driver, 300)
                self.wait_until_next_message_driver.until(WaitForMessage(self.message_log))
                last_message = self.get_last_message()
                self.on_message(last_message)
                self.wait_until_next_message()
            except:
                self.wait_until_next_message()

    def wait_for_prompt(self):
        if self.is_started:
            try:
                prompt = WebDriverWait(self.driver, 20).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="sd-current"]/div')))
                button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="box-interface-input"]')))
                button.click()
            except:
                self.wait_for_prompt()


    def wait_until_disconnect(self):
        if self.is_started:
            try:
                self.wait_until_disconnect_driver = WebDriverWait(self.driver,100000)
                self.wait_until_disconnect_driver.until(
                    EC.visibility_of_element_located((By.ID, 'log-static-end-talk')))
                self.on_disconnect(self)
            except:
                self.wait_until_disconnect()




