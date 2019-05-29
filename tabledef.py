import datetime
from sqlalchemy import create_engine
from sqlalchemy import Column, DateTime, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash
 
userEngine = create_engine('sqlite:///users.db', echo=True)
userBase = declarative_base()

class User(userBase):
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    isAdmin = Column(Boolean)

    def __init__(self, username, password, isAdmin=False):
        self.username = username
        self.password = generate_password_hash(password)
        self.isAdmin = isAdmin
 
userBase.metadata.create_all(userEngine)

teamEngine = create_engine('sqlite:///teams.db', echo=True)
teamBase = declarative_base()

class Team(teamBase):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    drivetrain = Column(String)
    driveSpeed = Column(Integer)
    hatch = Column(Integer)
    climb = Column(Integer)
    ball = Column(Integer)
    driverLevel = Column(Integer)
    autonomous = Column(Integer)
    notes = Column(String)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    match = Column(Integer)
    event = Column(String)
    eventID = Column(String)

    def __init__(self, number, drivetrain, driveSpeed, hatch, climb, ball, driverLevel, autonomous, notes, match, event, eventID):
        self.number = number
        self.drivetrain = drivetrain
        self.driveSpeed = driveSpeed
        self.hatch = hatch
        self.climb = climb
        self.ball = ball
        self.driverLevel = driverLevel
        self.autonomous = autonomous
        self.notes = notes
        self.match = match
        self.event = event
        self.eventID = eventID


# create tables
teamBase.metadata.create_all(teamEngine)



