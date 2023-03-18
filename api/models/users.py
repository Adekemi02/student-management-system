from ..utils import db
from datetime import datetime



# class GoogleForm(db.Model):
#     __tablename__ = 'google_forms'
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(80), unique=True, nullable=False)
#     last_name = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     phone = db.Column(db.String(80), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

#     __mapper_args__ = {
#         'polymorphic_identity': 'google_form',
#     }


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    # confirmed_on = db.Column(db.DateTime, nullable=True)

    user_type = db.Column(db.String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    def __repr__(self):
        return f"User(' {self.name}')"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # get user details from google form
    # @classmethod
    # def get_user_details(cls, id):
    #     details = GoogleForm.query.join(User).filter(User.id == id).first()
    #     return details


    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    
    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    

class Admin(User):
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

