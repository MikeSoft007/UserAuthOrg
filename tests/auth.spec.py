import unittest
import sys
import os
# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
from flask_jwt_extended import decode_token
from app import create_app, db
from app.models import User, Organization
from flask import json


class UniteTestCase(unittest.TestCase):
    '''Unit Test. 
    The tests covers token generation, experation and organization access.'''
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

    def register_user(self, firstName, lastName, email, password, phone):
        return self.client().post('/auth/register', data=json.dumps({
            'firstName': firstName,
            'lastName': lastName,
            'email': email,
            'password': password,
            'phone': phone
        }), content_type='application/json')

    def login_user(self, email, password):
        return self.client().post('/auth/login', data=json.dumps({
            'email': email,
            'password': password
        }), content_type='application/json')

    def test_token_expiry(self):
        self.register_user('michael', 'ekpenyong', 'mekpenyong2@gmail.com', 'securepassword', '123-456-7890')
        response = self.login_user('mekpenyong2@gmail.com', 'securepassword')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        access_token = data['data']['accessToken']
        decoded_token = decode_token(access_token)
        exp_timestamp = decoded_token['exp']
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
        self.assertLessEqual(exp_datetime, datetime.utcnow() + timedelta(minutes=15))

    def test_token_contains_correct_user_details(self):
        self.register_user('michael', 'ekpenyong', 'mekpenyong2@gmail.com', 'securepassword', '123-456-7890')
        response = self.login_user('mekpenyong2@gmail.com', 'securepassword')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        access_token = data['data']['accessToken']
        decoded_token = decode_token(access_token)
        user_id_in_token = decoded_token['sub']
        self.assertEqual(user_id_in_token, data['data']['user']['userId'])

    def test_create_organization(self):
        self.register_user('michael', 'ekpenyong', 'mekpenyong2@gmail.com', 'securepassword', '123-456-7890')
        login_response = self.login_user('mekpenyong2@gmail.com', 'securepassword')
        login_data = json.loads(login_response.data)
        access_token = login_data['data']['accessToken']
        response = self.client().post('/api/organisations', data=json.dumps({
            'name': 'Team Sophia',
            'description': 'This is an organization for Sophia developers'
        }), headers={'Authorization': f'Bearer {access_token}'}, content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['status'], 'success')
        self.assertIn('orgId', data['data'])
        self.assertEqual(data['data']['name'], 'Team Sophia')

    def test_user_can_access_own_organization(self):
        self.register_user('michael', 'ekpenyong', 'mekpenyong2@gmail.com', 'securepassword', '123-456-7890')
        response = self.login_user('mekpenyong2@gmail.com', 'securepassword')
        data = json.loads(response.data)
        access_token = data['data']['accessToken']
        response_ = self.client().get('/api/organisations', headers={'Authorization': f'Bearer {access_token}'})
        access_data = response_.json
        self.assertEqual(response_.status_code, 200)
        org_name = access_data['data']['organisations'][0]['name']
        self.assertEqual(org_name, "michael's Organisation")

    def test_user_cannot_access_other_organizations(self):
        self.register_user('michael', 'ekpenyong', 'mekpenyong2@gmail.com', 'securepassword', '123-456-7890')
        response = self.login_user('mekpenyong2@gmail.com', 'securepassword')
        data = json.loads(response.data)
        access_token = data['data']['accessToken']
        response_ = self.client().get('/api/organisations', headers={'Authorization': f'Bearer {access_token}'})
        access_data = response_.json
        self.assertEqual(response_.status_code, 200)
        org_name = access_data['data']['organisations'][0]['name']
        self.assertNotEqual(org_name, "Other's Organization")



class EndToEndTestCase(unittest.TestCase):
    '''End-to-end tests. 
    The tests covers successful user registration, validation errors, and database constraints.'''
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

    def register_user(self, firstName, lastName, email, password, phone):
        return self.client().post('/auth/register', data=json.dumps({
            'firstName': firstName,
            'lastName': lastName,
            'email': email,
            'password': password,
            'phone': phone
        }), content_type='application/json')

    def login_user(self, email, password):
        return self.client().post('/auth/login', data=json.dumps({
            'email': email,
            'password': password
        }), content_type='application/json')

    def test_user_registration(self):
        response = self.register_user('michael', 'ekpenyong', 'mekpenyong2@gmail.com', 'securepassword', '123-456-7890')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['status'], 'success')
        self.assertIn('accessToken', data['data'])
        self.assertIn('user', data['data'])
        self.assertEqual(data['data']['user']['firstName'], 'michael')
        self.assertEqual(data['data']['user']['email'], 'mekpenyong2@gmail.com')

    def test_user_login(self):
        self.register_user('michael', 'ekpenyong', 'mekpenyong2@gmail.com', 'securepassword', '123-456-7890')
        response = self.login_user('mekpenyong2@gmail.com', 'securepassword')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIn('accessToken', data['data'])
        self.assertIn('user', data['data'])


    def test_duplicate_email_registration(self):
        # Register the first user
        response1 = self.register_user('mark', 'essien', 'mark.essien@example.com', 'password', '111-222-3333')
        self.assertEqual(response1.status_code, 201)

        # Attempt to register another user with the same email
        response2 = self.register_user('esseien', 'mark', 'mark.essien@example.com', 'password', '444-555-6666')
        data = json.loads(response2.data)
        self.assertEqual(response2.status_code, 422)

        # Verify the error message
        data = json.loads(response2.data)
        print("DATA", data)
        self.assertIn('Email already exists', data['errors'][0]['message'])



if __name__ == '__main__':
    unittest.main()