from flask import Flask, render_template, send_from_directory, request, jsonify, send_file
import io
import os
from pathlib import Path
import json
from google.cloud import texttospeech
from google.cloud import translate_v2 as translate
import openai
from dotenv import load_dotenv

# Load the env vars in the .env file
load_dotenv()


app = Flask(__name__)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\remip\Clé\stately-diagram-460009-k6-e85f360cb898.json"
UPLOAD_FOLDER = r'templates\audio-temp'
ALLOWED_EXTENSIONS = {'webm', 'mp3', 'wav'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_places_top10(age:int,language:str,areacode:str):
    """
    inputs : 
        age : int
        language : string. (possible values : fr, ar, en, etc...)
        areacode : string

    Example : get_places_top10(45,"fr","78000")
    
    """
    with open("static\data-solinum\soliguide_response.json", "r") as f:
      document = json.load(f)
      accepted_places = []
      for place in document["places"]:
        agemax = place["publics"]["age"]["max"]
        languages = place["languages"]
        areacode_place = place.get('position', {}).get('codePostal', "non disponible")

        if agemax >= age and language in languages and areacode_place == areacode:
            accepted_places.append(place)
    return accepted_places[0]

        



def ask_question_with_audio(audio_path, dev_note=""):
    """Transcribe audio and get answer from OpenAI"""
    try:
        # Load your API key
        api_key = os.getenv('OPENAI_API_KEY')
        
        client = openai.OpenAI(api_key=api_key)
        
        # 1. Transcribe the audio question
        with open(audio_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                prompt=dev_note,
                response_format="text"
            )

        # 2. Get answer from ChatGPT
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """
        DEV NOTE: En te basant sur la transcription de la discussion :

        Pour chaque catégorie, donne la valeur correspondante, le tout sous form de json:

        1. Âge : Precis si donné, sinon, donne une approximation basée sur le contexte de la discussion. Si aucune information ne permet de scerner, dire 35.
        2. Langues : la langue parlée par la personne qui demande de l'aide pas la personne de la croix rouge et encodée (fr, ar, en, etc...). Sinon, français (fr) par défaut.
        3. Areacode : le code postal de la personne qui demande de l'aide 78000 par défaut.

        Format de réponse (exemple) :
        {"age" : 35,
        "langue" : "en",
        "areacode" : 75000}

        Répond uniquement sous forme de json compacte, sans phrases supplémentaires.
        """},
                {"role": "user", "content": transcription}
            ]
        )

        # 3. Get Suggestions
        json_string = response.choices[0].message.content
        # Convert string to JSON
        json_object = json.loads(json_string)

        # Extract age, language, and area code
        input_age = int(json_object.get('age', None))
        input_language = str(json_object.get('langue', None))
        input_areacode = str(json_object.get('areacode', None))

        get_places_top10_response = get_places_top10(input_age, input_language, input_areacode)
        output_top10 = json.dumps(get_places_top10_response, ensure_ascii=False)
        # Convert the response to JSON

        response_final = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """
                DEV NOTE: En te basant sur la transcription et les propositions de lieux formattent une réponse en markdown en classant chaque lieux par intérêt et en précisant uniquement les détails utiles.
                Formatage des réponses attendu :
                # Titres
                ## Sous-titres
                **Texte important** en gras  
                *Texte secondaire* en italique

                Listes :
                - Élément 1
                - Élément 2
                - Sous-élément

                Blocs de code :
                ```python
                print("Exemple pour les procédures")
                """},
                {"role": "user", "content": str(transcription+output_top10)}
            ]
        )

        
        return {
            "question": transcription,  # We won't use this but keeping it for debugging
            "answer": (response_final.choices[0].message.content)
        }

    except Exception as e:
        print(f"Error in audio processing: {str(e)}")
        return None


def ask_question(user_prompt):
    try:
        # Load your API key
        api_key = os.getenv('OPENAI_API_KEY')
        
        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""Tu es un assistant IA qui aide un bénévole de la Croix-Rouge française lors d’un entretien AEO (Accueil–Écoute–Orientation). Son rôle est de poser des questions ouvertes pour recueillir des informations sur les besoins et la situation de la personne. Ta réponse doit être concise, claire et fondée sur des faits. Tu dois te concentrer sur les besoins de la personne et éviter de donner des conseils ou des opinions personnelles mais tout en restant compatissant et sympathique. Si tu y as accès, base-toi sur le "Guide d’entretien Accueil-Écoute-Orientation", ainsi que sur le "RÉFÉRENTIEL D’ACTIVITÉ Permanence Accueil-Écoute-Orientation(PAEO)", et surtout sur le guidez technique de la croix rouge sur "L’ACCÈS AUX DROITS ET AUX SERVICES ACCOMPAGNER ET ORIENTER" et enfin également avec solinum/soliguide. Donne ta réponse en format markdown. Réponds à la question dans la langue utilisée dans la question. Si la question est en français, réponds en français. Si elle est en anglais, réponds en anglais. Si elle est dans une autre langue, réponds dans cette langue. Si tu ne comprends pas la question, dis simplement "Je ne comprends pas". Ne donne pas d'explications supplémentaires.
                Formatage des réponses attendu :
                # Titres
                ## Sous-titres
                **Texte important** en gras  
                *Texte secondaire* en italique

                Listes :
                - Élément 1
                - Élément 2
                - Sous-élément

                Blocs de code :
                ```python
                print("Exemple pour les procédures")
                """},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return {
            "question": user_prompt,
            "answer": response.choices[0].message.content
        }
    
    except Exception as e:
        print(f"Error in audio processing: {str(e)}")
        return None

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

@app.route('/process-audio', methods=['POST'])
def process_audio():
    try:
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_discussion.webm')
        
        if not os.path.exists(audio_path):
            return jsonify({'status': 'error', 'message': 'No audio file found'}), 400
            
        # Process the audio with your dev notes
        dev_notes = "DEV NOTE: This is for the French Red Cross. Provide clear, concise answers."
        result = ask_question_with_audio(audio_path, dev_notes)
        
        if not result:
            return jsonify({'status': 'error', 'message': 'Failed to process audio'}), 500
            
        return jsonify({
            'status': 'success',
            'answer': result['answer']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
@app.route('/ask-question', methods=['POST'])
def handle_question():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'status': 'error', 'message': 'No question provided'}), 400

        user_prompt = data['message']
        result = ask_question(user_prompt)
        
        if not result:
            return jsonify({'status': 'error', 'message': 'Failed to process question'}), 500
            
        return jsonify({
            'status': 'success',
            'answer': result['answer']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='127.0.0.1', port=5000, debug=True)


# ======================Other===========================

# DEV note for soliguide full api (excluding type of aid searched)
#f"""
# DEV NOTE: En te basant sur la transcription de la discussion :

# Pour chaque catégorie, liste toutes les valeurs possibles parmi les choix suivants, ou indique "non précisé" si aucune information :

# 1. Genre : femmes et hommes / femmes / hommes
# 2. Âge : enfants / adultes / seniors
# 3. Publics spécifiques : addiction / handicap / VIH / LGBT+ / sortants de prison / prostitution / étudiants / déplacés d'Ukraine / victimes de violence
# 4. Langues : liste des langues mentionnées
# 5. Situation administrative : tous / demandeurs d'asile / réfugiés / en situation régulière / sans-papiers
# 6. Situation familiale : tous / couples / familles / isolés / femmes enceintes
# 7. Accessibilité mobilité réduite : oui / non
# 8. Animaux acceptés : oui / non

# Format de réponse (exemple) :
# Genre : femmes, hommes
# Âge : adultes
# Publics spécifiques : étudiants, LGBT+
# Langues : français, anglais
# ...

# Répond uniquement sous forme de liste compacte, sans phrases supplémentaires.
# """
