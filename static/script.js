$(function(){

    $("#btn-add-task").click(function(){
        $(".container-form").slideToggle();
    });

    $("#btn-delete-subject").click(function(){
        // Add a th before the first th, with a Delete content
        $("tr th:first-child").before("<th>Delete</th>");

        // For each tr, add a td before its first child
        $("tbody>tr").each(function(index, element) {
            var id = $(this).children(":last").children(":first").children(":first").attr("value");
            $(this).children(":first").before("<td><form id='form-" + index + "' class='delete-form' action='/delete_subject' method='post'> <input name='subject_id' hidden type='text' value='" + id + "'> <button type='submit' style='background: transparent; border: none;'><i class='fas fa-trash'></i> </button></form> </td>");
        });

        // hide delete element
        $("#btn-delete-subject").hide();
        // show -done- button
        $("#btn-done").show();

    });

    $("#btn-delete-task").click(function(){
        // Add a th before the first th, with a Delete content
        $("tr th:first-child").before("<th>Delete</th>");

        // For each tr, add a td before its first child
        $("tbody>tr").each(function(index, element) {
            var id = $(this).children(":last").children(":first").children(":first").attr("value");
            $(this).children(":first").before("<td><form id='form-" + index + "' class='delete-form' action='/delete_task' method='post'> <input name='task_id' hidden type='text' value='" + id + "'> <button type='submit' style='background: transparent; border: none;'><i class='fas fa-trash'></i> </button></form> </td>");
        });

        // hide delete element
        $("#btn-delete-task").hide();
        // show -done- button
        $("#btn-done").show();

    });

    $(".delete-form").click(function(){
        // Submit this form
        alert(this);
        $(this).submit();
        alert("submiting");
    });

    $("#btn-done").click(function(){
        // remove the first th (child of tr) 
        $("tr th:first-child").remove();
        // remove the first td, child of tr
        $("tr td:first-child").remove()
        $("#btn-done").hide();
        $("#btn-delete-task").show();
        $("#btn-delete-subject").show();
    });

    // Input: background hexcolor, output: font color 
    function getContrast(rgbcolor){
        rgbcolor = rgbcolor.replace('rgb(', '');
        rgbcolor = rgbcolor.replace('rgba(', '')
        rgbcolor = rgbcolor.replace(')', '');

        var array = JSON.parse("[" + rgbcolor + "]");
        var r = array[0];
        var g = array[1];
        var b = array[2];
        var yiq = (((r*299)+(g*587)+(b*114))/1000);
        return (yiq >= 170) ? 'black' : 'white';
    }

    $('.subject_td').each(function() {
        var bgcolor = $(this).css('backgroundColor');
        var fontcolor = getContrast(bgcolor);

        $(this).css("color", fontcolor);
    });
    
    $('.subject_td>div').each(function() {
        var bgcolor = $(this).css('backgroundColor');
        var fontcolor = getContrast(bgcolor);

        $(this).css("color", fontcolor);
    });
    
    
})

