# Medical Note Generator Web App

This project is a simple web application that allows users to record audio through their microphone, save it to a .wav file, and process it for further use (e.g., medical note generation). 
The app is built using Flask for the backend and HTML/JavaScript for the frontend.

## Features

* Start and stop recording with a simple button interface.
* Records audio and saves it as a .wav file.
* Generates a transcript and medical note saved as .txt files.
* Frontend built with HTML and JavaScript.
* Backend using Flask and PyAudio for audio processing.

## Installation

1. Clone the repository

 `git clone https://github.com/OmarShoukry/medical-note-webapp.git`

2. Install dependencies:

 `pip install -r requirements.txt`

3. Run the Flask app:

 `python3 app.py`

4. Open your browser and navigate to:

 [(http://127.0.0.1:5000)](http://127.0.0.1:5000)

## Usage 

* Start Recording: Click the "Start Recording" button to begin recording audio.

* Stop Recording: Click the "Stop Recording" button to stop, the audio will be saved as `audio/conversation.wav`, a transcript will be saved as `generated/transcript.txt` and an SOAP format medical note will be saved as `generated/medicalnote.txt`
