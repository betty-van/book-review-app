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

# Set up a global variable tracking if logged in or not
isLoggedIn = False

# Rendering template index.html to default url
@app.route("/")
def index():
    headline="Please log in using the form below:"
    return render_template("index.html", headline=headline)

@app.route("/register")
def register():
    headline="Enter the following details to make an account."
    return render_template("register.html", headline=headline)

@app.route("/search", methods=["POST", "GET"])
def search():
    name= request.form.get("name")
    password= request.form.get("password")
    
    # Check if name and password are already in the database
    isLoggedIn = db.execute("SELECT name, password FROM users WHERE name = :name AND password = :password", {"name": name, "password": password}).rowcount > 0;
    if isLoggedIn == True: 
        # If match, render search page and continue
        headline="Fill out the form below to start searching for books."
        return render_template("search.html", headline=headline)
        isLoggedIn = True
    elif isLoggedIn == False:
        # If name and password is NOT in the table, revert to login page
        headline="You entered an invalid username and password. Please try again or register for an account."
        return render_template("index.html", headline=headline)  

@app.route("/logout")
def logout():
    headline="You have successfully logged out."
    isLoggedIn = False
    return render_template("logout.html", headline=headline)

# TODO
@app.route("/results", methods=["POST", "GET"])
def results():
    isLoggedIn = True
    isbn=request.form.get("isbn")
    title=request.form.get("title")
    author=request.form.get("author")

    # List all books found in the db that matches
    books =  db.execute("SELECT * FROM books WHERE isbn ILIKE :isbn OR title ILIKE :title OR author ILIKE :author", {"isbn": '%'+ isbn + '%', "title": '%' + title + '%', "author":'%'+ author + '%'}).fetchall()
    bookNotFound = db.execute("SELECT * FROM books WHERE isbn ILIKE :isbn OR title ILIKE :title OR author ILIKE :author", {"isbn": '%'+ isbn + '%', "title": '%' + title + '%', "author":'%'+ author + '%'}).rowcount == 0
    
    if bookNotFound:
        headline ="No book was found."
        return render_template("error.html", headline=headline)
    else: 
        headline="Your search results are below."
        return render_template("search-result.html", headline=headline, isbn=isbn, title=title, author=author, books=books)
        
@app.route("/registrationsuccess", methods=["POST"])
def is_registered():
    name= request.form.get("name")
    password= request.form.get("password")

    # Check to see if name and password is already in the table
    alreadyRegistered = db.execute("SELECT name, password FROM users WHERE name = :name AND password = :password", {"name": name, "password": password}).rowcount > 0
    if alreadyRegistered: 
        headline="You already have an account. Please log in by clicking the link below to be redirected back to the home page."
        return render_template("registrationsuccess.html", headline=headline, name=name,  password=password)
    elif not alreadyRegistered:
        # If name and password is NOT in the table, insert it into the table
        db.execute("INSERT INTO users (name, password) VALUES (:name, :password)", {'name': name, 'password': password})
        print(f"Added {name} to the database.", {"name": name})
        db.commit()
        headline="Successful registration. Please log in by clicking the link below to be redirected back to the home page."
        return render_template("registrationsuccess.html", headline=headline, name=name,  password=password)
    db.commit()   

@app.route("/bookdetails/<int:book_id>")
def bookdetails(book_id):
    # List all details about a single book

    # Make sure book exists by its book_id
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        headline = "Book not found."
        return render_template("error.html", headline=headline)
    
    # Get book details & render onto page
    return render_template("bookdetails.html", book=book)

    