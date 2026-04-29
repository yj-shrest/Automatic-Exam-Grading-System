from flask import Flask, jsonify
from flask_cors import CORS
from flask import request
from DetectTick import detect, detect_multiple
from pdf2image import convert_from_path
import os
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return jsonify(message="Welcome to the Flask backend with CORS enabled!")
@app.route('/convert_pdf', methods=['POST'])
def convert_pdf():
    file = request.files['file']
    filepath = "uploads/new.pdf"
    file.save(filepath)

    images = convert_from_path(filepath)
    image_urls = []

    for i, image in enumerate(images):
        img_path = f'static/{file.filename}_page_{i+1}.jpg'
        image.save(img_path, 'JPEG')
        image_urls.append(f'/static/{file.filename}_page_{i+1}.jpg')

    return jsonify({"images": image_urls})
@app.route('/mcq', methods=['POST'])
def process_images():
    if 'questionImage' not in request.files or 'answerPdf' not in request.files or 'answerKey' not in request.form:
        return jsonify(error="Missing image or text"), 400

    image1 = request.files['questionImage']
    text = request.form['answerKey']

        # Process the images and text here
    # For example, you can save the images and print the text
    image1.save('image1.png')
    print(text)
    Answer_Key = {index + 1: char for index, char in enumerate(text)}
    Detected = detect_multiple('image1.png', 'uploads/new.pdf',Answer_Key)
    print("Detected ticks", Detected)
    print(Answer_Key)
    return jsonify(Detected=Detected) 

if __name__ == '__main__':
    app.run(debug=True,port=5001)