from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy #sqlalchemy
from flask_bcrypt import Bcrypt
from bankapp import app, db, bcrypt
from bankapp.customers import customers

@app.route("/")
def home():
	return render_template("index.html", content="Testing")

# Test method
@app.route("/view")
def view():
	return render_template("view.html", values=customers.query.all())


@app.route("/login", methods=["POST", "GET"])
def login():
	# If post (user clicks button), get data for nm and redirect to that url
	if request.method == "POST":
		# makes the session lase for the permenant_session_lifetime
		session.permenant = True
		user_name = request.form["nm"]
		user_password = request.form["pw"]

		## MOVEDadd the user name to session data
		##session["user"] = user_name

		# check if user is in database
		found_customer = customers.query.filter_by(name=user_name).first()
		if found_customer:
			if bcrypt.check_password_hash(found_customer.password, user_password):
				session["password"] = found_customer.password
				# add the user name to session data
				session["user"] = user_name
			else:
				flash("Login unsuccessful, invalid password")
				return redirect(url_for("login"))
		else:
			flash("Login unsuccessful, invalid username")
			#return redirect(url_for("login"))
			#TODO REMOVE next four lines
			adding_password = bcrypt.generate_password_hash(user_password).decode("utf-8")
			usr = customers(user_name, adding_password)
			db.session.add(usr)
			db.session.commit()


		# pass to user method using data from session
		flash("Login successful!")
		return redirect(url_for("user"))
	else:
		if "user" in session:
			flash("Already logged in")
			return redirect(url_for("user"))
		
		return render_template("login.html")

@app.route("/user", methods=["POST", "GET"])
def user():
	username = None
	if "user" in session:
		user = session["user"]

		if request.method == "POST":
			username = request.form["username"]
			session["username"] = username
			found_customer = customers.query.filter_by(name=user).first()
			found_customer.username = username
			db.session.commit()
			flash("Username was saved!")
		else:
			if "username" in session:
				username = session["username"]

		return render_template("customer.html", username=username)
	else:
		flash("You are not logged in")
		return redirect(url_for("login"))


@app.route("/logout")
def logout():
	flash("You are logged out")
	session.pop("user", None)
	session.pop("password", None)
	return redirect(url_for("login"))