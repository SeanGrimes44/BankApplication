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
#	amount = db.Column("amount", db.Numeric()) # ADD nullable=False
#	accounts = db.relationship("Account", backref="customer")

	def __init__(self, name, password):
		self.name = name
		self.password = password


#class Account(db.Model):
#	_id = db.Column("id", db.Integer, primary_key=True)
#	amount = db.Column("amount", db.Float
#	customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))


def init_db():
	db.drop_all()
	db.create_all()

if __name__ == "__main__":
	init_db()