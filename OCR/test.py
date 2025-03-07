from ultralytics import YOLO
from PIL import Image
import cv2  #For visualization

# 1. Load Your Trained Model
# Replace 'path/to/your/best.pt' with the actual path to your trained model file
model = YOLO('runs/detect/train11/weights/best.pt') # Use path to your trained model!

# 2. Load the New Image
image_path = 'image.png'  # Replace with the path to your new image
image = Image.open(image_path)

# 3. Run Inference (Make Predictions)
results = model(image)  # Pass the PIL image to the model for inference

# 4. Process and Display Results
for result in results:  #Iterate over the results.  There might be multiple detected objects.
    boxes = result.boxes  # Get the detected bounding boxes
    for box in boxes:
        # Extract bounding box coordinates
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  # xyxy format

        # Get confidence score
        confidence = box.conf[0].item()

        # Get class ID (0 for "diagram" in your case)
        class_id = int(box.cls[0].item())  # Assuming "diagram" is class ID 0

        # Print the information
        print(f"Detected Diagram: Confidence = {confidence:.3f}, Bounding Box = ({x1}, {y1}, {x2}, {y2})")

        # Load the image with OpenCV (for drawing bounding boxes)
        img_cv = cv2.imread(image_path)

        # Draw the bounding box
        cv2.rectangle(img_cv, (x1, y1), (x2, y2), (0, 255, 0), 2) #Green rectangle

        # Add a label with the class name and confidence
        label = f"Diagram: {confidence:.2f}"
        cv2.putText(img_cv, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Show the image with detections
        cv2.imshow("Detections", img_cv)
        cv2.waitKey(0)  # Wait until a key is pressed to close the image
        cv2.destroyAllWindows()

# If no detections were made:
if not results:
    print("No diagrams detected in the image.")