#! usr/bin/python3

"""Functional Test for slack app"""

# imports
import pytest
import time
import unittest
import requests
import pytest_mock_server

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from flask_testing import LiveServerTestCase
from slack_sdk import WebClient


class FuncTestApp(unittest.TestCase):
        
    @pytest.mark.server(url='http://localhost:5000', method=['GET', 'POST'])
    def setUp(self):
        self.client = WebClient(
            token=""
        )
        self.browser = webdriver.Chrome()
        self.browser.get(url='')
        time.sleep(2)
        self.browser.find_element_by_name("domain").send_keys('customerhddev-hmk7767')
        self.browser.find_element_by_css_selector('.margin_bottom_150').click()
        time.sleep(2)
        self.browser.find_element_by_id('google_login_button').click()
        self.browser.find_element_by_name('identifier').send_keys('')
        self.browser.find_element_by_css_selector('.VfPpkd-RLmnJb').click()
        time.sleep(2)
        self.browser.find_element_by_name('password').send_keys('')
        self.browser.find_element_by_css_selector('.VfPpkd-RLmnJb').click()
        time.sleep(2)
        self.browser.find_element_by_xpath("//button[@class='c-button-unstyled p-download_modal__not_now margin_right_50 bold']").click()
        
    def tearDown(self):
        time.sleep(10)
        self.browser.close()

    def _queue_is_empty_on_request(self):
        try:
            self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']").send_keys('/testqueue')
            self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']").send_keys(Keys.ENTER)
            self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']").send_keys(Keys.RETURN)
        except:
            self.browser.find_element_by_xpath("//div[@class='ql-editor']").send_keys(Keys.ENTER)
        
        q = self.browser.find_element_by_xpath("//div[@class='p-workspace__primary_view_body']").text
        self.assertIn('No one on break', q)
                
    def _payload_sent_for_break_event(self):
        # call slash command(break)
        # see if a in b
        try:
            self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']").send_keys('/testbreak')
            self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']").send_keys(Keys.ENTER)
            self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']").send_keys(Keys.RETURN)
        except:
            self.browser.find_element_by_xpath("//div[@class='ql-editor']").send_keys(Keys.ENTER)
            time.sleep(3)
        
        slash = self.browser.find_element_by_xpath("//div[@class='p-workspace__primary_view_body']").text
        self.assertIn('break', slash)
    
    def test_action_recognized_on_event_with_limit_of_two(self):
        # see if a in b
        slash = self.browser.find_element_by_xpath("//div[@class='p-workspace__primary_view_body']").text
        self.assertIn('break', slash)
        self.assertIn('back', slash)
        
    
    def _payload_sent_on_help_event(self):
        # call slash command
        # see if a in b
        try:
            self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']").send_keys('/testhelp')
            self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']").send_keys(Keys.ENTER)
            self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']").send_keys(Keys.RETURN)
            self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']").send_keys(Keys.RETURN)
        except:
            self.browser.find_element_by_xpath("//div[@class='ql-editor']").send_keys(Keys.ENTER)
            time.sleep(3)
        
        slash = self.browser.find_element_by_xpath("//div[@class='p-workspace__primary_view_body']").text
        self.assertIn('help with BreakBot', slash)
    
    def _user_appended_to_break_queue(self):
        # call slash for queue
        # see if a in b
        try:
            self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']").send_keys('/testqueue')
            self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']").send_keys(Keys.ENTER)
            self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']").send_keys(Keys.ENTER)
            if self.browser.find_element_by_xpath("//div[@class='ql-editor ql-blank']") == self.browser.find_element_by_xpath("//div[@class='ql-editor']"):
                self.browser.find_element_by_xpath("//div[@class='ql-editor']").send_keys(Keys.ENTER)
        except:
            self.browser.find_element_by_xpath("//div[@class='ql-editor']").send_keys(Keys.ENTER)
            time.sleep(3)
        
        q = self.browser.find_element_by_xpath("//div[@class='p-workspace__primary_view_body']").text
        self.assertIn('adrian.brown', q)
            
    
    def _user_removed_from_break_queue_on_back(self):
        # see if a in b
        q = self.browser.find_element_by_xpath("//div[@class='p-workspace__primary_view_body']").text
        self.assertIn('adrian.brown, is back', q)    

if __name__ == '__main__':
    unittest.main()