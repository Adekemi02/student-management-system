from ..utils import db
from .users import User
from .courses import Course
from datetime import datetime


class Student(User):
    __tablename__ = 'student'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    registration_id = db.Column(db.String(80), unique=True, nullable=False)
    course = db.relationship('Course', secondary='enrollment')

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }


    def __repr__(self):
        return f"Student(' {self.registration_id}')"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()


class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Enrollment(' {self.id}')"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    
    @classmethod
    def get_courses_by_student_id(cls, student_id):
        courses = Course.query.join(Enrollment).join(Student).filter(Student.id == student_id).all()
        return courses

    @classmethod
    def get_students_by_course_id(cls, course_id):
        students = Student.query.join(Enrollment).join(Course).filter(Course.id == course_id).all()
        return students
    
    @classmethod
    def get_student_by_course(cls, student_id, course_id):
        return cls.query.filter_by(student_id=student_id, course_id=course_id).first()
    