from flask import Flask, render_template, request, jsonify
import os
import wave
import pyaudio
from openai import OpenAI
import ssl
import threading

app = Flask(__name__)

# Initialize OpenAI client 
client = OpenAI(api_key="hiddenfrompublic")


# SSL bypass for OpenAI API (only for development)
ssl._create_default_https_context = ssl._create_unverified_context

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
AUDIO_FILE = "audio/conversation.wav"
TRANSCRIPT_FILE = "generated/transcript.txt"
MEDICAL_NOTE = "generated/medicalnote.txt"

recording = False
frames = []
stream = None
audio = pyaudio.PyAudio()

def record_audio():
    global frames, stream, audio, recording

    # Open the audio stream
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)
    
    frames = []
    while recording:
        data = stream.read(CHUNK)
        frames.append(data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording

    # Set recording flag to True
    recording = True
    # Start recording in a separate thread
    thread = threading.Thread(target=record_audio)
    thread.start()

    return jsonify({"message": "Recording started"}), 200

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording, frames, stream, audio

    # Set recording flag to False to stop recording
    recording = False

    # Close the audio stream
    stream.stop_stream()
    stream.close()

    # Save the recorded audio to a WAV file
    if not os.path.exists('audio'):
        os.makedirs('audio')

    with wave.open(AUDIO_FILE, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    return jsonify({"message": "Recording stopped", "filename": AUDIO_FILE}), 200

@app.route('/generate_note', methods=['POST'])
def generate_note():
    transcript = transcribe_audio(AUDIO_FILE)
    medical_note = generate_medical_note_from_transcript(transcript)

    return jsonify({"transcript": transcript, "medical_note": medical_note})



# Transcribe the recorded audio (Whisper)
def transcribe_audio(audio_file):
    with open(audio_file, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    
    # Save the transcript
    with open(TRANSCRIPT_FILE, 'w', encoding='utf-8') as f:
        f.write(transcription.text)

    return transcription.text

# Generate SOAP note using GPT-4
def generate_medical_note_from_transcript(transcript):
    prompt = (
        "**You are an outstanding charting assistant** The user is going to give you a transcript of a doctor and patient visit. You must carefully take the transcript and generate a comprehensive medical note for the clinician and deliver it to them so they can update their EMR system. This patient note must adhere to the standard SOAP note format. Here are your instructions for the note: **First, analyze the transcript between a patient and doctor during their visit. The doctor may also add information to the transcript if further detail is needed in the patient record** Format the patient note like so: - Subjective: Chief Complaint: (A brief statement of the patient's reason for the visit or the primary issue they are facing) History of Present Illness: (Be extremely detailed. Clearly document all symptoms, relevant history, and details about current medical symptoms, including duration, severity, and any triggering events) (Include any past medical conditions, surgeries, allergies, medications, and family medical history discussed during the conversation) (Document the patient's current medications, dosages, and any allergies or adverse reactions to medications) (Include information about the patient's lifestyle, such as smoking, alcohol consumption, exercise, and diet, if relevant) (Be as comprehensive as possible, utilize all the information in the transcript in order to deliver a very detailed, gold-standard patient note) - Objective: Vital Signs: (Record the patient's vital signs, including blood pressure, heart rate, respiratory rate, temperature, and any additional measurements) Physical Examination Findings: (Document findings from the physical examination, including any abnormalities, tenderness, or relevant clinical signs) Laboratory and Diagnostic Results: (Include any relevant laboratory tests, imaging studies, or other diagnostic results, providing details of the results if available) Assessment of Systems: (State the assessment of various body systems, including cardiovascular, respiratory, gastrointestinal, etc., based on the conversation and physical examination. Document these clearly and list every system mentioned on the transcript) (Never miss key details and medical findings. Make this portion detailed) - Assessment: Diagnosis: (Provide a professional analysis of the patient's medical condition and any applicable differential diagnoses based on the conversation and examination) Clinical Impressions: (Discuss the physician's overall impressions of the patient's health status and any concerns or areas of focus) - Plan: Treatment Plan: (Outline the management and treatment plan discussed during the visit, including medications prescribed, therapies recommended, and any referrals to specialists or additional diagnostic tests. Extract all relevant information directly from the transcript) Patient Education: (Include all educational information provided to the patient regarding their condition, medications, or lifestyle modifications. List patient instructions distinctly and clearly) Follow-up: (Specify the date and nature of the next follow-up appointment or any required monitoring) - Patient Follow-up Note: (Generate a follow-up note addressed to the patient. The note should include: 1. A brief summary of the diagnosis or condition discussed during the visit. 2. Clear instructions for care at home, including any medications prescribed, their dosages, and how to take them. 3. Specific 'homework' for the patient - this could be exercises, dietary recommendations, symptom monitoring, or anything else relevant to their condition and recovery. 4. Discharge information, if applicable, detailing any follow-up appointments, when and how to seek further medical advice, and under what circumstances they should return to the clinic or emergency department. 5. Encouragement for the patient to follow through with the plan, emphasizing the importance of their active participation in their recovery process. Ensure the tone is warm, supportive, and easy for the patient to understand) — - Other instructions: * Never repeat yourself. Always send the note right away. * Ensure your SOAP note is coherent and comprehensive, utilizing all of the information extracted from the transcript. * Do not skip any medical findings or observations from the doctor. * Always include all medication and prescriptions that were mentioned in the transcript and include full context, dosage, and relevant information regarding the prescription. * Use professional and appropriate medical terminology. * The contents of each section should be meticulously organized and documented in the correct sections. Each section of the SOAP note should have a bolded title. * NEVER CREATE YOUR OWN TRANSCRIPT. Only use the transcript for extracting information for the SOAP note. * If the user is not sending a transcript, also remind them to start a \"New Visit\" and remind them to remember to click the mic to start recording and again to stop. In order to get their SOAP notes, they need to press enter or send the transcript with the send button. * Never produce more than one patient note. Ensure only one note is delivered to the user."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": prompt}, 
                {"role": "user", "content": transcript}
            ]
        )
        medical_note = response.choices[0].message.content

        # Save medical note
        with open(MEDICAL_NOTE, 'w') as f:
            f.write(medical_note)

        return medical_note
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    if not os.path.exists("audio"):
        os.makedirs("audio")
    if not os.path.exists("generated"):
        os.makedirs("generated")

    app.run(debug=True)



