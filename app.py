import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# CONSTANT VALUES
DIFFICULTIES = ['hard','medium', 'easy']
STATUSES = ['assigned', 'in progress', 'completed']
not_allowed_characters = "<>{}#$^&*:;/!"

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///studyjournal.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show tasks, add new ones and edit them"""
    # Gets columns per row in the database that are not completed
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? AND completed_date IS NULL", session["user_id"])
    if len(tasks) == 0:
        tasks.append({"id": 37, "assignment": "study", "subject": 'matematicas', 'deadline': 'today', "type": 'homework', 'difficulty':'easy', 'status':['Assigned', 'In Progress', 'Completed'], 'est_time': '1 hour'})

    subjects = db.execute("SELECT * FROM subjects WHERE user_id = ? AND hide = 'false'", session["user_id"])
    # passes portfolio to the template
    return render_template("index.html", tasks=tasks, subjects=subjects)


@app.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task():
    """Show tasks, add new ones and edit them"""
    # Gets columns per row in the database that are not completed
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? AND completed_date = None", session["user_id"])
    if len(tasks) == 0:
        tasks.append({"id": 37, "assignment": "study", "subject": 'matematicas', 'deadline': 'today', "type": 'homework', 'difficulty':'easy', 'status':['Assigned', 'In Progress', 'Completed'], 'est_time': '1 hour'})
    input_assignment = request.form.get("assignment")
    input_subject = request.form.get("subject")
    input_deadline = request.form.get("deadline")
    input_type = request.form.get("deadline")
    input_difficulty = request.form.get("difficulty")
    input_est_time = request.form.get("est_time")

    # Validates assignment
    for character in input_assignment:
        if character in not_allowed_characters:
            return apology("This character '" + character + "' is not allowed")

    # Validates subject
    rows_subject = db.execute("SELECT subject FROM subjects WHERE user_id = ?", session["user_id"])
    subjects = []
    for row in rows_subject:
        subjects.append(row["subject"])

    if not input_subject in subjects:
        return apology("Please register your subject before you use it")

    # Validates time
    if not len(input_est_time) == 5:
        return apology("Invalid estimated time, must be HH:MM")
    if not input_est_time[0] in ['1', '2']:
        return apology("Invalid estimated time, use 24 hours format")
    if int(input_est_time[:1]) > 24:
        return apology("The maximum hours are 24")

    # inserts data into the database
    db.execute("INSERT INTO tasks (user_id, assignment, subject, deadline, type, difficulty, est_time) VALUES (?, ?, ?, ?, ?, ?, ?)", session["user_id"])
    # redirects to index
    return redirect("/")

@app.route("/delete_task", methods=["GET", "POST"])
@login_required
def delete_task():
    """Show tasks, add new ones and edit them"""
    # Gets columns per row in the database that are not completed
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? AND completed_date = None", session["user_id"])
    if len(tasks) == 0:
        tasks.append({"id": 37, "assignment": "study", "subject": 'matematicas', 'deadline': 'today', "type": 'homework', 'difficulty':'easy', 'status':['Assigned', 'In Progress', 'Completed'], 'est_time': '1 hour'})


    subjects = db.execute("SELECT * FROM subjects WHERE user_id = ? AND hide = 'false'", session["user_id"])
    # passes portfolio to the template
    return render_template("index.html", tasks=tasks, subjects=subjects)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/subjects")
@login_required
def subjects():
    """Show list of subjects"""
    subjects = db.execute("SELECT * FROM subjects WHERE user_id = ? AND hide = 'false'", session["user_id"])
    return render_template("subjects.html", subjects=subjects)

@app.route("/add_subject", methods = ["GET", "POST"])
@login_required
def add_subject():
    """Add more subjects"""
    input_subject = request.form.get("subject")

    for character in input_subject:
        if character in not_allowed_characters :
            return apology("Those symbols are not allowed")
    
    input_difficulty = request.form.get("difficulty")

    if not input_difficulty in DIFFICULTIES:
        return apology("Must enter a valid difficulty")
    
    input_subject = input_subject.strip()
    input_color = request.form.get("color")
    
    db.execute("INSERT INTO subjects (user_id, subject, difficulty, color) VALUES (?, ?, ?, ?)", session["user_id"], input_subject, input_difficulty, input_color)

    return redirect("/subjects")

@app.route("/delete_subject", methods = ["GET", "POST"])
@login_required
def delete_subject():
    """Delete an existing subject"""
    input_subject_id = request.form.get("subject_id")

    # Confirm its a valid id
    if not len(db.execute("SELECT * FROM subjects WHERE id = ? AND user_id = ?", input_subject_id, session["user_id"])) == 1:
        return apology("You can't delete this subject")
    
    # Deletes the subject from database
    db.execute("DELETE FROM subjects WHERE id = ? and user_id = ?", input_subject_id, session["user_id"])

    return redirect("/subjects")


@app.route("/completed_task")
def completed_task():
    """Register a completed task"""
    
    return redirect("/") 

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Ensure password confirmation is correct
        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("must confirm your password")

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # Ensure username doesnt exist
        if (len(rows) != 0):
            return apology("Username already exists. Must provide another")

        # Insert user into the database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?) ", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to subjects
        return redirect("/subjects")

    else:
        return render_template("register.html")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)