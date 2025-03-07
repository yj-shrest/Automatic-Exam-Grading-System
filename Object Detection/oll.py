import ollama
from PIL import Image
from io import BytesIO
import base64
import os

# Function to encode the image to base64 for Ollama
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def query_llava(image_path, prompt):
    try:
        image_data = encode_image(image_path)

        response = ollama.chat(
            model='deepseek-r1:32b',
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
            stream=False  # Set to True for streaming output
        )

        return response['message']['content']
    except Exception as e:
        print(f"Error: {e}")
        return None


# Example usage
image_file = "image.png"  # Replace with the path to your image file
prompt = """You are a teacher checking Bachelor's in Engineering exam papers. You will be given a question, its full marks, and the answer given by the student. Your task is to grade the student's answer strictly, keeping in mind 
    the full marks allocated for the question.

    Be sure to evaluate the completeness, accuracy, and clarity of the student's response while being fair and consistent with the marks.

    QUESTION: 'What is artificial intelligence?'
    Full Marks: 5
    
    Student's Answer: 'Artificial Intelligence is the field of computer science focused on creating machines that can mimic human intelligence. It includes technologies like machine Learning and neural networtes. Enabling computers to perform tasks such as problem sowing, language translation and decision making. 
AI nas applications in various industries, promising effeciency and productivity improvements. 
However, ethical concerns like bias and job displacement require careful consideration. Balancing innovation with responsibility is crucial for maximizing the positive impact of AI on society.'"""  # Your prompt for LLaVA

if os.path.exists(image_file):
    output = query_llava(image_file, prompt)

    if output:
        print(f"LLaVA Output: {output}")
    else:
        print("Failed to get output from LLaVA.")
else:
    print(f"Error: Image file not found at {image_file}")