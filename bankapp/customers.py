from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy #sqlalchemy
from flask_bcrypt import Bcrypt
from bankapp import db
from decimal import Decimal


class customers(db.Model):
	_id = db.Column("id", db.Integer, primary_key=True)
	#NOTE: "name", and "password", is optional
	name = db.Column("name", db.String(30))
	password = db.Column("password", db.String(100)) # ADD unique=True, nullable=False
	#TODO Remove amount
	amount = db.Column("amount", db.Numeric(scale=2)) # ADD nullable=False
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
	owner_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
#	def __init__(self, amount, customer_id):
#		self.amount = amount
#		self.customer_id = customer_id
	def sub_amount(self, minus_amount):
		self.amount -= minus_amount
		
	def add_amount(self, add_amount):
		self.amount += add_amount
#class Transaction(db.Model):
#	_id = db.Column("id", db.Integer, primary_key=True)


def init_db():
	db.drop_all()
	db.create_all()

if __name__ == "__main__":
	init_db()