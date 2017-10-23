var pageLoaded = true;

$.post("/cgi-bin/interface.py",{comment:$("#btn2").val()}, responseVersions);
function responseVersions(response) {
    var i = 0;

    while (!(document.readyState === 'complete')) {
        console.log(i++);
        if (i > 100)
            break ;
    }
    $('#my_versions').html(response);
}

function show_log() {
    console.log(pageLoaded);
    if (pageLoaded === false){
        document.getElementById("loader").style.display = "block";
    }
}

function showOpenFileMessage() {
    $("#inf2").html("<strong>Please, select file</strong>");
    document.getElementById("in1").disabled = true;
    document.getElementById("upload_btn").disabled = true;
}

function hideOpenFileMessage() {
    document.getElementById("in1").disabled = false;
    document.getElementById("upload_btn").disabled = false;
}

function onResponse(btn){
    hideOpenFileMessage();
    $("#inf2").html(btn);
    pageLoaded = true;
    document.getElementById("loader").style.display = "none";
}

function sendData(data) {
    $.post("/cgi-bin/Controler.py", data, onResponse);
    pageLoaded = false;
    setTimeout(show_log, 5000);
    return false;
}

$(document).ready(function(){
    $('#ajax_form').submit(function(event){
        var data = {
            version: $('input[name="version"]:checked').val(),
            text: $("#input_textarea").val()
        };
        console.log(data["text"]);
        return sendData(data);
    });
    $('#ajax_form2').submit(function(event){
        var data = {
            version: $('input[name="version"]:checked').val(),
            file: "open file"
        };
        showOpenFileMessage();
        return sendData(data);
    });
});
