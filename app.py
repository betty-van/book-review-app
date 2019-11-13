# Goodreads API
# key: Ofp1GU7uUbEelrn6ZrT9w
# secret: Ywf8dKYfvqVbmNoUJwNGZgH2lHAFciC7rzQbu2Ds4s
import os

import requests
from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Rendering template index.html to default url
@app.route("/")
def index():
    headline="Please log in using the form below:"
    return render_template("index.html", headline=headline)

@app.route("/register")
def register():
    headline="Enter the following details to make an account."
    return render_template("register.html", headline=headline)