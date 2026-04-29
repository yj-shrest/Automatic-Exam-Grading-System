import ollama
from PIL import Image
from io import BytesIO
import base64
import os
from google import genai
from pydantic import BaseModel
import re
import json
class score(BaseModel):
    score : float
    comment: str
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
def check_answer(question,relevant_text,ideal_answer,answer,full_marks):
    print(relevant_text)
    print(answer)
    try:
        prompt = f"""You will be given a question,the relevant text, its full marks,may be an ideal answer and the answer given by the student. Your task is to grade the student's answer strictly, keeping in mind 
                the full marks allocated for the question.The relevant text may or may not be relevant to the question, it is from a book. The answer is extracted using OCR so NEGLECT ANY FORMATTING ISSUES or SPELLING ERRORS.
                Be sure to evaluate the completeness, accuracy, and clarity of the student's response while being fair and consistent with the marks.

                QUESTION: '{question}'
                Relevant Text: '{relevant_text}'
                Ideal Answer: '{ideal_answer}'
                Full Marks: '{full_marks}'
                Student's Answer: '{answer}'
                
                Give the response in the json format:
                score:3, comment:"justification"
                """  
        response = ollama.chat(
            model='koesn/mistral-7b-instruct:latest',
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
            stream=False  
        )
        print(response['message']['content'])
        text = response['message']['content']
        text = text.replace("json", "").replace("`", "").strip()
        match = re.search(r'{(.*?)}', text)
        if match:
            text = match.group(1)
        temp = json.loads(text)
        print(temp)
        return temp
    except Exception as e:
        print(f"Error: {e}")
        return None

def gradeDiagram(question, diagrams, full_marks):
    gemini_api_key = "AIzaSyAFSjqpFOK2aG1jilF5RciOpjNbQYNi4cE"
    if not gemini_api_key:
        raise ValueError("Gemini API Key not provided. Please provide GEMINI_API_KEY as an environment variable")
    client = genai.Client(api_key=gemini_api_key)
    contents = []
    contents.extend(diagrams) 
    prompt = (
     f"""The question is '{question}' and the following diagrams were included in the answer by the student, only judge the 
     diagram if it is relevant to the question, correct, accurate and complete and give it a score out of {full_marks}""")
    contents.append(prompt) 

    response = client.models.generate_content(
    model="gemini-1.5-pro",
    contents=contents,
    config={
        'response_mime_type': 'application/json',
        'response_schema': score,
    })
    print("response:"+ response.text)
    parsed_data = json.loads(response.text)
    print(parsed_data)
    return parsed_data['score']

def check_answer_gemini (question,relevant_text,ideal_answer,answer,full_marks):
    gemini_api_key = "AIzaSyAFSjqpFOK2aG1jilF5RciOpjNbQYNi4cE"
    if not gemini_api_key:
        raise ValueError("Gemini API Key not provided. Please provide GEMINI_API_KEY as an environment variable")
    client = genai.Client(api_key=gemini_api_key)
    print(relevant_text)
    print(answer)
    try:
        prompt = f"""You will be given a question,the relevant text, its full marks,may be an ideal answer and the answer given by the student. Your task is to grade the student's answer strictly, keeping in mind 
                the full marks allocated for the question.The relevant text may or may not be relevant to the question, it is from a book. The answer is extracted using OCR so NEGLECT ANY FORMATTING ISSUES or SPELLING ERRORS.
                Be sure to evaluate the completeness, accuracy, and clarity of the student's response while being fair and consistent with the marks.

                QUESTION: '{question}'
                Relevant Text: '{relevant_text}'
                Ideal Answer: '{ideal_answer}'
                Full Marks: '{full_marks}'
                Student's Answer: '{answer}'
                
                Give the response in the json format:
                grade:3, comment:"justification"
                """ 
        response = client.models.generate_content(
            model="gemini-1.5-pro",
            contents=[prompt],
            config={
                'response_mime_type': 'application/json',
                'response_schema': score,
            })
        print(response.text)
        parsed_data = json.loads(response.text)
        return parsed_data
    except Exception as e:
        print(f"Error: {e}")
        return None