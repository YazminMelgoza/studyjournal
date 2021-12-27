# StudyJournal
#### Video Demo: <URL HERE>
#### Description:
StudyJournal is a productivity tool for students. When students have a lot of responsabilities and tasks, many of us doesn't even know what to do first. StudyJournal automatically orders your tasks by priority, so you don't need to spend much time planning. 

* Login/Register: Create yor personal Account
* Tasks: Add and organize your tasks by priority
* Subjects: Customize your subjects with a color of your preference 
* Stopwatch: An implementation of the Reverse Pomodoro technique. Select a task from your list and start focusing 
* History: A quick visually representation of your progress today, the last 7 days and in the current month.

Each page has an specific purpose. For example, your History lets you visualize your progress and encourages you to do better than yesterday. The Stopwatch page is meant to help you focus on your task, reminding you that you can achieve your goals in a determined lapse of time if you keep concentrated. The subjects' difficulty is a piece of data used to prioritize your tasks. 
### How to use it?
1. After you register to StudyJournal, you'll be redirected to your subjects page. Then its time to start adding all of your subjects. You can choose a name, difficulty (easy, medium or hard) and a color. If you make a mistake you can delete tasks as well. 
2. Next you can go to your tasks page and start easily adding your pending tasks. Click on 'Add Task' and submit the form. 
3. Go to the 'Focus' page, you'll see a stopwatch. First select a task from the list and then click on the play button to measure the start the stopwatch. You can pause/resume your study session, but be sure to click at the 'stop' button when you finish, because otherwise your progress won't be saved.
4. After you started working on tasks, you may want to change the status of them in the 'tasks' page. If you have already worked on a certain task, you can update its status to 'in progress' or to 'completed'.
5. There's a check button on the last column of the tasks table, the difference between this button and the completed status is that you should click on the check button just after you have turned in your work to your teacher. This is a way to prevent users from forgetting to turn in things that they have already completed (It has happened to many of us at least once).  
6. Finally, you can view your study statistics in the History page.

Hope that you like all the features and use them well :)
## Understanding
#### app.py
First it imports some modules. You'll see that there's a module called datetime, and another called jsonify. Datetime was usefull to work with some of the features, for example, formatting and parsing date strings.  
`/index` makes a pretty long query to the database, that is because it is selecting Tasks by priority order, first it joins all the tables into a single one, and then orders them by cases: When the difficulty is hard, it will have a higher priority than an easy task, and so on and so forth. Then it formats the data before passing it into the template, you can see that it uses the datetime module to format the date from "YYYY-mm-dd" to "%a %d %b" e.g. "Mon 27 Dec". And finally it generates a dictionary of colors, containing all the subjects and its color.
Contains all the application routes, for GET requests, it may select query the database for  makes querys to the database to add or delete subjects/tasks and update tasks' status. 
It also returns JSON data to the frontend via AJAX in the focus page. You'll see at almost the end of the file that there are several routes that send or get data.
#### helpers.py
The functions on this file were created because they are used several times in `app.py`
#### static/script.js
Contains several functions used in `index.html`, `subjects.html`. There's one I would like to stand out. Since the user can enter a custom color for each subject, it would be a problem if text color was always white or always black, so I made this script to detect where to use black or white font color, If a subject has a darker color, the font would be white, else, it will be black. 
#### static/stopwatch.js
Has the logic to implement a stopwatch, when to increment seconds, minutes and hours. Starts an animation when the play button is clicked. When the stop button is clicked, it makes an AJAX POST request to the backend. 
#### static/charts.js
This script is used in the history page and it uses the Google API to generate 2 charts (A column chart and a pie chart).
First it gets the data from the backend, for the column chart it gets a list of the data rows, containg 'Day' and 'Hours'. Once it recieves a response, it generates the charts.
## Credits
StudyJournal icon - [Rawand Dahnous](https://dribbble.com/alrawand)
Background photo - [Jess Bailey](https://unsplash.com/@jessbaileydesigns?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)
Icons - [Font Awesome by Dave Gandy](http://fontawesome.io)
## How to lauch Application
1. Ensure you have installed Python 3 in your PC
2. Clone the code: `git clone https://github.com/YazminMelgoza/studyjournal.git`
3. In your terminal window, run this command: `pip install -r requirements.txt`
4. Run the app by the command `flask run`
5. Open your browser in your local host 127.0.0.1