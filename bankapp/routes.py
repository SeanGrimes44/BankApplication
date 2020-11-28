from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy #sqlalchemy
from flask_bcrypt import Bcrypt
from bankapp import app, db, bcrypt
from bankapp.customers import customers, Account
from decimal import Decimal

@app.route("/")
def home():
	return render_template("index.html", content="Testing")

# Test method
@app.route("/view")
def view():
	return render_template("view.html", values=customers.query.all())#, acs=Account.query.all())

@app.route("/transfer", methods=["POST", "GET"])
def transfer():
	if ("user" in session):
		# Make the transaction
		user = session["user"]
		user_account = customers.query.filter_by(name="frank")
		#if (user_account):
		#	flash("User account is found!")

		#POST stuff here
		if request.method == "POST":
			sender_id = request.form["sn"]
			receiver_id = request.form["rc"]
			send_amount = request.form["am"]


			# Checking if sending account is found
			try:
				converted_sender_id = int(sender_id)
				
			except:
				flash("Please enter a valid sending account number")
				return redirect(url_for("transfer"))


			#TODO only filter by user's accounts
			send_account = Account.query.filter_by(bank_id=converted_sender_id).first()
			if (send_account):
				flash("Account found!")
			else:
				flash("Input valid, but account not found.")


		# Checking if recieving account is found
			try:
				converted_receiver_id = int(receiver_id)
				
			except:
				flash("Please enter a valid receiving account number")
				return redirect(url_for("transfer"))


			rec_account = Account.query.filter_by(bank_id=converted_receiver_id).first()
			if (rec_account):
#				minus_string = "12.10"
#				minus = Decimal(minus_string)
#				rec_account.sub_amount(minus)
#				db.session.commit()
				flash("Receiving Account found!")
			else:
				flash("Input valid, but receiving account not found.")

			#Check if amount to send is valid.
			#TODO Check if non-negative.
			send_amount_decimal = Decimal(send_amount)
			if (send_amount_decimal < send_account.amount):
				rec_account.add_amount(send_amount_decimal)
				send_account.sub_amount(send_amount_decimal)
				db.session.commit()



		return render_template("transfer.html")
	else:
		flash("You are not logged in")
		return redirect(url_for("login"))


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
			adding_amount = 15.23
			adding_amount_rounded = round(adding_amount, 2)
			minus = 1.23
			usr = customers(user_name, adding_password, adding_amount_rounded)
			usr.sub_amount(minus)


			db.session.add(usr)
			db.session.commit()

			#TEST create accounts
			savings = Account(bank_id=123, amount=13.20, owner=usr, account_type="Savings")

			checking = Account(bank_id=222, amount=14.20, owner=usr, account_type="Checking")
			db.session.add(savings)
			db.session.add(checking)
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