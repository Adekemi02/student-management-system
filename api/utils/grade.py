from ..models.students import Student, Enrollment
from flask import jsonify



#  Convert a score to a grade
def get_grade(score):
    if score < 100 and score > 79:
        return 'A'
    elif score < 80 and score > 69:
        return 'B'
    elif score < 70 and score > 59:
        return 'C'
    elif score < 60 and score > 49:
        return 'D'
    elif score < 50 and score > 44:
        return 'E'
    elif score < 45:
        return 'F'
    else:
        return 'F'
    
# Convert a grade to a grade point
def convert_grade_to_gpa(grade):
    if grade == 'A':
        return 5.0
    elif grade == 'B':
        return 4.0
    elif grade == 'C':
        return 3.0
    elif grade == 'D':
        return 2.0
    elif grade == 'E':
        return 1.0
    else:
        return 0.0
    

# def calculate_cgpa(registration_id):
#     student = Student.query.filter_by(registration_id=registration_id).first()
#     if not student:
#         return jsonify({'message': 'Student not found'}), 404
    
#     enrollments = Enrollment.query.filter_by(student_id=student.id).all()
#     if not enrollments:
#         return jsonify({'message': 'Student has not enrolled for any course'}), 404
    
#     total_credit_unit = 0
#     total_grade_point = 0

#     for enrollment in enrollments:
#         grade_point = get_grade_point(enrollment.score)

#         total_grade_point += enrollment.course.credit_unit * grade_point
#         total_credit_unit += enrollment.course.credit_unit
    
#     cgpa = total_grade_point / total_credit_unit
    
#     return cgpa