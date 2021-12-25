import os
import requests
import urllib.parse
import datetime

from flask import redirect, render_template, request, session
from functools import wraps
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///studyjournal.db")

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def validate_date(date):
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return apology("Incorrect date format, should be YYYY-MM-DD")

def monthList():
    day = datetime.date.today()
    current_month = day.month
    tdelta = datetime.timedelta(days=1)
    monthdays = []
    
    while day.month == current_month:
        monthdays.append(str(day))
        day = day - tdelta

    return monthdays

def weekList():
    # Save the current date in a variable
    today = datetime.date.today()

    # Gets the last seven days in a list
    week = []
    for i in range(0, 7):
        tdelta = datetime.timedelta(days=i)
        week.append(str(today - tdelta))

    return week


def get_total_hours(dates):
    """Given a list of dates, returns the sum of all the hours in those days"""

    # initializes sum
    mysum = datetime.timedelta()
    for date in dates:
        rows = db.execute("SELECT duration FROM studylog WHERE user_id = ? AND date = ?", session["user_id"], date)
        
        for row in rows:
            timestring = row['duration']
            (h, m, s) = timestring.split(":")
            d = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
            mysum += d

    return str(mysum)


def get_total_tasks(dates):
    """Given a list of dates, returns the count of all the completed tasks in those days"""

    # initializes sum
    mysum = 0
    for date in dates:
        # formats the date string
        date = date.replace("-", "/")
        rows = db.execute("SELECT count(assignment) FROM tasks WHERE user_id = ? AND completed_date LIKE ?", session["user_id"], date + "%")
        
        mysum += int(rows[0]['count(assignment)'])

    return str(mysum)

def convert_hour_to_num(hour):
    """Given an hour:minutes:seconds string, returns a single num representing the hours"""
    (h, m, s) = hour.split(":")
    return int(h) + (float(m) / 60) + (float(s) / 3600)