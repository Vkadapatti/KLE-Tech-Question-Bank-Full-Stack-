from flask import Flask, render_template, request, redirect, send_file
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import os, datetime

app = Flask(__name__)
app.secret_key = 'supersecret'  # for flash messages
app.config['UPLOAD_FOLDER'] = 'uploads'

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["KLE_QBANK"]
collection = db["files"]

# Create folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    files = list(collection.find())
    return render_template('dashboard.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file or file.filename == '':
        return redirect('/')
    
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    collection.insert_one({
        "filename": filename,
        "type": file.content_type,
        "size": round(os.path.getsize(save_path) / 1024, 2),
        "upload_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_path": save_path
    })
    return redirect('/')

@app.route('/download/<file_id>')
def download_file(file_id):
    file_record = collection.find_one({"_id": ObjectId(file_id)})
    if file_record:
        return send_file(file_record['file_path'], as_attachment=True, download_name=file_record['filename'])
    return redirect('/')

@app.route('/delete/<file_id>')
def delete_file(file_id):
    file_record = collection.find_one({"_id": ObjectId(file_id)})
    if file_record:
        if os.path.exists(file_record['file_path']):
            os.remove(file_record['file_path'])
        collection.delete_one({"_id": ObjectId(file_id)})
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
