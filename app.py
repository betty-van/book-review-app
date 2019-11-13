# Goodreads API
# key: Ofp1GU7uUbEelrn6ZrT9w
# secret: Ywf8dKYfvqVbmNoUJwNGZgH2lHAFciC7rzQbu2Ds4s
import os

import requests
from flask import Flask, session, render_template, request
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

@app.route("/search", methods=["POST"])
def search():
    name= request.form.get("name")
    password= request.form.get("password")
    headline="Fill out the form below to start searching for books."
    return render_template("search.html", headline=headline, name=name,  password=password)

@app.route("/logout")
def logout():
    headline="You have successfully logged out."
    return render_template("logout.html", headline=headline)

@app.route("/results", methods=["POST", "GET"])
def results():
    isbn=request.form.get("isbn")
    title=request.form.get("title")
    author=request.form.get("author")
    headline="Your search results are below."
    return render_template("search-result.html", headline=headline, isbn=isbn, title=title, author=author)

@app.route("/registrationsuccess", methods=["POST"])
def is_registered():
    name= request.form.get("name")
    password= request.form.get("password")

    # Check to see if name and password is already in the table
    accounts = db.execute("SELECT name, password FROM users WHERE name = :name AND password = :password", {"name": name, "password": password}).fetchone()
    alreadyRegistered = accounts != None
    if alreadyRegistered: 
        headline="You already have an account. Please log in by clicking the link below to be redirected back to the home page."
        return render_template("registrationsuccess.html", headline=headline, name=name,  password=password)
    else:
        # If name and password is NOT in the table, insert it into the table
        db.execute("INSERT INTO users (name, password) VALUES (:name, :password)", {"name": name, "password": password})
        headline="Successful registration. Please log in by clicking the link below to be redirected back to the home page."
        return render_template("registrationsuccess.html", headline=headline, name=name,  password=password)
    db.commit()
    