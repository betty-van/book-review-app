import os

from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sys import argv, exit
import csv

# Interact with a SQL database
# database engine object from SQLAlchemy that manages connections to the database
# DATABASE_URL is an environment variable that indicates where the database lives
engine = create_engine(os.getenv("DATABASE_URL"))

# create a 'scoped session' that ensures different users' interactions with the database are kept separate
db = scoped_session(sessionmaker(bind=engine))

f = open("books.csv")
reader = csv.reader(f)


# loop gives each column a name
for isbn, title, author, year in reader: 
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year }) 
    print("Added {} book published in {} with ISBN number {} written by {}".format(title, year, isbn, author))
db.commit()

