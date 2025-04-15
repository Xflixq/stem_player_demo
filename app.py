from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_cors import CORS
import os
import subprocess
from pydub import AudioSegment

UPLOAD_FOLDER = 'uploads'
STEM_FOLDER = 'stems'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a'}

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STEM_FOLDER'] = STEM_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STEM_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Run spleeter separation (4 stems: vocals, drums, bass, other)
        subprocess.run([
            'spleeter', 'separate',
            '-p', 'spleeter:4stems',
            '-o', app.config['STEM_FOLDER'],
            filepath
        ])

        song_name = os.path.splitext(filename)[0]
        return jsonify({'message': 'Stems generated', 'path': f'/stems/{song_name}/'})

@app.route('/stems/<song>/<stem>')
def get_stem(song, stem):
    path = os.path.join(app.config['STEM_FOLDER'], song)
    return send_from_directory(path, stem)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
