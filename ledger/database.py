import sqlalchemy
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
engine = sqlalchemy.create_engine('sqlite:////tmp/test.db')
