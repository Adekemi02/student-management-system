from ..models.users import GoogleForm, Admin
from .admin import assign_registration_id
from werkzeug.security import generate_password_hash
from ..models.students import Student
from ..models.courses import Course


def populate_google_forms():

    # how data will be stored in the database
    admins = [
        {
            "first_name": "Admin",
            "last_name": "Admin",
            "email": "admin@gmail.com",
            "password": "admin101",
            "role": "admin",
            "is_admin": True
        },
    ]

    students = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "studentdoe@gmail.com",
            "password": "admin101",
        },
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "janedoe@gmail.com",
            "password": "admin101",
        }
    ]

    courses = [
        {
            "name": "Computer Science",
            "code": "CSC",
            "credit_unit": 3,
            "teacher": "Teacher 1"
        },
        {
            "name": "Mathematics",
            "code": "MTH",
            "credit_unit": 3,
            "teacher": "Teacher 2"
        }
    ]

    for user in admins:
        admin = Admin(
            name = user['name'],
            email = user['email'],
            password = generate_password_hash(user['password']),
            role = user['role'],
            is_admin = user['is_admin'],
            user_type = 'admin'

        )
        
        admin.save()

    for user in students:
        registration_id = assign_registration_id()
        student = Student(
            name = user['name'],
            email = user['email'],
            password = generate_password_hash(user['password']),
            user_type = 'student',
            registration_id = registration_id
        )

        student.save()

    for course in courses:
        course = Course(
            name = course['name'],
            code = course['code'],
            credit_unit = course['credit_unit'],
            teacher = course['teacher']
        )

        course.save()
