import unittest
from ..import create_app
from ..config.config import config
from ..utils import db
from ..models.users import User, Admin
from flask_jwt_extended import create_access_token


class UserTestCase(unittest.TestCase):
    
    def setUp(self):

        self.app = create_app(config=config['test'])

        self.appctx = self.app.app_context()

        self.appctx.push()

        self.client = self.app.test_client()

        db.create_all()
        

    def tearDown(self):

        db.drop_all()

        self.appctx.pop()

        self.app = None

        self.client = None


    def test_user(self):

        admin_signup_data = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": "testadmin@gmail.com",
            "password": "password",
            "phone": "08012345678",
            "role": "admin",
            # "user_type": "admin",
            # "is_admin": "True"
        }

        response = self.client.post('/admin/create_admin', json=admin_signup_data)

        admin = User.query.filter_by(email='testadmin@gmail.com').first()

        assert admin.first_name == 'Test'

        assert admin.last_name == 'Admin'

        assert response.status_code == 201

        student_signup_data = {
            "first_name": "Test",
            "last_name": "Student",
            "email": "teststudent@gmail.com",
            "password": "password",
            "registration_id": "STU0000",
            "phone": "08012345678",
        }

        response = self.client.post('/auth/signup', json=student_signup_data)

        assert response.status_code == 201


    def test_user_login(self):
        data = {
            "email": "teststudent@gmail.com",
            "password": "password"
        }

        response = self.client.post('/auth/login', json=data)

        assert response.status_code == 201