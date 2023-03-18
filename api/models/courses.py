from ..utils import db
from datetime import datetime


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    course_code = db.Column(db.String(80), unique=True, nullable=False)
    credit_unit = db.Column(db.Integer, nullable=False)
    teacher = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # enrolled_students = db.relationship('User', secondary='student')

    def __repr__(self):
        return f"Course(' {self.name}')"
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    
    @classmethod
    def get_by_course_code(cls, course_code):
        return cls.query.filter_by(course_code=course_code).first()
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    