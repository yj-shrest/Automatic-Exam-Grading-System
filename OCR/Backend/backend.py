from flask import Flask, jsonify
from flask_cors import CORS
from flask import request
from RAGG import encode_and_save, retrieve_pages
import os
from PyPDF2 import PdfReader
from ocr import ocr_pdf
from LLM import check_answer,gradeDiagram,check_answer_gemini
from DiagramDetecter import detectDiagram
import os
import torch
import numpy as np
from transformers import AutoProcessor, AutoModelForCausalLM
import requests
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

print(f"Using {'GPU' if device == 'cuda:0' else 'CPU'}")

model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Florence-2-large-ft", torch_dtype=torch_dtype, trust_remote_code=True
).to(device)
processor = AutoProcessor.from_pretrained("microsoft/Florence-2-large-ft", trust_remote_code=True)
@app.route('/')
def home():
    return jsonify(message="Welcome to the Flask backend with CORS enabled!")

@app.route('/count', methods=['POST'])
def pageCount():
    if 'file' not in request.files:
        return jsonify(error="Missing file"), 400

    file = request.files['file']
    pdf_reader = PdfReader(file)
    num_pages = len(pdf_reader.pages)
    return jsonify(num_pages=num_pages)

@app.route('/add_database', methods=['POST'])
def add_database():
    if 'file' not in request.files or 'database_name' not in request.form:
        return jsonify(error="Missing file, database path, or database name"), 400

    file = request.files['file']
    database_name = request.form['database_name']
    database_path = 'Database/' + '_'.join(database_name.split(' '))+ '/'
    os.makedirs(database_path, exist_ok=True)
    filename = '_'.join(database_name.split(' ')) 
    file.save(database_path + filename + '.pdf')
    encode_and_save(filename)
    return jsonify(message="Database created")

@app.route('/all_databases', methods=['GET'])
def all_databases():
    return jsonify(databases=[os.listdir('Database')])

@app.route('/subjective', methods=['POST'])
def subjectiveGrade():
    if 'question' not in request.form or 'answer' not in request.files or 'database_name' not in request.form:
        return jsonify(error="Missing question, answer, or database name"), 400
    answer_file = request.files['answer']
    question= request.form['question']
    database_name = request.form['database_name']
    full_marks = request.form['full_marks']
    ideal_answer = request.form['ideal_answer']
    filename = '_'.join(database_name.split(' '))

    os.makedirs('temp/', exist_ok=True)
    answer_file.save('temp/' + filename + '_answer.pdf')
    diagrams,updated_images = detectDiagram('temp/' + filename + '_answer.pdf')
    relevant_pages = retrieve_pages(question, filename,1)
    relevant_text = ' '.join(relevant_pages)
    comment = 'Placeholder Comment'
    if  isinstance(diagrams, list):
        answer = ocr_pdf('temp/' + filename + '_answer.pdf',model, processor, device, torch_dtype,updated_images)
        print("Diagram Present, Using hybrid Mode for Evaluation")
        diagramScore = gradeDiagram(question,diagrams,float(full_marks)*0.3)
        print(diagramScore)
        textGrade = check_answer(question,relevant_text,ideal_answer,answer,float(full_marks)*0.7)
        # print(diagramScore, "+", textGrade['grade'])
        grade = diagramScore + textGrade['score']
        comment = textGrade['comment']
    else:
        answer = ocr_pdf('temp/' + filename + '_answer.pdf',model, processor, device, torch_dtype)
        print("No diagram evaluating text only")
        textGrade = check_answer(question,relevant_text,ideal_answer, answer,full_marks)
        grade = textGrade['score']
    return jsonify(grade=grade,comment= comment)

if __name__ == '__main__':
    app.run(debug=True,port=5000)