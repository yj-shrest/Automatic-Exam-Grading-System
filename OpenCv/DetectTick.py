import cv2
import numpy as np
import matplotlib.pyplot as plt
from paddleocr import PaddleOCR

def align_images(base_image, align_image):
    """
    Aligns align_image to base_image using feature matching and homography.
    """
    # Convert images to grayscale
    gray_base = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
    gray_align = cv2.cvtColor(align_image, cv2.COLOR_BGR2GRAY)

    # Detect SIFT keypoints and descriptors
    sift = cv2.SIFT_create()
    keypoints1, descriptors1 = sift.detectAndCompute(gray_base, None)
    keypoints2, descriptors2 = sift.detectAndCompute(gray_align, None)

    # Match descriptors using BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)

    # Sort matches by distance
    matches = sorted(matches, key=lambda x: x.distance)

    # Extract matched keypoints
    points1 = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    points2 = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # Find homography matrix
    homography, _ = cv2.findHomography(points2, points1, cv2.RANSAC, 5.0)

    # Warp align_image to base_image
    height, width = gray_base.shape
    aligned_image = cv2.warpPerspective(gray_align, homography, (width, height))

    return aligned_image

def preprocess_image(image):
    """
    Preprocesses the image to reduce noise and enhance consistency.
    """
    # Apply GaussianBlur to reduce noise
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    # Normalize or equalize histogram to handle lighting differences
    equalized = cv2.equalizeHist(blurred)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    #plt.imshow(thresh, cmap='gray')
    #plt.show()
    return thresh

def detect(image_path,ques_path):
    Final = []
    # Load ticked and text-only images
    ticked_image = cv2.imread(image_path)
    text_only_image = cv2.imread(ques_path)

    # Preprocess the ticked image
    preprocessed_ticked = preprocess_image(cv2.cvtColor(ticked_image, cv2.COLOR_BGR2GRAY))

    # Align text-only image to ticked image
    aligned_text_only = align_images(ticked_image, text_only_image)

    # Preprocess the aligned image (AFTER alignment)
    aligned_text_only_preprocessed = preprocess_image(aligned_text_only)

    # Ensure the aligned image has the same dimensions as the ticked image
    aligned_text_only_preprocessed = cv2.resize(
        aligned_text_only_preprocessed, 
        (preprocessed_ticked.shape[1], preprocessed_ticked.shape[0])
    )

    # Subtract aligned text-only image from the ticked image
    diff_image = cv2.absdiff(preprocessed_ticked, aligned_text_only_preprocessed)

    # Apply a threshold to highlight differences (ticks)
    _, tick_mask = cv2.threshold(diff_image, 30, 255, cv2.THRESH_BINARY)

    # Perform morphological operations to clean up noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned_mask = cv2.morphologyEx(tick_mask, cv2.MORPH_CLOSE, kernel)

    # Detect contours of the tick marks
    contours, _ = cv2.findContours(tick_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    tick = []
    # Draw the detected ticks on the original ticked image
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        aspect_ratio = w / h

            # Extract the bounding box region
        bounding_box = tick_mask[y:y+h, x:x+w]
        non_zero_pixels = cv2.countNonZero(bounding_box)
        pixel_density = non_zero_pixels / (w * h)

        if 10 < area < 500 and 0.5 < aspect_ratio < 1.5 and pixel_density > 0.1:
        #if True:
            tick.append(contour)
            cv2.rectangle(text_only_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #cv2.drawContours(ticked_image, [contour], -1, (0, 255, 0), 2)
    # Display the subtracted image and results
    # cv2.imshow('Subtracted Image', tick_mask)
    # cv2.imshow('Cleaned Subtracted Image', cleaned_mask)


    ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Use English model

    # Perform OCR
    results = ocr.ocr(ques_path, cls=True)

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
    # print(ocr_data)
    for t in tick:
        tx, ty, tw, th = cv2.boundingRect(t)
        mtx = tx+(tw)/2
        mty = ty+(th)/2
        #print(tx, ty)
        index = 0
        for entry in ocr_data:
            x1 = entry['bounding_box'][0][0]
            y1 = entry['bounding_box'][0][1]
            x2 = entry['bounding_box'][2][0]
            y2 = entry['bounding_box'][2][1]
            #cv2.rectangle(text_only_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            if  (x1 < mtx < x2 and y1 < mty < y2) or (x1 < tx < x2 and y1 < ty < y2) or (x1 < tx+tw < x2 and y1 < ty+th < y2):
                # print(tx, ty)
                # print(x1, x2, y1, y2)

                cv2.rectangle(text_only_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                choice  = entry['text'].strip()
                ques = ocr_data[index]["text"][0].strip()
                while not ques.isnumeric():
                    index -= 1
                    ques = ocr_data[index]["text"][0].strip()
                temp= {int(ques):choice}
                Final.append(temp)
            index += 1
    unique_detected = {}
    for item in Final:
        for key, value in item.items():
            if key not in unique_detected:
                unique_detected[key] = value

    Final = [{key: value} for key, value in unique_detected.items()]
    cv2.imshow('Detected Ticks', text_only_image)    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return Final

if __name__ == "__main__":
    Answer_Key = {
        1: "A",
        2: "B",
        3: "C",
        4: "D",
        5: "A",
        6: "B",
        7: "C",
        8: "D",
        9: "A",
        10: "B"
    }
    Detected = detect("assets/ticked.png", "assets/mcq.png")
    print(Detected)
    score = 0
    for i in Detected:
        for key in i:
            if Answer_Key[key].lower() == i[key][0].lower():
                score += 1
                print(key)
    print("Score: ", score)