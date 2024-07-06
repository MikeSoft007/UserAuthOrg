import unittest
import sys
import os

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Organization
from flask import json


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration(self):
        response = self.client().post('/auth/register', data=json.dumps({
            'firstName': 'michael',
            'lastName': 'ekpenyong',
            'email': 'mekpenyong2@gmail.com',
            'password': 'securepassword',
            'phone': '123-456-7890'
        }), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['status'], 'success')
        self.assertIn('accessToken', data['data'])
        self.assertIn('user', data['data'])
        self.assertEqual(data['data']['user']['firstName'], 'michael')
        self.assertEqual(data['data']['user']['email'], 'mekpenyong2@gmail.com')

if __name__ == '__main__':
    unittest.main()
