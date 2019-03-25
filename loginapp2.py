from flask import Flask, flash, redirect, render_template, request, session, Response
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from tabledef import User, Team
from werkzeug.security import check_password_hash, generate_password_hash
import random
import json
import re

userEngine = create_engine('sqlite:///users.db', echo=True)
userSession = sessionmaker(bind=userEngine)

teamEngine = create_engine('sqlite:///teams.db', echo=True)
teamSession = sessionmaker(bind=teamEngine)

app = Flask(__name__)
app.secret_key = str(random.random())


@app.route('/', methods=["GET"])
def home():
	if not session.get('logged_in'):
		return redirect('login')
	else:
		return render_template('index.html', name=session.get('user')[1], isAdmin=session.get('user')[3])

@app.route('/userExists', methods=["POST"])
def user():
	s = userSession()
	query = s.query(User).filter(User.username.in_([request.form['username']]))
	result = query.first()
	s.close()
	if result:
		return Response('true')
	return Response('false')

@app.route('/accounts', methods=["GET"])
@app.route('/accounts/', methods=["GET"])
def manage():
	if not session.get('logged_in'):
		return redirect('login')
	if not session.get('user')[3]:
		return redirect('')
	users = userEngine.execute('SELECT * FROM users')
	u = []
	for _r in users:
		u.append(_r)
	return render_template("manage.html", name=session.get('user')[1], isAdmin=session.get('user')[3], users=u)

@app.route('/scout', methods=["GET"])
@app.route('/scout/', methods=["GET"])
def scout():
	if not session.get('logged_in'):
		return redirect('login')

	return render_template("scout.html", name=session.get('user')[1], isAdmin=session.get('user')[3])

@app.route('/results/<string:team>/data', methods=["GET"])
@app.route('/results/<string:team>/data/', methods=["GET"])
def getTeamData(team):
	if re.search("frc[0-9]+", team):
		try:
			result = teamEngine.execute('SELECT * FROM teams WHERE number = ' + str(team.replace("frc", "")))
			r = {}
			for row in result:
				r[row[0]] = list(row)

			return json.dumps(r)
		except:
			return "Team Not Found"
	else:
		flash("Invalid Team Key")
		return "Team Not Found"

@app.route('/results/<string:team>', methods=["GET"])
@app.route('/results/<string:team>/', methods=["GET"])
def getTeam(team):
	if not re.search("frc[0-9]+", team):
		flash("Invalid Team Key")
		return redirect("search")
	return render_template("teamVeiwer.html", team=team, name=session.get('user')[1], isAdmin=session.get('user')[3])

@app.route('/results', methods=["GET"])
@app.route('/results/', methods=["GET"])
def results():
	if not session.get('logged_in'):
		return redirect('login')
	try:
		teams = teamEngine.execute('SELECT * FROM teams')
		t = {}
		for r in teams:
			if r[1] not in t:
				t[r[1]] = [r[0], 0]
			t[r[1]][1] += 1
	except:
		teams = {}

	return render_template("results.html", name=session.get('user')[1], teams=t, isAdmin=session.get('user')[3])

@app.route('/search', methods=["GET"])
@app.route('/search/', methods=["GET"])
def search():
	return render_template("search.html", name=session.get('user')[1], isAdmin=session.get('user')[3])

@app.route('/results/delete', methods=['POST'])
def deleteResult():
	if not session.get('logged_in'):
		return redirect('login')
	s = teamSession()
	s.query(Team).filter_by(id=request.form['id']).delete()
	s.commit()
	s.commit()
	s.close()
	flash('Entry "{}" deleted!'.format(request.form['id']))
	return redirect('results')

@app.route('/results/add', methods=['POST'])
def addResult():
	s = teamSession()
	team = Team(request.form["number"],
				request.form["drivetrain"] if request.form["drivetrain"] != "Other" else request.form[
					"drivetrainOther"],
				request.form["speed"], request.form["hatch"], request.form["climb"],
				request.form["ball"], request.form["driver"], request.form["auton"], request.form["comments"])
	s.add(team)
	s.commit()
	s.commit()
	s.close()
	flash("Data saved!")
	return redirect('scout')


@app.route('/accounts/update', methods=['POST'])
def update():
	if not session.get('logged_in'):
		return redirect('login')
	field = str(request.form['field'])
	value = str(request.form[field])
	user_id = request.form['id']
	s = userSession()
	if field == 'password':
		s.query(User).filter_by(id=user_id).update({field: generate_password_hash(value)})
	else:
		s.query(User).filter_by(id=user_id).update({field: value})
	s.commit()
	s.commit()
	s.close()
	if user_id == str(session.get('user')[0]):
		user = userEngine.execute('SELECT * FROM users WHERE id = ?', (user_id))
		for p in user: session['user'] = tuple(p)
	flash(field.capitalize()+' updated!')
	return redirect('accounts')

@app.route('/accounts/addAdmin', methods=['POST'])
def addAdmin():
	if not session.get('logged_in'):
		return redirect('login')
	if not session.get('user')[3]:
		return redirect('')
	user_id = request.form['id']

	s = userSession()
	s.query(User).filter_by(id=user_id).update({"isAdmin": True})
	s.commit()
	s.commit()
	s.close()
	flash('Admin privileges added!')
	if user_id == str(session.get('user')[0]):
		user = userEngine.execute('SELECT * FROM users WHERE id = ?', (user_id))
		for p in user: session['user'] = tuple(p)
	return redirect('accounts')


@app.route('/accounts/revokeAdmin', methods=['POST'])
def revokeAdmin():
	user_id = request.form['id']

	s = userSession()
	s.query(User).filter_by(id=user_id).update({"isAdmin": False})
	s.commit()
	s.commit()
	s.close()
	flash('Admin privileges revoked!')
	if user_id == str(session.get('user')[0]):
		user = userEngine.execute('SELECT * FROM users WHERE id = ?', (user_id))
		for p in user: session['user'] = tuple(p)
		return redirect('')

	return redirect('accounts')

@app.route('/matches', methods=['GET'])
@app.route('/matches/<string:match>', methods=['GET'])
@app.route('/matches/<string:match>/', methods=['GET'])
def matches(match=""):
	if not session.get('logged_in'):
		return redirect('login')
	if re.search("[0-9]{4}[a-zA-Z]+", match):
		return render_template('matches.html', match=match, name=session.get('user')[1], isAdmin=session.get('user')[3])
	else:
		flash("Invalid Match Key")
		return redirect("search")



@app.route('/accounts/delete', methods=['POST'])
def deleteAccount():
	if not session.get('logged_in'):
		return redirect('login')
	user_id = request.form['id']
	username = request.form['name']

	s = userSession()
	s.query(User).filter_by(id=user_id).delete()
	s.commit()
	s.commit()
	s.close()
	flash('Account "{}" deleted!'.format(username))
	if username == session.get('user')[1]:
		return redirect('logout')
	return redirect('accounts')

@app.route('/accounts/add', methods=['POST'])
def add():
	s = userSession()
	try:
		user = User(request.form['username'], request.form['password'],isAdmin=True if request.form['isAdmin'] == 'on' else False)
	except:
		user = User(request.form['username'], request.form['password'],
					isAdmin=False)
	s.add(user)
	s.commit()
	s.commit()
	s.close()
	flash('Account "{}" created!'.format(request.form['username']))
	return redirect('accounts')



@app.route('/login', methods=['GET'])
def login():

	if session.get('logged_in'):
		return redirect('')
	return render_template('login.html')

@app.route('/check', methods=['POST'])
def check():

	POST_USERNAME = str(request.form['username'])
	POST_PASSWORD = str(request.form['password'])
	s = userSession()

	query = s.query(User).filter(User.username.in_([POST_USERNAME]))
	result = query.first()
	if result is not None:
		if check_password_hash(result.password, POST_PASSWORD):
			session['logged_in'] = True
			user = userEngine.execute('SELECT * FROM users WHERE username = ?', (POST_USERNAME))
			for p in user: session['user'] = tuple(p)
		else:
			flash('wrong')
	else:
			flash('wrong')
	s.close()
	return redirect('')

#TODO: check to see if we really need to send a list of users
@app.route("/register", methods=["GET"])
def register():
	users = userEngine.execute('SELECT * FROM users')
	u = []
	for _r in users:
		u.append(_r)
	return render_template('register.html', users=u)
 
@app.route("/logout")
def logout():
	session['logged_in'] = False
	session['user'] = None
	return redirect('login')

if __name__ == "__main__":
	app.run(debug=True)