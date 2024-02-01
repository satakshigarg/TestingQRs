from flask import Flask, render_template, request, redirect, send_file
import qrcode
import os
import requests

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def upload_to_fileio(file_path):
    fileio_url = 'https://file.io/'
    files = {'file': open(file_path, 'rb')}
    response = requests.post(fileio_url, files=files)
    file_info = response.json()

    return file_info['link']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        # Save the uploaded PDF file locally
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)

        # Upload the PDF file to File.io
        fileio_link = upload_to_fileio(pdf_path)

        # Generate QR code for the File.io link
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(fileio_link)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Save the QR code image
        qr_path = os.path.join(app.config['UPLOAD_FOLDER'], 'qrcode.png')
        qr_img.save(qr_path)

        return render_template('upload.html', qr_path=qr_path)

@app.route('/download/<filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
