# Goodreads API
# key: Ofp1GU7uUbEelrn6ZrT9w
# secret: Ywf8dKYfvqVbmNoUJwNGZgH2lHAFciC7rzQbu2Ds4s
# DATABASE_URL=postgres://xpsrascgzfgxzm:b7668097ffd03198d922523344120670dd76f03a849c9977a804cd2ab5631c46@ec2-54-197-239-115.compute-1.amazonaws.com:5432/d2ebb11rclhqv
import os

import requests
import json
from flask import Flask, session, render_template, request, jsonify
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
    isLoggedIn = db.execute("SELECT name, password FROM users WHERE name = :name AND password = :password", {"name": name, "password": password}).rowcount > 0
    if isLoggedIn == True: 
        # If match, render search page and continue
        headline="Fill out the form below to start searching for books."
        return render_template("search.html", headline=headline)
    elif isLoggedIn == False:
        # If name and password is NOT in the table, revert to login page
        headline="You entered an invalid username and password. Please try again or register for an account."
        return render_template("index.html", headline=headline)  

@app.route("/logout")
def logout():
    headline="You have successfully logged out."
    return render_template("logout.html", headline=headline)

@app.route("/results", methods=["POST", "GET"])
def results():
    isbn=request.form.get("isbn")
    title=request.form.get("title")
    author=request.form.get("author")

    # List all books found in the db that matches
    # If ONLY ISBN is entered
    if not author and not title:
        books = db.execute("SELECT * FROM books WHERE isbn ILIKE :isbn", {"isbn": '%'+ isbn + '%'}).fetchall()
        bookNotFound = db.execute("SELECT * FROM books WHERE isbn ILIKE :isbn", {"isbn": '%'+ isbn + '%'}).rowcount == 0
    # Only isbn and author is filled out
    if not title:
        books = db.execute("SELECT * FROM books WHERE isbn ILIKE :isbn AND author ILIKE :author", {"isbn": '%'+ isbn + '%', "author":'%'+ author + '%'}).fetchall()
        bookNotFound = db.execute("SELECT * FROM books WHERE isbn ILIKE :isbn AND author ILIKE :author", {"isbn": '%'+ isbn + '%', "author":'%'+ author + '%'}).rowcount == 0
    # Only isbn and title is filled out
    if not author:
        books = db.execute("SELECT * FROM books WHERE isbn ILIKE :isbn AND title ILIKE :title", {"isbn": '%'+ isbn + '%', "title":'%'+ title + '%'}).fetchall()
        bookNotFound = db.execute("SELECT * FROM books WHERE isbn ILIKE :isbn AND title ILIKE :title", {"isbn": '%'+ isbn + '%', "title":'%'+ title + '%'}).rowcount == 0
    # If only author was filled out
    if not title and not isbn:
        books = db.execute("SELECT * FROM books WHERE author ILIKE :author", {"author": '%'+ author + '%'}).fetchall()
        bookNotFound = db.execute("SELECT * FROM books WHERE author ILIKE :author", {"author": '%'+ author + '%'}).rowcount == 0
    # Only author and title are filled in
    if not isbn: 
        books = db.execute("SELECT * FROM books WHERE title ILIKE :title AND author ILIKE :author", {"title": '%'+ title + '%', "author":'%'+ author + '%'}).fetchall()
        bookNotFound = db.execute("SELECT * FROM books WHERE title ILIKE :title AND author ILIKE :author", {"title": '%'+ title + '%', "author":'%'+ author + '%'}).rowcount == 0
    #  Only title is filled in
    if not author and not isbn:
        books = db.execute("SELECT * FROM books WHERE title ILIKE :title", {"title": '%'+ title + '%'}).fetchall()
        bookNotFound = db.execute("SELECT * FROM books WHERE title ILIKE :title", {"title": '%'+ title + '%'}).rowcount == 0
    # All fields are filled in
    else:
        books =  db.execute("SELECT * FROM books WHERE isbn ILIKE :isbn AND title ILIKE :title AND author ILIKE :author", {"isbn": '%'+ isbn + '%', "title": '%' + title + '%', "author":'%'+ author + '%'}).fetchall()
        bookNotFound = db.execute("SELECT * FROM books WHERE isbn ILIKE :isbn AND title ILIKE :title AND author ILIKE :author", {"isbn": '%'+ isbn + '%', "title": '%' + title + '%', "author":'%'+ author + '%'}).rowcount == 0
    
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
    reviews = db.execute("SELECT * FROM reviews WHERE book_id  = :book_id", {"book_id": book.isbn})
    if book is None:
        headline = "Book not found."
        return render_template("error.html", headline=headline)

    # Get Goodreads avg rating and number of ratings
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Ofp1GU7uUbEelrn6ZrT9w", "isbns": book.isbn})
    book = res.json()
    average_rating = book['books'][0]['average_rating']
    rating_number = book['books'][0]['work_ratings_count']

    
    # Get book details & render onto page
    return render_template("bookdetails.html", book=book, reviews=reviews)

@app.route("/reviews/<int:book_id>")
def review(book_id):
    # Check book is in databasea
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        headline = "Book not found."
        return render_template("error.html", headline=headline)

    # Render review page
    headline = "Fill in the review form below and press submit."
    return render_template("review.html", headline=headline)

@app.route("/submissionsuccess", methods=["POST"])
def submission():
    username= request.form.get("username")
    reviewText= request.form.get("reviewText")
    rating= request.form.get("rating")
    isbn = request.form.get("isbn")

    # Make sure book exists
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        headline = "Book not found."
        return render_template("error.html", headline=headline)

    # Check if this user already made a review by checking username and isbn
    alreadyReviewed = db.execute("SELECT user_id, book_id FROM reviews WHERE user_id = :user_id AND book_id = :book_id", {"user_id": username, "book_id": isbn}).rowcount > 0

    if alreadyReviewed:
        currentReview = db.execute("SELECT user_id, book_id FROM reviews WHERE user_id = :user_id AND book_id = :book_id", {"user_id": username, "book_id": isbn}).fetchone()
        headline = "You have already submitted a review for this book."
        return render_template("submission.html", headline=headline, username=username, reviewText=currentReview.review, rating=currentReview.rating)
    elif not alreadyReviewed:
    # Insert into reviews table
        db.execute("INSERT INTO reviews(user_id, review, rating, book_id) VALUES (:user_id, :review, :rating, :book_id)", {"user_id": username, "review": reviewText, "rating": rating, "book_id": isbn})
        db.commit()
        headline="Your submission was successful."
        return render_template("submission.html", headline=headline, username=username, reviewText=reviewText, rating=rating)

@app.route("/api/<string:isbns>", methods=["GET"])
def api(isbns):
    # Check if ISBN is in database
    inDatabase = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbns}).rowcount > 0
    if not inDatabase:
        return ({"error": "Invalid isbns"}), 404

    # Get book in database
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbns}).fetchone()

    # Get Goodreads api
    credentials= "Ofp1GU7uUbEelrn6ZrT9w"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": credentials, "isbns": isbns})
    bookJSON = res.json()

    average_rating = bookJSON['books'][0]['average_rating']
    rating_number = bookJSON['books'][0]['work_ratings_count']

    headline="JSON Object"

    # Make sure printing correct variables
    myJSON = {
        "title": book.title,
        "isbn": book.isbn,
        "year": book.year,
        "author": book.author,
        "review_count": rating_number,
        "average_rating": average_rating
    }

    return jsonify(myJSON)


    

    