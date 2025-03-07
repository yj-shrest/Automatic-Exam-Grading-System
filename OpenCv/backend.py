from flask import Flask, jsonify
from flask_cors import CORS
from flask import request
from DetectTick import detect
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return jsonify(message="Welcome to the Flask backend with CORS enabled!")

@app.route('/mcq', methods=['POST'])
def process_images():
    if 'questionImage' not in request.files or 'answerImage' not in request.files or 'answerKey' not in request.form:
        return jsonify(error="Missing image or text"), 400

    image1 = request.files['questionImage']
    image2 = request.files['answerImage']
    text = request.form['answerKey']

        # Process the images and text here
    # For example, you can save the images and print the text
    image1.save('image1.png')
    image2.save('image2.png')
    print(text)
    Answer_Key = {index + 1: char for index, char in enumerate(text)}
    Detected = detect('image2.png', 'image1.png')
    print("Detected ticks", Detected)
    print(Answer_Key)
    score = 0
    for i in Detected:
        for key in i:
            if Answer_Key[key].lower() == i[key][0].lower():
                score += 1
                print(key)
    print("Score: ", score)
    return jsonify(score=score) 

if __name__ == '__main__':
    app.run(debug=True,port=5001)