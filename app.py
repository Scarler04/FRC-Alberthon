from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Your HTML file

@app.route('/pdf/<filename>')
def serve_pdf(filename):
    return send_from_directory('static/pdf', filename)

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='192.168.27.119', port=5000, debug=True)