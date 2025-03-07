gemini_api_key = "AIzaSyAFSjqpFOK2aG1jilF5RciOpjNbQYNi4cE"
from google import genai
import PIL.Image
import cv2
import matplotlib.pyplot as plt
import numpy as np
from pydantic import BaseModel
import re
import json
class box(BaseModel):
    x1 : int
    y1 : int
    x2 : int
    y2 : int

class Objects(BaseModel):
  box : list[int]

image = PIL.Image.open('image.png')

client = genai.Client(api_key=gemini_api_key)

prompt = (
  """Return a bounding box for the diagram or figure in this answer sheet image.
  if the diagram or figure is not present, return an empty bounding box.""")

response = client.models.generate_content(
  model="gemini-1.5-pro",
  contents=[image, prompt],
  config={
        'response_mime_type': 'application/json',
        'response_schema': box,
    })
print(response.text)
parsed_data = json.loads(response.text)
coordinates = [parsed_data["x1"], parsed_data["y1"], parsed_data["x2"], parsed_data["y2"]]
x1, y1, x2, y2 = coordinates


# Convert PIL image to OpenCV format
image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

# Draw the bounding box on the image
cv2.rectangle(image_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)

# Convert OpenCV image back to RGB format for displaying with matplotlib
image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)

# Display the image with the bounding box
plt.imshow(image_rgb)
plt.axis('off')
plt.show()