from paddleocr import PaddleOCR
import cv2
import numpy as np

# Function to preprocess the image
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Reduce noise using Gaussian blur
    # blur = cv2.GaussianBlur(thresh, (2, 2), 0)
    
    # Resize image for better OCR accuracy
    img_resized = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    cv2.imshow('Preprocessed Image', img_resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return img_resized

# Function to perform OCR and apply spell correction
def perform_ocr(image_path):
    processed_img = preprocess_image(image_path)
    image = cv2.imread(image_path)
    # Initialize PaddleOCR with optimized parameters
    ocr = PaddleOCR(use_angle_cls=True, lang='en', rec_algorithm='CRNN', det_db_box_thresh=0.5)
    
    # Perform OCR
    result = ocr.ocr(image, cls=True)
    corrected_words = []
    for line in result:
        for word_info in line:
            corrected_word = word_info[1][0]
            corrected_words.append(corrected_word)
    
    return corrected_words

# Path to input image
image_path = 'assets/image.png'

# Run OCR and get corrected text
text_result = perform_ocr(image_path)

# Print final OCR results
print("Corrected OCR Text:")
print(' '.join(text_result))