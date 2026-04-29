import cv2
import numpy as np
import matplotlib.pyplot as plt
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
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
    aligned_image = cv2.warpPerspective(gray_align, homography, (width, height),borderValue=255)

    return aligned_image

def draw_contour_boxes(source_img, target_img):
    """
    Finds contours in `source_img` and draws their bounding boxes on `target_img`.
    """
    # Ensure source is grayscale/binary for contour detection
    if len(source_img.shape) == 3:
        gray = cv2.cvtColor(source_img, cv2.COLOR_BGR2GRAY)
    else:
        gray = source_img

    # Threshold if not already binary
    # _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # Find contours in the binary image
    contours, _ = cv2.findContours(source_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    # print("Contours found:", contours)
    # Draw bounding boxes around contours on a copy of the target image
    result = target_img.copy()
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # print("Bounding box:", x, y, w, h)
        # cv2.rectangle(result, (x, y), (x + w, y + h), (255, 255, 255),-1)
        cv2.drawContours(result, [cnt], -1, (255, 255, 255), 4)    
    return result


def preprocess_image(image,n=0):
    """
    Preprocesses the image to reduce noise and enhance consistency.
    """
    # Apply GaussianBlur to reduce noise

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    blurred = cv2.GaussianBlur(image, (3,3), 0)

    # Step 2: Adaptive threshold
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # Step 3: Dilation to expand white contours
    # kernel = np.ones((5, 5), np.uint8)  # You can try (5,5) for thicker expansion
    # dilated = cv2.dilate(thresh, kernel, iterations=2)  
    #plt.imshow(thresh, cmap='gray')
    #plt.show()
    if(n==1):
        return image
    else:
        return thresh 


def detect_multiple(ques_path,image_path,Answer_Key): 
    images = convert_from_path(image_path)
    Final = {}
    for i, image in enumerate(images):
        image.save('temp.png', 'JPEG')
        result = detect('temp.png',ques_path)
        print(result)
        score = 0
        for j in result:
            for key in j:
                if Answer_Key[key].lower() == j[key][0].lower():
                    score += 1
        Final[i+1] = score
    return Final
def detect(image_path,ques_path):
    Final = []
    # Load ticked and text-only images
    ticked_image = cv2.imread(image_path)
    text_only_image = cv2.imread(ques_path)

    # Preprocess the ticked image
    preprocessed_ticked = preprocess_image(cv2.cvtColor(ticked_image, cv2.COLOR_BGR2GRAY),1)
    # Align text-only image to ticked image
    # cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("Image", 600, 900)
    # cv2.imshow('Image', preprocessed_ticked) 
    # cv2.waitKey(0)
    aligned_text_only = align_images(ticked_image, text_only_image) 
    

    # Preprocess the aligned image (AFTER alignment)
    aligned_text_only_preprocessed = preprocess_image(aligned_text_only)

    # Ensure the aligned image has the same dimensions as the ticked image
    aligned_text_only_preprocessed = cv2.resize(
        aligned_text_only_preprocessed, 
        (preprocessed_ticked.shape[1], preprocessed_ticked.shape[0])
    )

    # Subtract aligned text-only image from the ticked image
    # diff_image = cv2.absdiff(preprocessed_ticked, aligned_text_only_preprocessed)
    diff_image = draw_contour_boxes(aligned_text_only_preprocessed, preprocessed_ticked) 
    # cv2.imshow('Image', ticked_image)  
    # cv2.waitKey(0) 
    # cv2.imshow('Image', aligned_text_only_preprocessed)  
    # cv2.waitKey(0) 
    # cv2.imshow('Image', diff_image)  
    # cv2.waitKey(0) 
    # Apply a threshold to highlight differences (ticks)
    _, tick_mask = cv2.threshold(diff_image, 40, 255, cv2.THRESH_BINARY)

    # Perform morphological operations to clean up noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    cleaned_mask = cv2.morphologyEx(tick_mask, cv2.MORPH_CLOSE, kernel)
    # cv2.imshow('Image', tick_mask)  
    # cv2.waitKey(0) 
    # Detect contours of the tick marks
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))  # Adjust size
    dilated = cv2.dilate(tick_mask, kernel, iterations=2) 
    # cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("Image", 700, 1000)
    # cv2.imshow('Image', dilated)
    # cv2.waitKey(0)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(c) for c in contours]

# Merge nearby boxes (example threshold = 20 pixels)
    merged = []
    used = [False] * len(boxes)

    for i, (x1, y1, w1, h1) in enumerate(boxes): 
        if used[i]:
            continue
        x2, y2 = x1 + w1, y1 + h1
        for j in range(i + 1, len(boxes)):
            if used[j]:
                continue
            x3, y3, w3, h3 = boxes[j]
            x4, y4 = x3 + w3, y3 + h3

            # Check if boxes are near each other
            if abs(x1 - x3) < 70 and abs(y1 - y3) < 20:
                x1, y1 = min(x1, x3), min(y1, y3)
                x2, y2 = max(x2, x4), max(y2, y4)
                used[j] = True
        used[i] = True
        merged.append((x1, y1, x2 - x1, y2 - y1))
        # cv2.rectangle(ticked_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
    tick = []
    # cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("Image", 700, 1000)
    # cv2.imshow('Image', ticked_image)
    # cv2.waitKey(0)
    # Draw the detected ticks on the original ticked image
    for box in merged:
        x, y, w, h = box
        area = w * h
        
        aspect_ratio = w / h

            # Extract the bounding box region
        bounding_box = tick_mask[y:y+h, x:x+w]
        non_zero_pixels = cv2.countNonZero(bounding_box) 
        pixel_density = non_zero_pixels / (w * h)

        # cv2.drawContours(ticked_image, [contour], -1, (0, 255, 255), 2)
        #cv2.rectangle(ticked_image, (x, y), (x + w, y + h), (0, 255, 0), 1) 
        # if 100 < area and area < 1000 and 0.5 < aspect_ratio and aspect_ratio < 1.5 and pixel_density > 0.1:
        if area<20000 and area>100 and pixel_density>0.1:
        # if area>150 and aspect_ratio>0.5 and aspect_ratio<2 and pixel_density>0.1:
            cv2.rectangle(ticked_image, (x, y), (x + w, y + h), (0, 0, 255), 2)  
            # print("Bounding box:", x, y, w, h,area)
            tick.append(box) 
    # cv2.imshow('Image', ticked_image)
    # cv2.waitKey(0)


    ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Use English model
  
    # Perform OCR
    results = ocr.ocr(aligned_text_only, cls=True)
 
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
        tx1, ty1, tw, th = t
        tx2 = tx1 + tw
        ty2 = ty1 + th
        mtx = tx1+(tw)/2
        mty = ty1+(th)/2
        #print(tx, ty)
        index = 0
        for entry in ocr_data:
            temp_index = index
            x1 = entry['bounding_box'][0][0]
            y1 = entry['bounding_box'][0][1]
            x2 = entry['bounding_box'][2][0]
            y2 = entry['bounding_box'][2][1]
            ix1 = max(x1, tx1)
            iy1 = max(y1, ty1)
            ix2 = min(x2, tx2)
            iy2 = min(y2, ty2)
            intersection_width = max(0, ix2 - ix1)
            intersection_height = max(0, iy2 - iy1)
            area_of_intersection = intersection_width * intersection_height
            #cv2.rectangle(text_only_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            # middle of tick must lie within 10 percentage of the bounding box
            if  area_of_intersection>1:
                area = tw * th
                cv2.rectangle(ticked_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.rectangle(ticked_image, (tx1, ty1), (tx1 + tw, ty1 + th), (0, 0, 255), 2)
                choice  = entry['text'].strip()
                ques = ocr_data[temp_index]["text"][0].strip()
                second_digit = ocr_data[temp_index]["text"][1].strip() 
                if second_digit.isnumeric():
                    ques = second_digit + ques
                while not ques.isnumeric():
                    temp_index -= 1
                    ques = ocr_data[temp_index]["text"][0].strip()
            
                second_digit = ocr_data[temp_index]["text"][1].strip() 
                # print(ques,second_digit)
                if second_digit.isnumeric():
                    ques = ques + second_digit 
                temp = {int(ques): [choice, area_of_intersection]}
                Final.append(temp)
            index += 1
    unique_detected = {}
    print("Final: ",Final)
    for item in Final:
        for key, value in item.items():
            if key not in unique_detected:
                unique_detected[key] = value
            else:
                if value[1] > unique_detected[key][1] and value[0][0] in ['a', 'b', 'c', 'd']:
                    unique_detected[key] = value

    Final = [{key: value[0]} for key, value in unique_detected.items()]
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Image", 700, 1000)
    cv2.imshow('Image', ticked_image)    
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