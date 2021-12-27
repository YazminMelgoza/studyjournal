import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, timedelta

from helpers import apology, login_required, validate_date, weekList, monthList, get_total_hours, get_total_tasks, convert_hour_to_num

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
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///studyjournal.db")

@app.route("/", methods=["GET"])
@login_required
def index():
    """Show tasks, add new ones and edit them"""
    # Gets columns per row in the database that are not completed
    tasks = db.execute("SELECT tasks.id, tasks.user_id, assignment, subjects.subject, deadline, duration, status, tasks.difficulty, subjects.difficulty subject_difficulty, type FROM tasks JOIN subjects ON tasks.subject_id = subjects.id WHERE tasks.user_id = ? AND completed_date IS NULL ORDER BY CASE WHEN status = 'completed' THEN 1 END, deadline, CASE WHEN subject_difficulty = 'hard' THEN 1 WHEN subject_difficulty = 'medium' THEN 2 WHEN subject_difficulty = 'easy' THEN 3 END, CASE WHEN tasks.difficulty = 'hard' THEN 1 WHEN tasks.difficulty = 'medium' THEN 2 WHEN tasks.difficulty = 'easy' THEN 3 END, CASE WHEN status = 'assigned' THEN 1 WHEN status = 'in progress' THEN 2 WHEN status = 'completed' THEN 3 END, duration DESC", session["user_id"])

    subjects = db.execute("SELECT * FROM subjects WHERE user_id = ?", session["user_id"])

    # sets the list of status for each task
    for task in tasks:
        # Resets status list
        select_status = ["assigned", "in progress", "completed"]
        # Removes current status from the list
        current_status = task["status"]
        select_status.remove(current_status.lower())

        # Reinsert the current status at the beggining of the list
        select_status.insert(0, current_status)
        # Changes the value of the key to be the modified list
        task["status"] = select_status

        # Formats date to be more legible
        deadline = datetime.strptime(task['deadline'], '%Y-%m-%d')
        task["deadline"] = deadline.strftime('%a %d %b')
        
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
    """ add new tasks to the database and validates input"""
    input_assignment = request.form.get("assignment")
    input_subject_id = request.form.get("subject_id")
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
    if not input_subject_id:
        return apology("Please enter a subject")
    rows_subject = db.execute("SELECT subject, id FROM subjects WHERE user_id = ?", session["user_id"])
    subjects = []
    subjects_id = []
    for row in rows_subject:
        subjects.append(row["subject"])
        subjects_id.append(int(row["id"]))

    if not int(input_subject_id) in subjects_id:
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
    db.execute("INSERT INTO tasks (user_id, assignment, subject_id, deadline, type, difficulty, duration) VALUES (?, ?, ?, ?, ?, ?, ?)", session["user_id"], input_assignment, input_subject_id, input_deadline, input_type, input_difficulty, input_est_time)
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
    subjects = db.execute("SELECT * FROM subjects WHERE user_id = ?", session["user_id"])
    return render_template("subjects.html", subjects=subjects)


@app.route("/add_subject", methods = ["GET", "POST"])
@login_required
def add_subject():
    """Add more subjects"""
    input_subject = request.form.get("subject")

    for character in input_subject:
        if character in not_allowed_characters :
            return apology("Character " + character + " is not allowed")
    
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


@app.route("/focus", methods=["GET"])
@login_required
def focus():
    # Get rows of tasks from the database
    tasks = db.execute("SELECT a.id, a.assignment, a.duration, b.subject, b.color FROM tasks a JOIN subjects b ON a.subject_id = b.id WHERE a.user_id = ? AND completed_date IS NULL AND a.status != 'completed' ORDER BY deadline, CASE WHEN b.difficulty = 'hard' THEN 1 WHEN b.difficulty = 'medium' THEN 2 WHEN b.difficulty = 'easy' THEN 3 END, duration DESC", session["user_id"])
    return render_template("focus.html", tasks=tasks)


@app.route("/history")
@login_required
def history():
    # A) hours studied
    # 1.-today
    today = date.today()
    week = weekList()
    month = monthList()

    hoursWeek = get_total_hours(week)
    hoursToday = get_total_hours([str(today)])
    hoursMonth = get_total_hours(month)

    hours_studied = {"today": hoursToday, "week": hoursWeek, "month": hoursMonth }
    
    tasksWeek  = get_total_tasks(week)
    tasksToday = get_total_tasks([str(today)])
    tasksMonth = get_total_tasks(month)

    tasks = {'today': tasksToday, "week": tasksWeek, "month": tasksMonth}

    completed_tasks = db.execute("SELECT a.id, assignment, b.subject, a.deadline, duration, a.difficulty, a.type, a.completed_date, b.color FROM tasks a JOIN subjects b ON a.subject_id = b.id WHERE a.user_id = ? AND a.completed_date IS NOT NULL ORDER BY a.completed_date DESC", session["user_id"])
    return render_template("history.html", hours=hours_studied, tasks = tasks, completed_tasks=completed_tasks)


@app.route("/ajax_studylog", methods = ["POST"])
@login_required
def ajax_studylog():
    if request.json:    
        # Get inputs from the user
        duration = request.json['duration']
        task_id = request.json['task_id']

        # Get formatted date
        d = datetime.now()
        date = d.strftime("%Y-%m-%d")

        # Insert into database
        db.execute("INSERT INTO studylog (user_id, task_id, date, duration) VALUES (?, ?, ?, ?)", session["user_id"], task_id, date, duration)
        return jsonify("Studylog submitted succesfully")
    else:
        return jsonify("Couldn't submit studylog")


@app.route("/ajax_tasks", methods = ["GET"])
@login_required
def ajax_tasks():
    tasks = db.execute("SELECT a.id, assignment, b.subject, duration FROM tasks a JOIN subjects b ON a.subject_id = b.id WHERE a.user_id = ? AND a.completed_date IS NULL", session["user_id"])
    return jsonify(tasks)


@app.route("/getChartData", methods = ["GET"])
@login_required
def getChartData():
    """Gets the number of hours studied by the user in the last 7 days"""
    # List to store the chart's column [column1, column2,... ]
    dataList = [['Day', 'Hours']]
    
    # stores the days in the week in a list
    week = list(reversed(weekList()))

    for day in week:
        # list of dictionaries [{'duration':  }, {}, ...]
        rows = db.execute("SELECT duration FROM studylog WHERE user_id = ? AND date = ? ", session["user_id"], day)
        
        # Initializes sum to 0:00:00
        hours = timedelta()
        for row in rows:
            duration = row['duration']
            (h, m, s) = duration.split(":")
            d = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
            hours += d
        hours = convert_hour_to_num(str(hours))
        #stores date, hours in the dataList
        dataList.append([day, hours])

    return jsonify(dataList)


@app.route("/getPieChartData", methods = ["GET"])
@login_required
def getPieChartData():
    data_list = [['Task', 'Hours']]
    color_dict = {}

    today = str(date.today())
    task_ids = db.execute("SELECT * FROM studylog WHERE user_id = ? AND date = ? GROUP BY task_id", session["user_id"], today)

    task_list = [element['task_id'] for element in task_ids]

    for index, task_id in enumerate(task_list): 
        # Gets the data 
        rows = db.execute("SELECT a.task_id, a.date, a.duration, b.assignment, c.subject, c.color FROM studylog a JOIN tasks b ON a.task_id = b.id JOIN subjects c ON b.subject_id = c.id WHERE a.user_id = ? AND a.task_id = ? AND a.date = ?", session["user_id"], task_id, today)
        
        # Declares variables
        color = rows[0]['color']
        assignment = rows[0]['assignment'] 
        subject = rows[0]['subject']
        task_name = assignment + " " + subject
        hours = timedelta()

        # Adds all the hours into a single variable
        for row in rows:
            duration = row['duration']
            (h, m, s) = duration.split(":")
            d = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
            hours += d

        # convert hours to number (float)
        hours = convert_hour_to_num(str(hours))

        # stores date, hours in the dataList
        data_list.append([task_name, hours])
        
        # stores the color
        color_dict[index] = {'color': color}

    data_dict = {'data': data_list, 'slicesColor': color_dict}
    
    return jsonify(data_dict)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
