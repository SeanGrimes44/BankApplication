from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy #sqlalchemy
from flask_bcrypt import Bcrypt
from bankapp import app, db, bcrypt
from bankapp.customers import customers, Account, Transaction
from decimal import Decimal

@app.route("/")
def home():
	return render_template("index.html", content="Testing")


@app.route("/view", methods=["POST", "GET"])
def view():
	if ("user" in session):
		user = session["user"]

		# Go to transaction page
		if request.method == "POST":
			account_to_get = request.form["account_select"]#.get("account_select")
			session["account"]=account_to_get
			return redirect(url_for("view_transactions"))
		else:



			customer_to_view = customers.query.filter_by(name=user).first()
			accounts_to_view = Account.query.filter_by(owner=customer_to_view)
			sorted_accounts = accounts_to_view.order_by(Account.bank_id.asc())
			today = datetime.now()
		#customer_to_view.accounts = customer_to_view.accounts.order_by(Account.bank_id.asc())

		return render_template("view.html", acs=sorted_accounts, day="today")
	return redirect(url_for("login"))

@app.route("/transactions", methods=["POST", "GET"])
def view_transactions():
	if ("account" in session):
		account = session["account"]
		account_number = int(account)
		account_to_view = Account.query.filter_by(bank_id=account_number).first()
		transactions_to_view = Transaction.query.filter_by(receiver=account_to_view)
		sorted_transactions = transactions_to_view.order_by(Transaction.amount.desc())

		#Sorting
		if request.method == "POST":
			sorting_method = request.form["sort_select"]
			if (sorting_method == "1"):
				#Amount (Ascending)
				#account_to_view = Account.query.filter_by(bank_id=account_number).first()
				#transactions_to_view = Transaction.query.filter_by(receiver=account_to_view)
				sorted_transactions = transactions_to_view.order_by(Transaction.amount.asc())
				return render_template("transactions.html", acc=account_to_view, tra=sorted_transactions)
				#return url_for("logout")

			elif (sorting_method == "2"):
				#Amount (Descending)
				#account_to_view = Account.query.filter_by(bank_id=account_number).first()
				#transactions_to_view = Transaction.query.filter_by(receiver=account_to_view)
				sorted_transactions = transactions_to_view.order_by(Transaction.amount.desc())
				return render_template("transactions.html", acc=account_to_view, tra=sorted_transactions)

			elif (sorting_method == "3"):
				#Date (Ascending)
				sorted_transactions = transactions_to_view.order_by(Transaction.date_sent.asc())
				return render_template("transactions.html", acc=account_to_view, tra=sorted_transactions)

			elif (sorting_method == "4"):
				#Date (Descending)
				sorted_transactions = transactions_to_view.order_by(Transaction.date_sent.desc())
				return render_template("transactions.html", acc=account_to_view, tra=sorted_transactions)


		return render_template("transactions.html", acc=account_to_view, tra=sorted_transactions)

	flash("Must select an account to view transactions from.")
	return redirect(url_for("view"))


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
				rec_transaction = Transaction(merchant_id=send_account.bank_id, amount=send_amount_decimal, receiver=rec_account, date_sent=datetime.utcnow())

				send_account.sub_amount(send_amount_decimal)
				send_transaction = Transaction(merchant_id=rec_account.bank_id, amount=-send_amount_decimal, receiver=send_account, date_sent=datetime.utcnow())
				db.session.add(rec_transaction)
				db.session.add(send_transaction)
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
			savings = Account(bank_id=987, amount=13.20, owner=usr, account_type="Savings")

			checking = Account(bank_id=999, amount=14.20, owner=usr, account_type="Checking")
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
	session.pop("account", None)
	return redirect(url_for("login"))