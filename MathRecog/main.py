import os
import json
import numpy as np
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for faster plotting
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# Paths
INPUT_FOLDER = "mathwriting-2024/train"
OUTPUT_FOLDER = "dataset"
IMAGE_FOLDER = os.path.join(OUTPUT_FOLDER, "images")
LABELS_FILE = os.path.join(OUTPUT_FOLDER, "labels.json")

# Ensure output directories exist
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Define namespace
NAMESPACE = {'inkml': 'http://www.w3.org/2003/InkML'}

def process_inkml_file(inkml_filename):
    """
    Processes a single InkML file:
    - Parses the XML
    - Extracts the normalized label and stroke data
    - Plots the strokes and saves as JPG in IMAGE_FOLDER
    - Returns (jpg_filename, normalized_label) for JSON
    """
    try:
        inkml_path = os.path.join(INPUT_FOLDER, inkml_filename)
        tree = ET.parse(inkml_path)
        root = tree.getroot()

        # Extract normalized label
        normalized_label = None
        for annotation in root.findall('inkml:annotation', NAMESPACE):
            if annotation.attrib.get('type') == "normalizedLabel":
                normalized_label = annotation.text.strip()
                break
        if normalized_label is None:
            # Skip files with no normalized label
            return None

        # Extract strokes from all <trace> elements
        strokes = []
        for trace in root.findall('inkml:trace', NAMESPACE):
            # Split each trace string into points and convert to float (only x, y)
            points = [tuple(map(float, p.split()))[:2] for p in trace.text.strip().split(",")]
            strokes.append(np.array(points))

        # Generate output filenames
        base_filename = os.path.splitext(inkml_filename)[0]
        img_filename = f"{base_filename}.jpg"
        img_path = os.path.join(IMAGE_FOLDER, img_filename)

        # Plot strokes without displaying
        fig, ax = plt.subplots(figsize=(6, 6), dpi=300)
        ax.axis('off')
        for stroke in strokes:
            # Plot each stroke, flipping y-axis for proper orientation
            ax.plot(stroke[:, 0], -stroke[:, 1], 'k', linewidth=2)
        # Draw canvas and save image
        canvas = FigureCanvas(fig)
        canvas.draw()
        fig.savefig(img_path, bbox_inches='tight', pad_inches=0)
        plt.close(fig)  # Free the memory for this figure

        return (img_filename, normalized_label)
    except Exception as e:
        print(f"Error processing {inkml_filename}: {e}")
        return None

def process_all_inkml():
    # Get first 1000 InkML files
    all_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".inkml")]
    inkml_files = all_files[:50000]
    print(f"Found {len(inkml_files)} InkML files (processing first 1000).")

    # Use multiprocessing pool to process files in parallel
    num_workers = min(cpu_count(), len(inkml_files)) -1
    print(f"Using {num_workers} workers for parallel processing.")
    with Pool(num_workers) as pool:
        results = list(tqdm(pool.imap(process_inkml_file, inkml_files), total=len(inkml_files), desc="Processing InkML files"))
    
    # Aggregate valid results (skip None values)
    labels_dict = {img_filename: label for (img_filename, label) in results if img_filename is not None}

    # Save labels to JSON
    with open(LABELS_FILE, 'w', encoding='utf-8') as json_file:
        json.dump(labels_dict, json_file, indent=4)
    
    print(f"Saved {len(labels_dict)} images and labels in '{OUTPUT_FOLDER}/'.")

if __name__ == "__main__":
    process_all_inkml()