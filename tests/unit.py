#! usr/bin/python3

"""
[Test file for flask apps. Import remaining dependencies.]
"""

# imports
import pytest
import unittest
import requests
import pytest_mock_server

# from app import break_queue FIXME: import error due to folder add
from slack_sdk import WebClient

class TestApp(unittest.TestCase):
    
    @pytest.mark.server(url='http://localhost:5000', method=['GET', 'POST'])
    def setUp(self):
        self.client = WebClient(
            token=""
        )
    
    def tearDown(self):
        pass
        
    def _post_message(self):
        response = self.client.chat_postMessage(
            channel='#testing_ground',
            text='test_post_message'
        )
        self.assertEqual(response.status_code, 200)

    def _authentication_failure(self):
        self.client_two = WebClient(
            token='faketokenforthetest'
        )
        
        self.assertNotEqual(self.client_two.token, self.client.token)
        
    def _authentication_success(self):
        self.client_success = WebClient(
            token=""
        )
        
        self.assertEqual(self.client_success.token, self.client.token)
        
    def _check_queue_size(self):
        queue = break_queue.maxlen
        
        self.assertEqual(queue, 3)
        

if __name__ == '__main__':
    unittest.main()