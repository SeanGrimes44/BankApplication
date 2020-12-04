from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy #sqlalchemy
from flask_bcrypt import Bcrypt
from bankapp import app, db, bcrypt
from bankapp.modules import Customer, Account, Transaction
from decimal import Decimal

# Page to view account.
@app.route("/", methods=["POST", "GET"])
@app.route("/view", methods=["POST", "GET"])
def view():
	if ("user" in session):
		user = session["user"]

		# Go to transaction page
		if request.method == "POST":
			account_to_get = request.form["account_select"]
			session["account"]=account_to_get
			return redirect(url_for("view_transactions"))
		else:

			customer_to_view = Customer.query.filter_by(name=user).first()
			accounts_to_view = Account.query.filter_by(owner=customer_to_view)

		return render_template("view.html", acs=accounts_to_view)
	flash("Please log in to view your accounts.")
	return redirect(url_for("login"))

@app.route("/transactions", methods=["POST", "GET"])
def view_transactions():
	# Check if there is an account to view.
	if ("account" in session):
		# Find the account's transactions in the database.
		account = session["account"]
		account_number = int(account)
		account_to_view = Account.query.filter_by(bank_id=account_number).first()
		transactions_to_view = Transaction.query.filter_by(receiver=account_to_view)
		sorted_transactions = transactions_to_view.order_by(Transaction.amount.desc())

		# Sort the transactions.
		if request.method == "POST":
			sorting_method = request.form["sort_select"]
			if (sorting_method == "1"):
				#Amount (Ascending)
				sorted_transactions = transactions_to_view.order_by(Transaction.amount.asc())
				return render_template("transactions.html", acc=account_to_view, tra=sorted_transactions)

			elif (sorting_method == "2"):
				#Amount (Descending)
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
		user_account = Customer.query.filter_by(name=user)

		# Sending money.
		if request.method == "POST":
			sender_id = request.form["sn"]
			receiver_id = request.form["rc"]
			send_amount = request.form["am"]

			# Checking if sending account is found.
			try:
				converted_sender_id = int(sender_id)
				
			except:
				flash("Please enter a valid account number.")
				return redirect(url_for("transfer"))

			send_account = Account.query.filter_by(bank_id=converted_sender_id).first()

			# Check for the sending account.
			if not send_account:
				flash("Please enter a valid account number.")
				return redirect(url_for("transfer"))

		# Checking if recieving account is found
			try:
				converted_receiver_id = int(receiver_id)
				
			except:
				flash("Please enter a valid receiving account number")
				return redirect(url_for("transfer"))

			# Check if receiving account is found.
			rec_account = Account.query.filter_by(bank_id=converted_receiver_id).first()
			if not rec_account:
				flash("Please enter a valid account number.")
				return redirect(url_for("transfer"))

			#Check if amount to send is valid.
			send_decimal = Decimal(send_amount)
			send_amount_decimal = round(send_decimal, 2)#Decimal(send_amount)

			if (send_amount_decimal < send_account.amount and send_amount_decimal > 0):
				rec_account.add_amount(send_amount_decimal)
				rec_transaction = Transaction(merchant_id=send_account.bank_id, amount=send_amount_decimal, receiver=rec_account, date_sent=datetime.utcnow())

				send_account.sub_amount(send_amount_decimal)
				send_transaction = Transaction(merchant_id=rec_account.bank_id, amount=-send_amount_decimal, receiver=send_account, date_sent=datetime.utcnow())
				db.session.add(rec_transaction)
				db.session.add(send_transaction)
				db.session.commit()
				flash("Transfer successfully made!")
				return redirect(url_for("view"))

			# Invalid amount of money.
			else:
				flash("Invalid amount of money.")
				return redirect(url_for("transfer"))

		return render_template("transfer.html")
	else:
		flash("You are not logged in.")
		return redirect(url_for("login"))

@app.route("/login", methods=["POST", "GET"])
def login():
	# User attempts to log in.
	if request.method == "POST":
		# Get information for the user
		session.permenant = True
		user_name = request.form["nm"]
		user_password = request.form["pw"]

		# check if user is in database.
		found_customer = Customer.query.filter_by(name=user_name).first()
		if found_customer:
			if bcrypt.check_password_hash(found_customer.password, user_password):
				session["password"] = found_customer.password
				# Add the user name to session data.
				session["user"] = user_name
			else:
				flash("Login unsuccessful, invalid password")
				return redirect(url_for("login"))
		else:
			flash("Login unsuccessful, invalid username")
			return redirect(url_for("login"))

		# Pass to view method using data from session.
		flash("Login successful!")
		return redirect(url_for("view"))
	else:
		if "user" in session:
			flash("Already logged in.")
			return redirect(url_for("view"))
		
		return render_template("login.html")

@app.route("/logout")
def logout():
	flash("You are logged out")
	session.pop("user", None)
	session.pop("password", None)
	session.pop("account", None)
	return redirect(url_for("login"))