from ultralytics import YOLO
from PIL import Image
from pdf2image import convert_from_path
import os

def detectDiagram(pdf_path):
    """
    Detects diagrams in each page of a PDF, crops them, and returns a list of cropped images.
    """
    model = YOLO('../runs/detect/train11/weights/best.pt')  # Use path to your trained model!

    # 1. Convert PDF to a List of Images
    images = convert_from_path(pdf_path)
    all_cropped_images = []  # To store cropped images from all pages

    # 2. Iterate through Each Page (Image)
    for page_num, image in enumerate(images):
        print(f"Processing page {page_num + 1}/{len(images)}")

        # 3. Run Inference (Make Predictions)
        results = model(image)  # Pass the PIL image to the model for inference

        # 4. Process and Display Results (per page)
        for result in results:  # Iterate over the results.  There might be multiple detected objects.
            boxes = result.boxes  # Get the detected bounding boxes
            for box in boxes:
                # Extract bounding box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  # xyxy format

                # Get confidence score
                confidence = box.conf[0].item()

                # Get class ID (0 for "diagram" in your case)
                class_id = int(box.cls[0].item())  # Assuming "diagram" is class ID 0

                # Print the information
                print(f"  Detected Diagram: Confidence = {confidence:.3f}, Bounding Box = ({x1}, {y1}, {x2}, {y2})")

        # 5. Crop and Save (Append to the List)
        cropped_images = []
        tolerance = image.width / 15

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cropped_image = image.crop((x1 - tolerance, y1 - tolerance, x2 + tolerance, y2 + tolerance))
                cropped_images.append(cropped_image)
        all_cropped_images.extend(cropped_images)  # Add to the overall list

    # 6. Return Final Result
    if not all_cropped_images:
        return "No diagrams detected in the entire PDF."
    else:
        return all_cropped_images

if __name__ == "__main__":
    pdf_path = "diagrams.pdf"  # Make sure to replace with your PDF file path
    diagrams = detectDiagram(pdf_path)

    if isinstance(diagrams, list):
        print(f"Total diagrams detected: {len(diagrams)}")
        for i, diagram in enumerate(diagrams):
            print(f"Saving diagram {i+1}")
            # Save the diagram
            diagram.save(f"diagram{i+1}.png")  # Save each diagram

    else:
        print("No diagrams")