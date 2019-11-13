import os

from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sys import argv, exit
import csv

# Interact with a SQL database
db = sqlalchemy("postgres://xpsrascgzfgxzm:b7668097ffd03198d922523344120670dd76f03a849c9977a804cd2ab5631c46@ec2-54-197-239-115.compute-1.amazonaws.com:5432/d2ebb11rclhqv")

# Don't need to CREATE table since it already exists in the db

# Check that usage was appropriate
if len(argv) != 2:
    print("[Usage]: python import.py <csv>")
    exit(1)

databaseFileName = argv[1]
fields =[]
rows =[]
names = []

# Opens database file and stores in a dictionary
with open(databaseFileName) as csvfile:
    csvReader = csv.DictReader(csvfile)

    # Extracts row data one by one
    for row in csvReader:
        rows.append(row)

# Inserts house and birth into the db
for row in rows:
    # Parse the string for first, middle, and last name
    name = row["name"].split()

    if len(name) == 2:
        name.insert(1, "NULL")

    db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES (?, ?, ?, ?, ?)", name[0], name[1], name[2], row["house"], row["birth"])
