from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy #sqlalchemy
from flask_bcrypt import Bcrypt
from bankapp import db
from decimal import Decimal

class Customer(db.Model):
	_id = db.Column("id", db.Integer, primary_key=True)
	name = db.Column("name", db.String(30))
	password = db.Column("password", db.String(100))
	accounts = db.relationship("Account", backref="owner", lazy=True)

	def __init__(self, name, password, amount):
		self.name = name
		self.password = password
		self.amount = amount

	def sub_amount(self, minus_amount):
		self.amount -= minus_amount

class Account(db.Model):
	_id = db.Column("id", db.Integer, primary_key=True)
	bank_id = db.Column("number", db.Integer, unique=True)
	amount = db.Column("amount", db.Numeric(scale=2))
	account_type = db.Column("type", db.String(10))
	transactions = db.relationship("Transaction", backref="receiver", lazy=True)
	owner_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)

	def sub_amount(self, minus_amount):
		self.amount -= minus_amount

	def add_amount(self, add_amount):
		self.amount += add_amount

class Transaction(db.Model):
	_id = db.Column("id", db.Integer, primary_key=True)
	merchant_id = db.Column("merchant", db.Integer)
	amount = db.Column("transfer_amount", db.Numeric(scale=2))
	date_sent = db.Column(db.DateTime, default=datetime.utcnow)
	receiver_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)

def init_db():
	db.drop_all()
	db.create_all()

if __name__ == "__main__":
	init_db()