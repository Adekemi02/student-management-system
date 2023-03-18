from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData


# convention = {
#     "ix": 'ix_%(column_0_label)s',
#     "uq": "uq_%(table_name)s_%(column_0_name)s",
#     "ck": "ck_%(table_name)s_%(constraint_name)s",
#     "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
#     "pk": "pk_%(table_name)s"
# }

# metadata = MetaData(naming_convention=convention)
# db = SQLAlchemy(metadata=metadata)


db = SQLAlchemy()





#  Calculate GPA
# def calculate_gpa(registration_id):
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
#         total_grade_point += enrollment.course.credit_unit * get_grade(grade_point)
#         total_credit_unit += enrollment.course.credit_unit
    
#     gpa = total_grade_point / total_credit_unit
    
#     return gpa


def get_grade_point(score):
    if score is None:
        return 'F'
    elif score >= 70:
        return 'A'
    elif score >= 60:
        return 'B'
    elif score >= 50:
        return 'C'
    elif score >= 40:
        return 'D'
    elif score >= 45:
        return 'E'
    else:
        return 'F'