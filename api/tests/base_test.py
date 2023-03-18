import unittest
from ..import create_app
from ..config.config import config
from ..utils import db
from ..models.users import User, Admin


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