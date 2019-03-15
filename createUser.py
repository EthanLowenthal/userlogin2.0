from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from tabledef import User, Team
import random
import string

# engine = create_engine('sqlite:///users.db', echo=True)
#
# Session = sessionmaker(bind=engine)
# s = Session()
#
# admin = User('admin', '', isAdmin=True)
# s.add(admin)
#
# dave = User('dave', '')
# s.add(dave)
#
# s.commit()
# s.commit()


engine = create_engine('sqlite:///teams.db', echo=True)

Session = sessionmaker(bind=engine)
s = Session()
team = Team(8, 'swervethis is a super long comment blah blach blah', random.randint(0, 10), random.randint(0, 3), random.randint(0, 3),
			random.randint(0, 3), random.randint(0, 10), random.randint(0, 10), 'this is a super long comment blah blach blah this is a super long comment blah blach blah this is a super long comment blah blach blah this is a super long comment blah blach blah this is a super long comment blah blach blah this is a super long comment blah blach blah this is a super long comment blah blach blah')
s.add(team)
# for i in range(10):
# 	team = Team(random.randint(0,100), 'swerve', random.randint(0,10), random.randint(0,3), random.randint(0,3), random.randint(0,3), random.randint(0,10), random.randint(0,10), 'comment')
#
# 	# team = Team(random.randint(0,100), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)), random.randint(0,10), random.randint(0,3), random.randint(0,3), random.randint(0,3), random.randint(0,10), random.randint(0,10), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15)))
# 	s.add(team)



s.commit()
s.commit()