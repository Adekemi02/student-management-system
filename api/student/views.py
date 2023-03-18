from flask_restx import Resource, fields, Namespace
from flask import request
from http import HTTPStatus
from ..admin.admin import admin_required, is_admin_or_student
from ..models.students import Student, Enrollment
from ..models.courses import Course
from ..models.grades import Grade
from ..utils.grade import get_grade, convert_grade_to_gpa
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from ..utils import db


student_ns = Namespace('student', description='Student related operations')

student_signup_model = student_ns.model(
    'StudentSignup', {
        'first_name': fields.String(required=True, description='The user name'),
        'last_name': fields.String(required=True, description='The user name'),
        'email': fields.String(required=True, description='The user email'),
        'password': fields.String(required=True, description='The user password'),
        'phone': fields.String(required=True, description='The user phone number'),
    }
)

student_model = student_ns.model(
    'Student', {
        'id': fields.Integer(required=True, description='The user identifier'),
        'first_name': fields.String(required=True, description='The user name'),
        'last_name': fields.String(required=True, description='The user name'),
        'email': fields.String(required=True, description='The user email'),
        'password_hash': fields.String(required=True, description='The user password'),
        'phone': fields.String(required=True, description='The user phone number'),
        'registration_id': fields.String(required=True, description='The user registration id'),
    }
)

grade_model = student_ns.model(
    'Grade', {
        # 'grade': fields.Integer(required=True, description='The grade'),
        'course_id': fields.Integer(required=True, description='The course id'),
        'student_id': fields.Integer(required=True, description='The student id'),
        'score': fields.Integer(required=True, description='The score'),
    }
)

grade_update_model = student_ns.model(
    'GradeUpdate', {
        'score': fields.Integer(required=True, description='The score')
    }
)

@student_ns.route('/')
class GetAllStudents(Resource):
    @student_ns.marshal_list_with(student_model)
    @student_ns.doc(description = 
                    'This endpoint is only available for the admin user to get all students'
                    )
    @admin_required()
    def get(self):
        '''
        Get all students
        '''
        
        students = Student.query.all()

        return students, HTTPStatus.OK
    
@student_ns.route('/<int:student_id>')  # /api/student/1 del, put
class GetUpdateDeleteStudentByID(Resource):
    # @student_ns.marshal_with(student_model)
    @student_ns.doc(description =
                    '''
                        This endpoint is available for all authenticated 
                        users and admin to get a student by id
                    ''',
                    params = {"student_id": "The student's id"}
                    )
    @jwt_required()
    def get(self, student_id):
        '''
        Get a student by id
        '''

        if not is_admin_or_student(student_id):
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
        
        student = Student.get_by_id(student_id)

        if not student:
            return {'message': 'Student not found'}, HTTPStatus.NOT_FOUND

        student_info = {}
        student_info['id'] = student.id
        student_info['first_name'] = student.first_name
        student_info['last_name'] = student.last_name
        student_info['email'] = student.email
        student_info['phone'] = student.phone
        student_info['registration_id'] = student.registration_id

        return student_info, HTTPStatus.OK
    

    @student_ns.expect(student_signup_model)
    @student_ns.marshal_with(student_model)
    @student_ns.doc(description =
                    '''
                        This endpoint is available for all registered and authenticated
                        students to update their profile
                    '''
                    )
    @jwt_required()
    def put(self, student_id):
        '''
        Update a student by id
        '''
        
        student = Student.get_by_id(student_id)
        current_user = get_jwt_identity()

        # check if the student is the current user
        if student.id != current_user:
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED
        
        data = student_ns.payload

        student.first_name = data['first_name']
        student.last_name = data['last_name']
        student.email = data['email']
        student.password_hash = generate_password_hash(data['password'])
        student.phone = data['phone']

        student.update()

        student_info = {}
        student_info['id'] = student.id
        student_info['first_name'] = student.first_name
        student_info['last_name'] = student.last_name
        student_info['email'] = student.email
        student_info['phone'] = student.phone
        student_info['registration_id'] = student.registration_id
        
        return student, HTTPStatus.OK


    @student_ns.doc(description =
                    '''
                        This endpoint is available for only the admin to delete a student
                    ''',
                    params = {"student_id": "The student's id"}
                    )
    @admin_required()
    def delete(self, student_id):
        '''
        Delete a student by id
        '''
        student = Student.get_by_id(student_id)

        student.delete()

        return {'message': 'Student Deleted Successfully'}, HTTPStatus.OK
    

@student_ns.route('/<int:student_id>/courses')
class GetStudentCourses(Resource):
    @student_ns.doc(description =
                    '''
                        This endpoint is available for all authenticated users 
                        to get all courses registered by a student
                    ''',
                    params = {"student_id": "The student's id"}
                    )
    @jwt_required()
    def get(self, student_id):
        '''
        Get all courses registered by a student
        '''
        if not is_admin_or_student(student_id):
            return {'message': 'You are not authorized to perform this action'}, HTTPStatus.UNAUTHORIZED

        student = Student.get_by_id(student_id)
        courses = Enrollment.get_courses_by_student_id(student_id)

        course_list = []
        for course in courses:
            course_details = {}
            course_details['id'] = course.id
            course_details['registration_id'] = student.registration_id
            course_details['name'] = course.name
            course_details['course_code'] = course.course_code
            course_details['credit_unit'] = course.credit_unit
            course_details['teacher'] = course.teacher

            course_list.append(course_details)
        
        return course_list, HTTPStatus.OK
    

@student_ns.route('/<int:student_id>/grades')
class GetStudentGrades(Resource):
    @student_ns.doc(description =
                    '''
                        This endpoint is available for all authenticated 
                        users(Admin and Students) to retrieve a student grade
                    ''',
                    params = {"student_id": "The student's id"}
                    )
    @jwt_required()
    def get(self, student_id):
        '''
            Get a student grade    
        '''

        if not is_admin_or_student(student_id):
            return {'message': 'You are not authorized view this page'}, HTTPStatus.UNAUTHORIZED

        # check if student exists
        student = Student.get_by_id(student_id)
        if not student:
            return {'message': 'Student not found'}, HTTPStatus.NOT_FOUND
        
        # get the student grades
        courses = Enrollment.get_courses_by_student_id(student_id)

        course_list = []
        for course in courses:
            grade_res = {}
            get_grade = Grade.query.filter_by(student_id=student_id, 
                                              course_id=course.id).first()

            grade_res['course_name'] = course.name
            grade_res['course_id'] = course.id

            if get_grade:
                grade_res['id'] = get_grade.id
                grade_res['grade'] = get_grade.grade
                grade_res['score'] = get_grade.score

            else:
                grade_res['grade'] = None
                grade_res['score'] = None

            course_list.append(grade_res)

        return course_list, HTTPStatus.OK


@student_ns.route('/course/add_grade')
class AddGrade(Resource):
    @student_ns.expect(grade_model)
    @student_ns.doc(description =
                    '''
                        This endpoint is available for only the 
                        admin to add grades for a student
                    ''',
                    params = {"student_id": "The student's id"}
                    )
    @admin_required()
    def post(self): # /api/student/1/grades
        '''
        Add grades for a student
        '''

        student_id = request.json['student_id']
        course_id = request.json['course_id']
        score_value = request.json['score']

        # check if student exists
        student = Student.get_by_id(student_id)
        course = Course.get_by_id(course_id)

        if not student or not course:
            return {'message': 'Student or course not found'}, HTTPStatus.NOT_FOUND

        # check if student is registered for the course
        get_student = Enrollment.get_student_by_course(student_id=student.id, course_id=course.id)
        if not get_student:
            return {'message': 'Student not registered for this course'}, HTTPStatus.NOT_FOUND
        
        # check if grade already exists
        score = Grade.query.filter_by(student_id=student_id, course_id=course_id).first()
        grade = get_grade(score_value)
        if score:
            score.score = score_value
            score.grade = grade
        
        else:
            score = Grade(
                student_id = student_id,
                course_id = course_id,
                score = score_value,
                grade = grade
            )

        score.save()

        student_grade_details = {}
        student_grade_details['student_id'] = score.student_id
        student_grade_details['course_id'] = score.course_id
        student_grade_details['first_name'] = student.first_name
        student_grade_details['last_name'] = student.last_name
        student_grade_details['registration_id'] = student.registration_id
        student_grade_details['course_name'] = course.name
        student_grade_details['course_code'] = course.course_code
        student_grade_details['teacher'] = course.teacher
        student_grade_details['grade'] = score.grade
        student_grade_details['score'] = score.score

        return student_grade_details, HTTPStatus.CREATED


@student_ns.route('/grade/<int:grade_id>')
class UpdateGrade(Resource):
    @student_ns.expect(grade_update_model)
    @student_ns.doc(description =
                    '''
                        This endpoint is available for only the 
                        admin to update a student grade
                    ''',
                    params = {"grade_id": "The grade's id"}
                    )
    @admin_required()
    def put(self, grade_id):
        '''
        Update a student grade
        '''

        score_value = request.json['score']

        # check if grade exists
        score = Grade.query.filter_by(id=grade_id).first()
        if not score:
            return {'message': 'Grade not found'}, HTTPStatus.NOT_FOUND

        # update the grade
        score.score = score_value
        score.grade = get_grade(score_value)
        score.update()

        student_grade_details = {}
        student_grade_details['student_id'] = score.student_id
        student_grade_details['course_id'] = score.course_id
        student_grade_details['grade'] = score.grade
        student_grade_details['score'] = score.score

        return student_grade_details, HTTPStatus.OK

@student_ns.route('/<int:student_id>/gpa')
class GetStudentCGPA(Resource):
    @student_ns.doc(description =
                    '''
                        This endpoint is available for all authenticated 
                        users(Admin and Students) to get a student CGPA.
                    ''',
                    params = {"student_id": "The student's id"}
                    )
    @jwt_required()
    def get(self, student_id):
        '''
            Calculate a student's CGPA
        '''
        if not is_admin_or_student(student_id):
            return {'message': 'You are not authorized view this page'}, HTTPStatus.UNAUTHORIZED

        # check if student exists
        student = Student.get_by_id(student_id)
        if not student:
            return {'message': 'Student not found'}, HTTPStatus.NOT_FOUND
        
        # get the student grades
        courses = Enrollment.get_courses_by_student_id(student_id)

        total_weighted_gpa = 0
        total_credit_unit = 0

        for course in courses:

            #check if the course has a grade
            grade_exist = Grade.query.filter_by(student_id = student_id, course_id = course.id).first()
            if grade_exist:
                grade = grade_exist.grade

                # calculate the weighted gpa
                gpa = convert_grade_to_gpa(grade)
                weighted_gpa = gpa * course.credit_unit
                total_weighted_gpa += weighted_gpa
                total_credit_unit += course.credit_unit

            gpa = total_weighted_gpa / total_credit_unit

            # cgpa = gpa / len(courses)
            round_gpa = float("{:.2f}".format(gpa))

            return f"{student.first_name} {student.last_name}'s CGPA is {round_gpa}", HTTPStatus.OK

