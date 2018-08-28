from flask import Flask, flash, redirect, render_template, request, session, abort, Response
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from tabledef import User
from subprocess import call
import werkzeug
from werkzeug.security import check_password_hash, generate_password_hash
import cv2
import time
import random

engine = create_engine('sqlite:///users.db', echo=True)
cap = cv2.VideoCapture(0)
app = Flask(__name__)
app.secret_key = str(random.random())
# app.config['SESSION_TYPE'] = 'filesystem'

 
@app.route('/', methods=["GET"])
def home():
	if not session.get('logged_in'):
		return redirect('login')
	else:
		return render_template('index.html', name=session.get('user')[1], isAdmin=session.get('user')[3])
	
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
	try:
		if request.form['isAdmin'] == 'on':
			isAdmin = True
	except werkzeug.exceptions.BadRequestKeyError:
		isAdmin = False
		
	user = User(request.form['username'], request.form['password'],isAdmin=isAdmin)
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
 
@app.route("/logout")
def logout():
	session['logged_in'] = False
	session['user'] = None
	return redirect('login')

if __name__ == "__main__":
	app.run()