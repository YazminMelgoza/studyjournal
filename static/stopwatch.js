let seconds = 0;
let minutes = 0;
let hours = 0;

// vars to hold display value
let displaySeconds = 0;
let displayMinutes = 0;
let displayHours = 0;

let interval = null;
let input_task_id = null;

// Vars to hold time remaining and elapsed
let goalSeconds = [];

// Logic to increment seconds, minutes and hours
function stopwatch(){
    seconds++;

    if (seconds === 60) {
        // Restart seconds 
        seconds = 0;
        minutes++;

        if (minutes === 60) {
            // Reset minutes display
            minutes = 0;
            hours++;
            if (hours === 1) {
                $('.message').html("1 hour! You deserve a break, however, you can keep studying.");
            }
            else {
                $('.message').html( hours + " hours! You deserve a break, however, you can keep studying.");
            }
        }
        
        if (minutes === 30) {
            $('.message').html("30 minutes! You deserve a break, however, you can keep studying.");
        }
    }

    if (seconds < 10){
        displaySeconds = "0" + seconds.toString();
    }
    else {
        displaySeconds = seconds;
    }
 

    if (minutes < 10){
        displayMinutes = "0" + minutes.toString();
    }
    else {
        displayMinutes = minutes;
    }

    if (hours < 10){
        displayHours = "0" + hours.toString();
    }
    else {
        displayHours = hours;
    }

    // Display updated time values to user
    document.getElementById('display').innerHTML = displayHours + ':' + displayMinutes + ':' + displaySeconds;
}

function validate_input(task_id, task_name) {
    // 1.- Task id must be numeric
    if (parseInt(task_id) === NaN){
        return false;
    }

    // Since its numeric, ensure to convert it to type integer
    task_id = parseInt(task_id);
    
    // Initialize variable to hold get request and valid ids
    var result = null;

    // Makes a get request of the tasks from the corresponding user
    $.ajax({
        url: "/ajax_tasks",
        dataType: "json",
        type: "get",
        async: false,
        // data is stored in variable result
        success: function(data) {
            result = data;
        },
        error: function(event){
            event.preventDefault;
        } 
    });

    // Initialize variable to hold list of valid ids
    var valid_ids = [];
    
    // Iterates over result list of dictionaries
    for (let index in result){
        // Gets data per row
        let id = result[index].id;
        let assignment = result[index].assignment;
        let subject = result[index].subject;
        let name = assignment + " " + subject;

        // Stores valid ids in the list
        valid_ids.push(id);

        // if finds the task_id, then 
        if (id == task_id) {
            // compares names
            if (name != task_name) {
                alert("Invalid input, task name " +  task_id + " doesn't match");
                return false; 
            }
        }
    }

    // if the task id is not in the valid ids list, return false
    if (!valid_ids.includes(task_id, 0)) {
        alert("Invalid input, task doesnt exist");
        return false;
    }

    // if passes all tests, return true
    return true;
}

function getGoalSeconds(task_id){
    let totalTime = null;

    $.get("/ajax_tasks", function(tasks){
        // iterate over the list of dictionaries
        for(let index in tasks){
            // checks if the id of that task, matches the searched one
            let id = tasks[index].id;
            if (id == task_id){
                // If found, get the duration (est_time)
                totalTime = tasks[index].est_time;
            }
        }
        // convert string of text, to seconds
        a = totalTime.split(":");
        for (var x in a) {
            x = parseInt(x);
        }
        goalSeconds = (a[0]) * 3600 + (a[1]) * 60;
        console.log("total secs before return are "+ goalSeconds);
        
    })
    
    console.log("Return value total secs is " + goalSeconds);
    return goalSeconds;
}

// Makes an ajax post request that sends info to log into the database
function ajax_studylog(duration, task_id){

    $.ajax({
        url: '/ajax_studylog',
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify({"duration": duration, "task_id": task_id }, null, "\t"),
        dataType: 'json',
        type: "POST",
        success: function(response) {
            console.log(response);
        },
        error: function(error) {
            console.log(error);
        }
    });
};


// When the document is loaded, do the following
$(function(){
    // Disables button at the start
    $(".play").attr("disabled", "disabled");

    // When form is submited 
    $("form").on("submit", function(event){
        // Takes the input
        input_task_id = $("select option:checked").val();
        var input_task_name = $("select option:checked").html();
        // Confirms input is provided
        if (input_task_name === "Select a Task" || input_task_id === ""){
            alert("You must select a task")
            event.preventDefault();
            return false;
        }
        // Validates input
        if (!validate_input(input_task_id, input_task_name)){
            event.preventDefault();
            return false;
        }

        // Gets goal time
        $.get("/ajax_tasks", function(tasks){
            for(let index in tasks){
                // checks if the id of that task, matches the searched one
                let id = tasks[index].id;
                if (id == input_task_id){
                    // If found, get the duration (est_time)
                    totalTime = tasks[index].est_time;
                }
            }
            // convert string of text, to seconds
            a = totalTime.split(":");
            for (var x in a) {
                x = parseInt(x);
            }
            goalSeconds.push((a[0]) * 3600 + (a[1]) * 60);
            
            $(".animatedCircle").css("animation-duration", goalSeconds[0] + "s");
        });

        // Displays the selected input
        $("h3").html("Working on: " + input_task_name);

        // enables the button
        $(".play").removeAttr("disabled");

        // hides the form
        $(this).hide();
        // hides container form
        $(".container-form").hide();
        $('.message').html("Press start");
        event.preventDefault();
    });
    
    // When play button is clicked
    $(".play").click(function(){

        // starts running interval
        interval = window.setInterval(stopwatch, 1000);
        
        // Starts animation
        $(".animatedCircle").css("animation-play-state", "running")
        
        // Displays buttons ands message to user
        $(this).hide();
        $(".pause").show();
        $(".stop").show();
        if (minutes == 0 && seconds == 0 && hours == 0) {
            $('.message').html("When you finish, click the 'stop' button to save your progress");   
            setTimeout(function(){
                $('.message').html("Keep focused! You can do it");
            }, 10000)         
        }
        else {
            $('.message').html("Keep focused! You can do it");
        }
    });
    
    // When pause is clicked
    $(".pause").click(function(){
        window.clearInterval(interval);

        $(".animatedCircle").css("animation-play-state", "paused");
        $(this).hide();
        $(".play").show();
        $('.message').html("Don't forget to come back soon :)");
    });

    $(".stop").click(function(){
        //  Gets duration of the study session
        var duration = displayHours + ':' + displayMinutes + ':' + displaySeconds;
        // Resets stopwatch and variables
        seconds = 0;
        minutes = 0;
        hours = 0;

        goalSeconds.pop();
        window.clearInterval(interval);
        
        // Restart animation trick
        $("svg .animatedCircle").css("animation-play-state", "paused");
        var element = $("svg .animatedCircle"), newone = element.clone(true);
        
        element.before(newone);
        $("." + element.attr("class") + ":last").remove();
        
        // Initializes the page to be used again
        $(this).hide();
        $("#display").html("00:00:00");
        $(".pause").hide();
        $(".play").show();
        $('.message').html("You did well! you focused for " + duration);
        $(".play").attr("disabled", "disabled");
        $("form").show();
        $(".container-form").show();
        $("h3").html("Let's get things done");

        // Sends data to the backend
        ajax_studylog(duration, input_task_id);
    });

});
