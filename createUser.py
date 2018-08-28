from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from tabledef import User

engine = create_engine('sqlite:///users.db', echo=True)

Session = sessionmaker(bind=engine)
s = Session()

admin = User('admin', '', isAdmin=True)
s.add(admin)

dave = User('dave', '')
s.add(dave)

s.commit()
s.commit()