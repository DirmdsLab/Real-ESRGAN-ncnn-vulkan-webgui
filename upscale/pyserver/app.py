import os
import shutil
import subprocess
import zipfile
import io
import time
from flask import Flask, render_template, request, jsonify, Response, send_from_directory, send_file
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)

# Path Configuration

SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SERVER_DIR)

ESRGAN_DIR = os.path.join(
    ROOT_DIR,
    "realesrgan-ncnn-vulkan-20220424-ubuntu"
)

BIN_PATH = os.path.join(
    ESRGAN_DIR,
    "realesrgan-ncnn-vulkan"
)

INPUT_DIR = os.path.join(SERVER_DIR, "input")
OUTPUT_DIR = os.path.join(SERVER_DIR, "output")

# Validate binary

if not os.path.isfile(BIN_PATH):
    raise FileNotFoundError(
        f"Real-ESRGAN binary not found: {BIN_PATH}"
    )

# STRICT SECURITY WHITELISTS
ALLOWED_MODELS = [
    "realesr-animevideov3",
    "realesrgan-x4plus",
    "realesrgan-x4plus-anime",
    "realesrnet-x4plus"
]
ALLOWED_SCALES = ["2", "3", "4"]

# Clear input & output folders on startup
for folder in [INPUT_DIR, OUTPUT_DIR]:
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files')
    saved_files = []
    
    for file in files:
        if file.filename == '':
            continue
        filename = secure_filename(file.filename)
        file.save(os.path.join(INPUT_DIR, filename))
        saved_files.append(filename)
        
    return jsonify({'success': True, 'files': saved_files})

@app.route('/stream-upscale')
def stream_upscale():
    filenames = request.args.getlist('files')
    
    # SECURITY VALIDATION: Model Name
    user_model = request.args.get('model', 'realesrgan-x4plus-anime')
    model_name = user_model if user_model in ALLOWED_MODELS else 'realesrgan-x4plus-anime'
    
    # SECURITY VALIDATION: Scale Ratio
    user_scale = request.args.get('scale', '4')
    scale_val = user_scale if user_scale in ALLOWED_SCALES else '4'
    
    def generate():
        for filename in filenames:
            name, _ = os.path.splitext(filename)
            
            # Generate a clean timestamp (YYYYMMDD-HHMMSS)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            out_filename = f"{name}_upscale-{timestamp}.png" 
            
            yield f"data: [INFO] Starting process for {filename} using model [{model_name}] with scale [{scale_val}x]...\n\n"
            
            cmd = [
                BIN_PATH,
                "-i", os.path.join(INPUT_DIR, filename),
                "-s", scale_val,
                "-n", model_name,
                "-o", os.path.join(OUTPUT_DIR, out_filename)
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=ESRGAN_DIR
            )
            
            for line in process.stdout:
                cleaned_line = line.strip()
                if cleaned_line:
                    yield f"data: {cleaned_line}\n\n"
            
            process.wait()
            
            if process.returncode == 0:
                # Return both original and output filename separated by pipe to map them in frontend
                yield f"data: SUCCESS:{filename}|{out_filename}\n\n"
            else:
                yield f"data: FAILED:{filename}\n\n"
                
        yield "data: ALL_DONE\n\n"

    return Response(generate(), mimetype='text/event-stream')

# Route to fetch original files from input directory
@app.route('/input/<filename>')
def download_input(filename):
    return send_from_directory(INPUT_DIR, filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

# Modified Preview Endpoint to handle both input and output folders
@app.route('/preview/<folder_type>/<filename>')
def preview_file(folder_type, filename):
    target_dir = INPUT_DIR if folder_type == "input" else OUTPUT_DIR
    file_path = os.path.join(target_dir, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        img = Image.open(file_path)
        img.thumbnail((80, 80))
        
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-zip')
def download_zip():
    filenames = request.args.getlist('files')
    if not filenames:
        return jsonify({'error': 'No files to zip'}), 400
    
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename in filenames:
            file_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(file_path):
                zipf.write(file_path, filename)
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='upscaled_anime_batch.zip'
    )

if __name__ == '__main__':
    print("===================================")
    print("Real-ESRGAN WebGUI")
    print("===================================")
    print(f"SERVER_DIR : {SERVER_DIR}")
    print(f"ROOT_DIR   : {ROOT_DIR}")
    print(f"ESRGAN_DIR : {ESRGAN_DIR}")
    print(f"BIN_PATH   : {BIN_PATH}")
    print(f"INPUT_DIR  : {INPUT_DIR}")
    print(f"OUTPUT_DIR : {OUTPUT_DIR}")
    print("===================================")

    app.run(
        host="0.0.0.0",
        port=5011,
        debug=False
    )