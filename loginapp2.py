from flask import Flask, flash, redirect, render_template, request, session, abort, Response
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from tabledef import User
from subprocess import call
import werkzeug
from werkzeug.security import check_password_hash, generate_password_hash
import random
import jinja2

engine = create_engine('sqlite:///users.db', echo=True)
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
	Session = sessionmaker(bind=engine)
	print(request.form)
	s = Session()
	query = s.query(User).filter(User.username.in_([request.form['username']]))
	result = query.first()
	if result:
		return Response('true')
	return Response('false')

@app.route('/accounts', methods=["GET"])
def manage():
	if not session.get('logged_in'):
		return redirect('login')
	if not session.get('user')[3]:
		return redirect('')
	users = engine.execute('SELECT * FROM users')
	u = []
	for _r in users:
		u.append(_r)
	return render_template("manage.html", name=session.get('user')[1], users=u)

@app.route('/accounts/update', methods=['POST'])
def update():
	field = str(request.form['field'])
	value = str(request.form[field])
	user_id = request.form['id']

	Session = sessionmaker(bind=engine)
	s = Session()
	if field == 'password':
		s.query(User).filter_by(id=user_id).update({field: generate_password_hash(value)})
	else:
		s.query(User).filter_by(id=user_id).update({field: value})
	s.commit()
	s.commit()
	if user_id == str(session.get('user')[0]):
		user = engine.execute('SELECT * FROM users WHERE id = ?', (user_id))
		for p in user: session['user'] = tuple(p)
	flash(field.capitalize()+' updated!')
	return redirect('accounts')

@app.route('/accounts/addAdmin', methods=['POST'])
def addAdmin():
	user_id = request.form['id']

	Session = sessionmaker(bind=engine)
	s = Session()
	s.query(User).filter_by(id=user_id).update({"isAdmin": True})
	s.commit()
	s.commit()
	flash('Admin privileges added!')
	if user_id == str(session.get('user')[0]):
		user = engine.execute('SELECT * FROM users WHERE id = ?', (user_id))
		for p in user: session['user'] = tuple(p)
	return redirect('accounts')

@app.route('/accounts/revokeAdmin', methods=['POST'])
def revokeAdmin():
	user_id = request.form['id']

	Session = sessionmaker(bind=engine)
	s = Session()
	s.query(User).filter_by(id=user_id).update({"isAdmin": False})
	s.commit()
	s.commit()
	flash('Admin privileges revoked!')
	if user_id == str(session.get('user')[0]):
		user = engine.execute('SELECT * FROM users WHERE id = ?', (user_id))
		for p in user: session['user'] = tuple(p)
		return redirect('')

	return redirect('accounts')

@app.route('/accounts/delete', methods=['POST'])
def delete():
	user_id = request.form['id']
	username = request.form['name']

	Session = sessionmaker(bind=engine)
	s = Session()
	s.query(User).filter_by(id=user_id).delete()
	s.commit()
	s.commit()
	flash('Account "{}" deleted!'.format(username))
	if username == session.get('user')[1]:
		return redirect('logout')
	return redirect('accounts')

@app.route('/accounts/add', methods=['POST'])
def add():
	Session = sessionmaker(bind=engine)
	s = Session()
	user = User(request.form['username'], request.form['password'],isAdmin=True if request.form['isAdmin'] == 'on' else False)
	s.add(user)
	s.commit()
	s.commit()
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
 
	Session = sessionmaker(bind=engine)
	s = Session()
	query = s.query(User).filter(User.username.in_([POST_USERNAME]))
	result = query.first()
	if result is not None:
		if check_password_hash(result.password, POST_PASSWORD):
			session['logged_in'] = True
			user = engine.execute('SELECT * FROM users WHERE username = ?', (POST_USERNAME))
			for p in user: session['user'] = tuple(p)
		else:
			flash('wrong')
	else:
		flash('wrong')

	return redirect('')

@app.route("/register", methods=["GET"])
def register():
	users = engine.execute('SELECT * FROM users')
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