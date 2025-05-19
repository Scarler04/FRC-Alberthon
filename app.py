from flask import Flask, render_template, send_from_directory, request, jsonify, send_file
import pyttsx3
import io
import os
from datetime import datetime
from google.cloud import texttospeech
from google.cloud import translate_v2 as translate
from werkzeug.utils import secure_filename




app = Flask(__name__)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\remip\Clé\stately-diagram-460009-k6-e85f360cb898.json"
UPLOAD_FOLDER = r'C:\Users\remip\Python\2024-2025\Alberthons\French Red Cross\test2\templates'
ALLOWED_EXTENSIONS = {'webm', 'mp3', 'wav'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdf/<filename>')
def serve_pdf(filename):
    return send_from_directory('static/pdf', filename)

@app.route('/translate', methods=['POST'])
def handle_translation():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        lang_in = data.get('lang_in')
        lang_out = data.get('lang_out')
        text_in = data.get('text_in')

        if not all([lang_in, lang_out, text_in]):
            return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400

        # Call your translation function
        text_out = traductor(lang_in, lang_out, text_in)

        return jsonify({
            'translation': text_out,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def traductor(lang_in: str, lang_out: str, text_in: str) -> str:
    client = translate.Client()

    result = client.translate(
        text_in,
        source_language=lang_in,
        target_language=lang_out,
        format_='text'  # or 'html' if the input contains HTML
    )

    return result['translatedText']


def generate_speech_google(text, language_code='en-US'):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Paramètres de la voix (neutre par défaut)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Format de sortie MP3
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Appel à l'API
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    return response.audio_content

@app.route('/generate-speech', methods=['POST'])
def handle_speech_request():
    data = request.get_json()
    text = data.get('text')
    language_code = data.get('language_code', 'en')  # Par défaut anglais

    if not text:
        return jsonify({'error': 'Aucun texte fourni'}), 400

    try:
        audio_content = generate_speech_google(text, language_code)
        return send_file(
            io.BytesIO(audio_content),
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="speech.mp3"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/save-recording', methods=['POST'])
def save_recording():
    if 'audio' not in request.files:
        return jsonify({'status': 'error', 'message': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    
    if audio_file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    if audio_file and allowed_file(audio_file.filename):
        # Define the filename you want to save as
        filename = 'temp_discussion.webm'
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save the file (this will overwrite existing file)
        audio_file.save(save_path)
        
        return jsonify({
            'status': 'success',
            'message': 'File saved successfully',
            'path': save_path
        })
    
    return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='127.0.0.1', port=5000, debug=True)
    # app.run(host='172.16.29.223', port=5000, debug=True)