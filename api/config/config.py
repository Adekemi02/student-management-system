import os
from decouple import config
from datetime import timedelta
import re


BASE_DIR = os.path.dirname(os.path.realpath(__file__))


database_name = 'student_db'

default_uri = "postgres://{}:{}@{}/{}".format(
    'postgres', 'password', 'localhost:5432', database_name)
    

uri = "postgres://gbclhpmmalhfuk:c5a1a8c5c7497010b214de84d7cf4ba77fcad62bbba6254017a846c5cbcc832c@ec2-3-93-160-246.compute-1.amazonaws.com:5432/d1rhhummufuk8r"
if uri and uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)


class Config:
    SECRET_KEY = config("SECRET_KEY", "secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_SECRET_KEY = config("JWT_SECRET_KEY")


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///"+os.path.join(BASE_DIR, "db.sqlite3")


class TestConfig(Config):
    TESTTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class ProdConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = uri
    DEBUG = config('DEBUG', False, cast=bool)
    


config_dict = {
    "dev": DevConfig,
    "test": TestConfig,
    "prod": ProdConfig,
}