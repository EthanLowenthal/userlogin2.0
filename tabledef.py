from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash
 
engine = create_engine('sqlite:///users.db', echo=True)
Base = declarative_base()
 
########################################################################
class User(Base):
    """"""
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    isAdmin = Column(Boolean)
 
    #----------------------------------------------------------------------
    def __init__(self, username, password, isAdmin=False):
        """"""
        self.username = username
        self.password = generate_password_hash(password)
        self.isAdmin = isAdmin
 
# create tables
Base.metadata.create_all(engine)


