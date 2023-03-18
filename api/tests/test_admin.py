# import unittest
# import json
# from ..import create_app
# from ..config.config import config
# from ..utils import db
# from ..models.users import User, Admin


# class UserTestCase(unittest.TestCase):
    
#     def setUp(self):

#         self.app = create_app(config=config['test'])

#         self.appctx = self.app.app_context()

#         self.appctx.push()

#         self.client = self.app.test_client()

#         db.create_all()
        

#     def tearDown(self):

#         db.drop_all()

#         self.appctx.pop()

#         self.app = None

#         self.client = None


#     def test_admin(self):

#         data = {
#             'first_name':'Admin',
#             'last_name': 'AdminOne',
#             'email':'admin13@gmail.com',
#             'password':'password123',
#             'phone':'08012345678',
#             'role':'admin',
#             'user_type':'admin'
#         } 

#         response = self.client.post('/auth/create_admin', json=data)

#         admin = User.query.filter_by(email='admin13@gmail.com').first()

#         assert admin.first_name == 'Admin'

#         assert response.status_code == 404


