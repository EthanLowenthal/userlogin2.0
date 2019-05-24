from flask import Flask, flash, redirect, render_template, request, session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from tabledef import Team
import random
import json
import re

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time

admins = ['95024349']

chrome_options = Options()
chrome_options.add_argument("--headless")

userEngine = create_engine('sqlite:///users.db', echo=True)
userSession = sessionmaker(bind=userEngine)

teamEngine = create_engine('sqlite:///teams.db', echo=True)
teamSession = sessionmaker(bind=teamEngine)

app = Flask(__name__)
app.secret_key = str(random.random())

@app.route("/logout")
def logout():
	session['logged_in'] = False
	session['user'] = None
	return redirect('login')

@app.route('/', methods=["GET"])
def home():
	if not session.get('logged_in'):
		return redirect('login')
	else:
		return render_template('index.html', name=session.get('user')[1])

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

def try_login(uname, password):
	driver = webdriver.Chrome(chrome_options=chrome_options)
	driver.get("https://id.pausd.org/")

	WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'identification')))
	loginid = driver.find_element_by_id('identification')
	loginid.send_keys(uname)
	driver.find_element_by_id('authn-go-button').click()

	time.sleep(0.3)
	try:
		driver.find_element_by_class_name('error-message')
		return None, False
	except NoSuchElementException:
		pass

	WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//*[@type="password"]')))
	passwd = driver.find_element_by_xpath('//*[@type="password"]')
	passwd.send_keys(password)
	driver.find_element_by_id('authn-go-button').click()

	time.sleep(0.3)
	try:
		driver.find_element_by_class_name('error-message')
		return None, False
	except NoSuchElementException:
		pass

	WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, 'cs-logo-container')))
	driver.find_element_by_xpath('//*[@title="IC Portal"]').click()
	time.sleep(1)
	driver.switch_to.window(driver.window_handles[1])

	WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'frameDetail')))
	iframe = driver.find_element_by_id("frameDetail")
	driver.switch_to.frame(iframe)
	WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//*[@id="userName"]/span')))
	name = driver.find_element_by_xpath('//*[@id="userName"]')
	name = name.get_attribute('innerHTML').replace('<span class="welcome">Welcome</span>', '')
	return name, True

@app.route('/login', methods=['GET'])
def login():

	if session.get('logged_in'):
		return redirect('')
	return render_template('login.html')

@app.route('/check', methods=['POST'])
def check():

	POST_USERNAME = str(request.form['username'])
	POST_PASSWORD = str(request.form['password'])

	name, valid = try_login(POST_USERNAME, POST_PASSWORD)

	if valid:
		session['logged_in'] = True
		isAdmin = POST_USERNAME in admins
		session['user'] = (POST_USERNAME, name, None, isAdmin)

	else:
		flash('wrong')

	return redirect('')

if __name__ == "__main__":
	app.run(debug=True)