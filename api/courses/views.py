from flask_restx import Resource, fields, Namespace
from flask import request
from http import HTTPStatus
from ..admin.admin import admin_required
from ..models.courses import Course
from ..models.students import Enrollment, Student
from flask_jwt_extended import jwt_required, get_jwt_identity


course_ns = Namespace('course', description='Course related operations')

course_model = course_ns.model(
    'Course', {
        'id': fields.Integer(required=True, description='The course identifier'),
        'name': fields.String(required=True, description='The course name'),
        'course_code': fields.String(required=True, description='The course code'),
        'credit_unit': fields.Integer(required=True, description='The course credit unit'),
        'teacher': fields.String(required=True, description='The course teacher'),
    }
)

course_registration_model = course_ns.model(
    'CourseRegistration', {
        'course_id': fields.Integer(description='The course ID'),
    }
)

student_enrollment_model = course_ns.model(
    'StudentEnrollment', {
        'student_id': fields.Integer(description='The student ID'),
        'course_id': fields.Integer(description='The course ID'),
    }
)

@course_ns.route('')    # /api/course  post, get courses
class GetCreateAllCourses(Resource):
    @course_ns.expect(course_model)
    @course_ns.marshal_list_with(course_model)
    @course_ns.doc(description =
                    '''
                        This endpoint is used to create a new course.
                        Only the admin user can create a new course
                    '''
                    )
    @admin_required()
    def post(self):
        '''
        Create a new course
        '''
        
        data = course_ns.payload

        course  = Course.get_by_course_code(data['course_code'])
        # check if course already exists
        if course:
            return {'message': 'Course already exists'}, HTTPStatus.BAD_REQUEST

        new_course = Course(
            name = data['name'],
            course_code = data['course_code'],
            credit_unit = data['credit_unit'],
            teacher = data['teacher']
        )

        new_course.save()

        return new_course, HTTPStatus.CREATED
    
    @course_ns.marshal_list_with(course_model)
    @course_ns.doc(description =
                    '''
                        This endpoint is used to get all courses.
                        This is available to all authenticated users
                    '''
                    )
    @jwt_required()
    def get(self):
        '''
            Get All Courses
        '''

        courses = Course.query.all()

        return courses, HTTPStatus.OK
    
    
@course_ns.route('/<int:course_id>')    # /api/course/<course_id>  get, update, delete a course
class GetUpdateDeleteCourse(Resource):
    @course_ns.marshal_with(course_model)
    @course_ns.doc(description =
                    '''
                        This endpoint is used to get a specific course.
                        This is available to all authenticated users
                    ''',
                    params={
                        'course_id': 'The course identifier'}
                    )
    @jwt_required()
    def get(self, course_id):
        '''
            Get a course
        '''

        course = Course.get_by_id(course_id)

        if course is None:
            return {'message': 'Course not found'}, HTTPStatus.NOT_FOUND

        return course, HTTPStatus.OK
    

    @course_ns.expect(course_model)
    @course_ns.marshal_with(course_model)
    @course_ns.doc(description =
                    '''
                        This endpoint is used to update a specific course.
                        Only the admin user can update a course
                    '''
                    )
    @admin_required()
    def put(self, course_id):
        '''
            Update a course
        '''

        data = course_ns.payload

        course = Course.get_by_id(course_id)

        if course is None:
            return {'message': 'Course not found'}, HTTPStatus.NOT_FOUND

        course.name = data['name']
        course.course_code = data['course_code']
        course.credit_unit = data['credit_unit']
        course.teacher = data['teacher']

        course.update()

        return course, HTTPStatus.OK


    @course_ns.doc(description =
                    '''
                        This endpoint is used to delete a specific course.
                        Only the admin user can delete a course
                    '''
                    )
    @admin_required()
    def delete(self, course_id):
        '''
            Delete a course
        '''

        course = Course.get_by_id(course_id)

        if course is None:
            return {'message': 'Course not found'}, HTTPStatus.NOT_FOUND

        course.delete()

        return {'message': 'Course deleted successfully'}, HTTPStatus.OK
    

@course_ns.route('/<int:course_id>/students')    # /api/course/<course_id>/students  get all students registered for a course    
class GetStudentsByCourse(Resource):
    # @course_ns.marshal_list_with(student_enrollment_model)
    @course_ns.doc(description =
                    '''
                        This endpoint is used to get all students registered for a specific course.
                        Only the admin user can get all students registered for a course
                    '''
                    )
    @admin_required()
    def get(self, course_id):
        '''
        Admin Get All Students Registered for a Course
        '''

        enrolled_students = Enrollment.get_students_by_course_id(course_id)

        if not enrolled_students:
            return {'message': 'No student registered for this course'}, HTTPStatus.NOT_FOUND

        student_details = []

        for students in enrolled_students:
            student_record = {}
            # student_record['course_id'] = students.course_id
            student_record['first_name'] = students.first_name
            student_record['last_name'] = students.last_name
            student_record['registration_id'] = students.registration_id

            student_details.append(student_record)

        return student_details, HTTPStatus.OK
    

@course_ns.route('/course/enroll')   # /api/course/course student register for a course
class StudentRegisterCourse(Resource):
    @course_ns.expect(course_registration_model)
    # @course_ns.marshal_with(student_enrollment_model)
    @course_ns.doc(description =
                    '''
                        This endpoint is used to register a student for a specific course.
                        This is available to all authenticated users
                    '''
                    )
    @jwt_required()
    def post(self):
        '''
        Student Enroll for a Course
        '''

        current_user = get_jwt_identity()

        data = request.get_json()

        student = Student.get_by_id(id=current_user)

        course = Course.get_by_id(id=data.get('course_id'))

        if course:
            #check if student is already registered for the course
            get_student = Enrollment.get_student_by_course(student_id=student.id, course_id=course.id)

            if get_student:
                return {'message': 'Student already enrolled for this course'}, HTTPStatus.BAD_REQUEST
            

            enroll_student = Enrollment(
                student_id = student.id,
                course_id = course.id
            )

            try:

                enroll_student.save()
                return {"message": "Course registered successfully"}, HTTPStatus.CREATED
            except:
                return {"message": "An error occurred while registering course"}, HTTPStatus.INTERNAL_SERVER_ERROR
        
        return {'message': 'Course not found'}, HTTPStatus.NOT_FOUND

@course_ns.route('/course/unenroll')   # /api/course/course student unregister for a course
class StudentUnregisterCourse(Resource):

    @course_ns.expect(course_registration_model)
    @course_ns.doc(description =
                    '''
                        This endpoint is used to unregister a student for a course.
                        This is available to all authenticated users
                        ''')
    @jwt_required()
    def delete(self):
        '''
        Student Unenroll for a Course
        '''

        current_user = get_jwt_identity()

        data = request.get_json()

        student = Student.get_by_id(id=current_user)

        course = Course.get_by_id(id=data.get('course_id'))
        if course:
            #check if student is already registered for the course
            get_student = Enrollment.get_student_by_course(student_id=student.id, course_id=course.id)

            if get_student:
                get_student.delete()
                return {'message': 'Course unregistered successfully'}, HTTPStatus.OK

            return {'message': 'Student not registered for this course'}, HTTPStatus.BAD_REQUEST
    
        return {'message': 'Course not found'}, HTTPStatus.NOT_FOUND 
    

    # /api/course/<course_id>/students  register a student for a course
# @course_ns.route('/<int:course_id>/student/<int:student_id>')    # /api/course/<course_id>/students  register a student for a course
# class AdminRegisterStudent(Resource):
#     # @course_ns.expect(student_enrollment_model)
#     # @course_ns.marshal_list_with(student_enrollment_model)
#     @course_ns.doc(description =
#                     '''
#                         This endpoint is used to register a student for a specific course.
#                         Only the admin user can register a student for a course
#                     '''
#                     )
#     @admin_required()
#     def post(self, course_id, student_id):
#         '''
#         Admin Register a Student for a Course
#         '''
        
#         course = Course.get_by_id(course_id)

#         student = Student.get_by_id(student_id)

#         student_in_course = Enrollment.get_student_by_course(student_id, course_id)

#         if student_in_course:
#             return {'message': 'Student already registered for this course'}, HTTPStatus.BAD_REQUEST
        
#         enroll_student = Enrollment(
#             student_id = student_id,
#             course_id = course_id
#         )

#         enroll_student.save()

#         return {"message": "Student registered successfully"}, HTTPStatus.CREATED


