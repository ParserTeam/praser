var pageLoaded = true;
var textArea = document.getElementById("input_textarea");

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

function onResponse(btn){
    $("#inf2").html(btn);
    pageLoaded = true;
    document.getElementById("loader").style.display = "none";
}

function sendData() {
    console.log("MY TEXT" + textArea.textContent)

    var data = {
        version: $('input[name="version"]:checked').val(),
        text: $("#input_textarea").val()
    };
    $.post("/cgi-bin/Controler.py", data, onResponse);
    pageLoaded = false;
    show_log();
    return false;
}

function addFilesTextToInput(files) {
    var end = files.length;
    var input = $("#input_textarea");

    input.val("");
    for (var i = 0, f; f = files[i]; i++) {
        var reader = new FileReader();

        if (!f.type.match('text*')) {
            continue;
        }

        reader.onload = (function(theFile) {
            return function(e) {
                // Render thumbnail.
                    input.val(input.val() + e.target.result + "\n\n");
                end--;
                if (end === 0)
                    sendData();
            };
        })(f);
        reader.readAsText(f);
    }
}

function textareaChanged() {
    setTimeout(function () { sendData(); }, 100);
}

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
textArea.addEventListener('dragover', handleDragOver, false);
textArea.addEventListener('drop', handleFileDrop, false);
