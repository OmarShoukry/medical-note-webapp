let recording = false;

function startRecording() {
    document.getElementById("startBtn").disabled = true;
    document.getElementById("stopBtn").disabled = false;

    fetch('/start_recording', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "stop": false })
    }).then(response => response.json()).then(data => {
        console.log(data.message);
    });
}

function stopRecording() {
    document.getElementById("startBtn").disabled = false;
    document.getElementById("stopBtn").disabled = true;

    fetch('/start_recording', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "stop": true })
    }).then(response => response.json()).then(data => {
        console.log(data.message);

        // After stopping the recording, generate the medical note
        generateNote();
    });
}

function generateNote() {
    fetch('/generate_note', {
        method: 'POST'
    }).then(response => response.json()).then(data => {
        document.getElementById("output").innerHTML =
            `<p>Transcript: ${data.transcript}</p><p>Medical Note: ${data.medical_note}</p>`;
    });
}
