import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


from helpers import apology, login_required, lookup, usd, validate_date

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# CONSTANT VALUES
DIFFICULTIES = ['hard','medium', 'easy']
STATUSES = ['assigned', 'in progress', 'completed']
not_allowed_characters = "<>{}#$^&*:;/!"
TYPES = ['homework', 'exam', 'project', 'personal', 'lecture', 'other']

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

    subjects = db.execute("SELECT * FROM subjects WHERE user_id = ? AND hide = 'false'", session["user_id"])
    # sets the list of status for each task
    if len(tasks) != 0:
        for task in tasks:
            # Resets status list
            select_status = ["assigned", "in progress", "completed"]
            # Removes current status from the list
            current_status = task["status"]
            print(current_status)
            select_status.remove(current_status.lower())
            # Reinsert the current status at the beggining of the list
            select_status.insert(0, current_status)
            # Changes the value of the key to be the modified list
            task["status"] = select_status

            # Formats date to be more legible
            deadline = datetime.strptime(task['deadline'], '%Y-%m-%d')
            task["deadline"] = deadline.strftime('%d %b %Y')
            # task['deadline'] = task["deadline"][8:] + '-' + task["deadline"][5:7] + '-' + task["deadline"][0:4]
    else:
        tasks.append({"id": 37, "assignment": "study", "subject": 'matematicas', 'deadline': 'today', "type": 'homework', 'difficulty':'easy', 'status':['Assigned', 'In Progress', 'Completed'], 'est_time': '1 hour'})
    # gets the dictionary of colors
    rows_subjects = db.execute("SELECT subject, color FROM subjects WHERE user_id = ?", session["user_id"])
    # Creates an empty dictionary to store: subject: color
    colors = {}
    for row in rows_subjects:
        colors[row["subject"]] = row["color"]
    # passes variables to the template
    return render_template("index.html", tasks=tasks, subjects=subjects, colors=colors)


@app.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task():
    """Show tasks, add new ones and edit them"""
    # Gets columns per row in the database that are not completed
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? AND completed_date = NULL", session["user_id"])
    if len(tasks) == 0:
        tasks.append({"id": 37, "assignment": "study", "subject": 'matematicas', 'deadline': 'today', "type": 'homework', 'difficulty':'easy', 'status':['Assigned', 'In Progress', 'Completed'], 'est_time': '1 hour'})
    input_assignment = request.form.get("assignment")
    input_subject = request.form.get("subject")
    input_deadline = request.form.get("deadline")
    input_type = request.form.get("type")
    input_difficulty = request.form.get("difficulty")
    input_est_time = request.form.get("est_time")

    # Validates assignment
    if not input_assignment:
        return apology("Must enter an assignment")
    for character in input_assignment:
        if character in not_allowed_characters:
            return apology("This character '" + character + "' is not allowed")

    # Validates subject
    if not input_subject:
        return apology("Please enter a subject")
    rows_subject = db.execute("SELECT subject FROM subjects WHERE user_id = ?", session["user_id"])
    subjects = []
    for row in rows_subject:
        subjects.append(row["subject"])

    if not input_subject in subjects:
        return apology("Please register your subject before you use it")

    # Validates deadline
    print(input_deadline)
    if not input_deadline:
        return apology("Please enter a deadline")

    validate_date(input_deadline)

    # Validates type
    if input_type not in TYPES:
        return apology("Please enter a valid type from the select menu")
    
    # Validates difficulty
    if input_difficulty not in DIFFICULTIES:
        return apology("Select a valid difficulty")

    # Validates time
    if not input_est_time:
        return apology("please enter an estimated time")
    if not len(input_est_time) == 5:
        return apology("Invalid estimated time, must be HH:MM")
    if not input_est_time[0] in ['0', '1', '2']:
        return apology("Invalid estimated time, use 24 hours format")
    if int(input_est_time[:1]) > 24:
        return apology("The maximum hours are 24")

    # inserts data into the database
    db.execute("INSERT INTO tasks (user_id, assignment, subject, deadline, type, difficulty, est_time) VALUES (?, ?, ?, ?, ?, ?, ?)", session["user_id"], input_assignment, input_subject, input_deadline, input_type, input_difficulty, input_est_time)
    # redirects to index
    return redirect("/")


@app.route("/delete_task", methods=["GET", "POST"])
@login_required
def delete_task():
    """Delete a task by its id and user id"""    
    # Gets input
    input_task_id = request.form.get("task_id")

    # Confirm its a valid id
    if not len(db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", input_task_id, session["user_id"])) == 1:
        return apology("You can't delete this task")
    
    # Deletes the task from database
    db.execute("DELETE FROM tasks WHERE id = ? and user_id = ?", input_task_id, session["user_id"])

    return redirect('/')


@app.route("/update_status", methods=["GET", "POST"])
@login_required
def update_status():
    """Update the status from an existing task"""
    input_task_id = request.form.get("task_id")
    input_status = request.form.get("input_status")

    # Ensure both inputs are submitted
    if not input_status or not input_task_id:
        return apology("must provide a new status and a task")

    # Validate input status
    if not input_status in STATUSES:
        return apology(str(input_status) + " is an invalid status")
    
    # Validate task id
    rows_task = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", input_task_id, session["user_id"])
    if not len(rows_task) == 1:
        return apology("You cannot update that task")

    db.execute("UPDATE tasks SET status = ? WHERE id = ? AND user_id = ?", input_status, input_task_id, session["user_id"])

    return redirect("/") 


@app.route("/complete_task", methods=["POST"])
@login_required
def complete_task():
    input_task_id = request.form.get("task_id")
    
    # Confirms data is submitted
    if not input_task_id:
        return apology("Couldn't find that task")
    
    # Validates input task id
    if not len(db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", input_task_id, session["user_id"])) == 1:
        return apology("Could't find that task :P")
    
    # Gets datetime
    now = datetime.now()
    dt_string = now.strftime("%Y/%m/%d %H:%M")
    
    # Update database. Since completed_date is not null, it wont be displayed in HTML file
    db.execute("UPDATE tasks SET completed_date = ? WHERE id = ? AND user_id = ?", dt_string, input_task_id, session["user_id"])

    return redirect("/")


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
