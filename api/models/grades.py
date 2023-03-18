from ..utils import db
from datetime import datetime


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(10), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    gpa = db.Column(db.Float, nullable=True, default=0.0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    def __repr__(self):
        return f"Grade(' {self.grade}')"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()