from flask import request, jsonify
from flask_restx import Resource, fields, Namespace
from http import HTTPStatus
from ..models.users import User
from ..models.students import Student
from ..admin.admin import assign_registration_id
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from ..utils.blocklist import BLACKLIST


auth_ns = Namespace('auth', description='Authentication related operations')


signup_model = auth_ns.model('Signup', {
        'first_name': fields.String(required=True, description='The user name'),
        'last_name': fields.String(required=True, description='The user name'),
        'email': fields.String(required=True, description='The user email'),
        'password': fields.String(required=True, description='The user password'),
        'phone': fields.String(required=True, description='The user phone number'),
    }
)

login_model = auth_ns.model('Login', {
        'email': fields.String(required=True, description='The user email'),
        'password': fields.String(required=True, description='The user password'),
    }
)

@auth_ns.route('/signup')
class SignupView(Resource):
    @auth_ns.expect(signup_model)
    @auth_ns.doc(description='User signup')

    def post(self):
        '''
        Create a new student user
        '''

        data = request.get_json()
        user = User.get_by_email(data.get('email'))

        # check if user already exists
        if user:
            return {'message': 'User already exists'}, HTTPStatus.CONFLICT
        
        # create new user
        registration_id = assign_registration_id()
        new_user = Student(
            first_name = data.get('first_name'),
            last_name = data.get('last_name'),
            email = data.get('email'),
            password_hash = generate_password_hash(data.get('password')),
            phone = data.get('phone'),
            registration_id = registration_id,
            user_type = 'student'
        )

        new_user.save()

        student_record = {}
        student_record['id'] = new_user.id
        student_record['first_name'] = new_user.first_name
        student_record['last_name'] = new_user.last_name
        student_record['email'] = new_user.email
        student_record['phone'] = new_user.phone
        student_record['registration_id'] = new_user.registration_id
        
        return student_record, HTTPStatus.CREATED
    

@auth_ns.route('/login')
class LoginView(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.doc(description='User login',
                 params={
                     'email': 'The user email',
                     'password': 'The user password'
                    }
                )
    def post(self):
        '''
        This endpoint is for user login, which returns a token
        '''

        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        # check if email and password are provided
        if not email or not password:
            return {'message': 'Email and password are required'}, HTTPStatus.BAD_REQUEST
        
        user = User.get_by_email(email)

        # check if user exists
        if user and check_password_hash(user.password_hash, password):
            # generate token
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            response = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return response, HTTPStatus.OK

        return {"message": "This is not a registered email. Please signup"}, HTTPStatus.NOT_FOUND
        
        
@auth_ns.route('/refresh')
class RefreshToken(Resource):
    @auth_ns.doc(description='Refresh token')
    @jwt_required(refresh=True)
    def post(self):
        '''
        This endpoint is for refreshing the token
        '''

        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        return {'access_token': access_token}, HTTPStatus.OK
    

@auth_ns.route('/logout')
class LogoutView(Resource):
    @auth_ns.doc(description='Logout user')
    @jwt_required()
    def post(self):
        '''
        This endpoint is for user logout
        '''

        token = get_jwt()
        jti = token['jti']
        token_type = token['type']
        BLACKLIST.add(jti)

        return {"message": f"{token_type} token has been revoked"}, HTTPStatus.OK