import os
import sys
import gc
import torch
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from transformers import AutoProcessor, AutoModelForCausalLM

def preprocess_image(image):
    """Preprocesses a single image to reduce noise and enhance clarity."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # equalized = clahe.apply(gray)

    kernel = np.array([[-1, -1, -1],
                       [-1, 9, -1],
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(gray, -1, kernel)

    rgb = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2RGB)

    return rgb

def ocr_image(image, model, processor, device, torch_dtype):
    """Performs OCR on a single preprocessed image."""
    prompt = "<OCR>"

    with torch.no_grad():
        inputs = processor(text=prompt, images=image, return_tensors="pt").to(device, torch_dtype)
        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=512,
            do_sample=False,
            num_beams=2
        )

        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = processor.post_process_generation(
            generated_text, task="<OCR>", image_size=(image.shape[1], image.shape[0]) 
        )['<OCR>']

    del inputs, generated_ids, generated_text 
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    gc.collect()

    return parsed_answer


def ocr_pdf(pdf_file, model, processor, device, torch_dtype,images=[]):
    """Performs OCR on all pages of a PDF and returns the concatenated text."""
    all_text = ""
    if images == []:
        images = convert_from_path(pdf_file)
    for i, imageOriginal in enumerate(images): 
        print(f"Processing page {i+1}/{len(images)}") 
        image = np.array(imageOriginal) 

        preprocessed_image = preprocess_image(image)

        page_text = ocr_image(preprocessed_image, model, processor, device, torch_dtype)
        all_text += page_text + "\n"  
        del image, preprocessed_image, page_text 
    return all_text


if __name__ == "__main__":
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    print(f"Using {'GPU' if device == 'cuda:0' else 'CPU'}")

    model = AutoModelForCausalLM.from_pretrained(
        "microsoft/Florence-2-large-ft", torch_dtype=torch_dtype, trust_remote_code=True
    ).to(device)
    processor = AutoProcessor.from_pretrained("microsoft/Florence-2-large-ft", trust_remote_code=True)

    try:
        ocr_text = ocr_pdf("sample.pdf", model, processor, device, torch_dtype)
        print(ocr_text) #prints the text
    finally:
        # Cleanup before exit
        del model, processor
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        gc.collect()