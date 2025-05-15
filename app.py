from flask import Flask, render_template, send_from_directory, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Your HTML file

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
        # text_out = traductor(lang_in, lang_out, text_in)
        
        return jsonify({
            'translation': "bonjour, test",
            'status': 'success'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def traductor(lang_in: str, lang_out: str, text_in: str) -> str:
    # Replace this with your actual translation logic
    # This is just a placeholder
    return "Bonjour, test"

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='192.168.27.119', port=5000, debug=True)