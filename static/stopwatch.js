let seconds = 0;
let minutes = 0;
let hours = 0;

// vars to hold display value
let displaySeconds = 0;
let displayMinutes = 0;
let displayHours = 0;

let interval = null;
let input_task_id = null;
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
    if (parseInt(task_id) === NaN){
        return false;
    }
    
    task_id = parseInt(task_id);

    $.get("/ajax_tasks", function(tasks){
        valid_ids = [];
        for (let index in tasks){
            let id = tasks[index].id;
            let assignment = tasks[index].assignment;
            let subject = tasks[index].subject;
            
            let name = assignment + " " + subject;

            valid_ids.push(id);

            if (id == task_id) {
                if (name != task_name) {
                    alert("Invalid input, 11task doesn't exist" + name + task_name);
                    return false;
                }
            }
        }
        if (!valid_ids.includes(task_id, 0)) {
            alert("Invalid input, 22task doesn't exist" + valid_ids);
            return false;
        }
    });
    return true;
}

function ajax_studylog(duration, task_id){
    console.log(duration);
    console.log(task_id);
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

$(function(){
    // Disables button at the start
    $(".play").attr("disabled", "disabled");

    // If form has been submited, enable the button to start 
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
        // Displays the selected input
        $("h3").html("Working on: " + input_task_name);
        // enables the button
        $(".play").removeAttr("disabled");
        // hides the form
        $(this).hide();
        $('.message').html("Press start");
        event.preventDefault();

    });
    
    // $(".play").removeAttr("disabled");
    $(".play").click(function(){
        interval = window.setInterval(stopwatch, 1000);

        $(this).hide();
        $(".pause").show();
        $(".stop").show();
        $('.message').html("Keep focused! You can do it");
    });
    
    $(".pause").click(function(){
        window.clearInterval(interval);
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
        window.clearInterval(interval);
        // Initializes the page to be used again 
        $(this).hide();
        $("#display").html("00:00:00");
        $(".pause").hide();
        $(".play").show();
        $('.message').html("You did well! you focused for " + duration);
        $(".play").attr("disabled", "disabled");
        $("form").show();
        $("h3").html("Let's get things done");
        // Sends data to the backend
        ajax_studylog(duration, input_task_id);
    });

});
