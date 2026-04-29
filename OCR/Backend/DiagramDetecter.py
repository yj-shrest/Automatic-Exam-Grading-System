from ultralytics import YOLO
from PIL import Image
from pdf2image import convert_from_path
import os
import cv2
import numpy as np

def detectDiagram(pdf_path):
    model = YOLO('../runs/detect/train11/weights/best.pt')
    images = convert_from_path(pdf_path)
    all_cropped_images = []
    updated_images = []
    for page_num, image in enumerate(images):
        print(f"Processing page {page_num + 1}/{len(images)}")
        results = model(image)
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                confidence = box.conf[0].item()
                class_id = int(box.cls[0].item())
                print(f"  Detected Diagram: Confidence = {confidence:.3f}, Bounding Box = ({x1}, {y1}, {x2}, {y2})")
        image_copy = image.copy()
        image_cv = cv2.cvtColor(np.array(image_copy), cv2.COLOR_RGB2BGR)
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cv2.rectangle(image_cv, (x1, y1), (x2, y2), color=(255, 255, 255), thickness=-1)
        image_copy = Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
        updated_images.append(image_copy)
        cropped_images = []
        tolerance = image.width / 15
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cropped_image = image.crop((x1 - tolerance, y1 - tolerance, x2 + tolerance, y2 + tolerance))
                cropped_images.append(cropped_image)
        all_cropped_images.extend(cropped_images)
    if not all_cropped_images:
        return "No diagrams detected in the entire PDF."
    else:
        return all_cropped_images, updated_images

if __name__ == "__main__":
    pdf_path = "diagrams.pdf"
    diagrams = detectDiagram(pdf_path)
    if isinstance(diagrams, list):
        print(f"Total diagrams detected: {len(diagrams)}")
        for i, diagram in enumerate(diagrams):
            print(f"Saving diagram {i+1}")
            diagram.save(f"diagram{i+1}.png")
    else:
        print("No diagrams")
