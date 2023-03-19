from ..models.users import User, Admin
from flask import request
from flask_restx import Resource, fields, Namespace
from functools import wraps
from werkzeug.security import generate_password_hash
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from http import HTTPStatus
from ..models.students import Student


admin_ns = Namespace('admin', description='Admin related operations')


admin_model = admin_ns.model('Admin', {
        'first_name': fields.String(required=True, description='The user name'),
        'last_name': fields.String(required=True, description='The user name'),
        'email': fields.String(required=True, description='The user email'),
        'password': fields.String(required=True, description='The user password'),
        'phone': fields.String(required=True, description='The user phone number'),
        'role': fields.String(required=True, description='The user role'),
    }
)

#   In production you comment this route 
#   and create admin from the terminal
@admin_ns.route('/create_admin')
class CreateAdminView(Resource):
    @admin_ns.doc(description='Create a new admin user from the admin dashboard')
    @admin_ns.expect(admin_model)

    def post(self):
        '''
        Create a new admin user
        '''
        data = request.get_json()
        user = User.get_by_email(data.get('email'))

        # check if user already exists
        if user:
            return {'message': 'User already exists'}, HTTPStatus.CONFLICT
        
        # create new user
        new_user = Admin(
            first_name = data.get('first_name'),
            last_name = data.get('last_name'),
            email = data.get('email'),
            password_hash = generate_password_hash(data.get('password')),
            phone = data.get('phone'),
            role = data.get('role'),
            is_admin = True,
            user_type = 'admin'
        )

        new_user.save()

        return {'message': 'Admin created successfully'}, HTTPStatus.CREATED
    
    
#   admin assigns registration id
def assign_registration_id():
    last_student = Student.query.order_by(Student.id.desc()).first()
    
    if not last_student:
        return 'STU00001'
    
    student_id = last_student.id
    new_student_id = student_id + 1
    new_student_id = '0000' + str(new_student_id)
    new_student_id = 'STU' + new_student_id[-5:]

    return new_student_id

#   get user type (admin, student)
def get_user_type(id: int):
    '''
    Get the type of user type
    '''

    user = User.query.filter_by(id=id).first()

    if user:
        return user.user_type
    
    return None


def admin_required():
    '''
    Custom decorator to check if the user is an admin
    '''
    def wrapper(fn):
        @wraps(fn)

        def decorated(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()

            if not get_user_type(claims['sub']) == 'admin':
                return {'message': 'You are not authorized to view this page.'}, HTTPStatus.UNAUTHORIZED      
            
            return fn(*args, **kwargs)
        
        return decorated
    
    return wrapper


def admin_or_student_required():
    '''
    Custom decorator to check if the user is an admin
    '''
    def wrapper(fn):
        @wraps(fn)

        def decorated(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()

            if not get_user_type(claims['sub']) == 'admin' or not get_user_type(claims['sub']) == 'student':
                return {'message': 'You are not authorized to view this page.'}, HTTPStatus.UNAUTHORIZED      
            
            return fn(*args, **kwargs)
        
        return decorated
    
    return wrapper

def is_admin_or_student(student_id: int):
    '''
        Check if the user is an admin or the student
    '''
       
    claims = get_jwt()
    current_user = get_jwt_identity()

    if (get_user_type(claims['sub']) == 'admin') or (int(current_user) == student_id):
        return True
    
    return False


