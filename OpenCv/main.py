from paddleocr import PaddleOCR
import json

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Use English model

# Path to your image
image_path = 'mcq.png'

# Perform OCR
results = ocr.ocr(image_path, cls=True)

# Prepare data structure to store results
ocr_data = []

# Loop through detected text lines
for line in results[0]:  # results[0] contains detected text lines
    bounding_box = line[0]  # Bounding box coordinates
    text = line[1][0]       # Detected text
    confidence = line[1][1] # Confidence score

    # Append to the data structure
    ocr_data.append({
        "text": text,
        "bounding_box": bounding_box,
        "confidence": confidence
    })

# Save to JSON file
output_path = 'ocr_results.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(ocr_data, f, ensure_ascii=False, indent=4)

print(f"OCR results saved to {output_path}")
