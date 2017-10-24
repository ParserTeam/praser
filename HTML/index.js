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
}

function hideOpenFileMessage() {
    document.getElementById("in1").disabled = false;
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

function addFilesTextToInput(files) {
    var textArea = document.getElementById("input_textarea");

    textArea.textContent = "";
    var end = files.length;
    for (var i = 0, f; f = files[i]; i++) {
        var reader = new FileReader();

        // Closure to capture the file information.
        reader.onload = (function(theFile) {
            return function(e) {
                // Render thumbnail.
                textArea.textContent = textArea.textContent + "\n\n" + e.target.result;
                end--;
                if (end == 0)
                    console.log(textArea.textContent);
            };
        })(f);

        // Read in the image file as a data URL.
        reader.readAsText(f);
    }
}

function textareaChanged() {
    console.log("aaaaaaaaaaaaaaaaaa");
}

$(document).ready(function () {
    $('#input_textarea').change(function () {
        console.log("qwerty");
    })
});

function handleFileDrop(evt) {
    evt.preventDefault();
    var files = evt.dataTransfer.files;
    addFilesTextToInput(files);
}

function handleFileSelect(evt) {
    var files = evt.target.files; // FileList object
    addFilesTextToInput(files);
}

function handleDragOver(evt) {
        evt.stopPropagation();
        evt.preventDefault();
        evt.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
    }

document.getElementById('files').addEventListener('change', handleFileSelect, false);
var dropZone = document.getElementById('input_textarea');
dropZone.addEventListener('dragover', handleDragOver, false);
dropZone.addEventListener('drop', handleFileDrop, false);

function sendMyRequest(event) {
    console.log($("#file").val());
    var data = {
        version: $('input[name="version"]:checked').val(),
        text: $("#input_textarea").val()
    };
    return sendData(data);
}

$(document).ready(function(){
    $('#ajax_form').submit(function(event){
        return sendMyRequest(event);
    });
});
