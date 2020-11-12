from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy #sqlalchemy
from flask_bcrypt import Bcrypt
from bankapp import db

class customers(db.Model):
	_id = db.Column("id", db.Integer, primary_key=True)
	#NOTE: "name", and "password", is optional
	name = db.Column("name", db.String(30))
	password = db.Column("password", db.String(100)) # ADD unique=True, nullable=False

	def __init__(self, name, password):
		self.name = name
		self.password = password