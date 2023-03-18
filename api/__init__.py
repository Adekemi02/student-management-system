from flask import Flask
from .config.config import config
from .utils import db
from .utils.blocklist import BLACKLIST
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api
from .models.users import User, Admin
from .models.students import Student, Enrollment
from .models.courses import Course
from .admin.admin import admin_ns
from .auth.view import auth_ns
from .student.views import student_ns
from .courses.views import course_ns
from http import HTTPStatus


def create_app(config=config['dev']):
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)

    jwt = JWTManager(app)
    
    migrate = Migrate(app, db)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload['jti'] in BLACKLIST
    
    @jwt.expired_token_loader
    def expired_token_callback():
        response = {
            "message": "The token has expired",
            "error": "token_expired"
        }
        return response, HTTPStatus.UNAUTHORIZED
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        response = {
            "description": "Signature verification failed",
            "error": "invalid_expired"
        }
        return response, HTTPStatus.UNAUTHORIZED
        
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        response = {
            "description": "Request does not contain an access token",
            "error": "authorization_required"
        }
        return response, HTTPStatus.UNAUTHORIZED
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        response = {
            "message": "The token has been revoked",
            "error": "token_revoked"
        }
        return response, HTTPStatus.UNAUTHORIZED
    
    authorizations = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            "description": "Add a JWT token to the header with ** Bearer &lt;JWT token&gt; to authorize **"
        }
    }

    api = Api(app,
              title="Student Management System",
              description="A simple student management system",
              authorizations=authorizations,
              security="Bearer Auth"
              
            )
    
    api.add_namespace(admin_ns)
    api.add_namespace(auth_ns)
    api.add_namespace(student_ns)
    api.add_namespace(course_ns)
    
    @app.shell_context_processor
    def make_shell_context():
        return {
            "db": db,
            "User": User,
            "Admin": Admin,
            "Student": Student,
            "Course": Course,
            "Enrollment": Enrollment
        }
    
    return app