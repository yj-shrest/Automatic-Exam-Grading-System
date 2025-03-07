import os
import random
import shutil
import matplotlib.pyplot as plt
from ultralytics import YOLO
import torch

if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"Training on GPU: {torch.cuda.get_device_name(0)}")
else:
    device = torch.device("cpu")
    print("Training on CPU (GPU not available)")
# --------------------------------------------------------------------------
# Data Preparation (Split Data into Train and Validation)
# --------------------------------------------------------------------------

def split_data(image_dir, label_dir, train_dir, val_dir, split_ratio=0.8):
    """Splits image and label data into training and validation sets."""

    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    if not os.path.exists(val_dir):
        os.makedirs(val_dir)

    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    random.shuffle(image_files)  # Shuffle to ensure random split

    split_index = int(len(image_files) * split_ratio)
    train_files = image_files[:split_index]
    val_files = image_files[split_index:]

    def move_files(files, source_image_dir, source_label_dir, dest_image_dir, dest_label_dir):
        for file in files:
            image_path = os.path.join(source_image_dir, file)
            label_file = os.path.splitext(file)[0] + '.txt' #Assuming .txt extention
            label_path = os.path.join(source_label_dir, label_file)

            # Move image
            shutil.move(image_path, os.path.join(dest_image_dir, file))

            # Move label
            shutil.move(label_path, os.path.join(dest_label_dir, label_file))

    move_files(train_files, image_dir, label_dir, os.path.join(train_dir,'..','images', 'train'), os.path.join(train_dir,'..', 'labels', 'train')) #os.path.join(train_dir,'images'), os.path.join(train_dir,'labels'))
    move_files(val_files, image_dir, label_dir, os.path.join(val_dir,'..', 'images', 'val'), os.path.join(val_dir, '..', 'labels', 'val')) #os.path.join(val_dir,'images'), os.path.join(val_dir,'labels'))
    print("Data split complete!")


# --------------------------------------------------------------------------
# Configuration (Set Your Paths)
# --------------------------------------------------------------------------

# Set Your Directories. Important : Give Absolute Paths
# image_dir = '/content/images'
# label_dir = '/content/labels'

# base_dir = '/content'   #Your folder

train_dir = 'aegs/Components/Object Detection/images/train'
val_dir = 'aegs/Components/Object Detection/images/val'



# --------------------------------------------------------------------------
# Data Splitting (Uncomment if you need to split the data)
# --------------------------------------------------------------------------
# split_data(image_dir, label_dir, base_dir, base_dir, split_ratio=0.8)
# --------------------------------------------------------------------------
# Training the Model
# --------------------------------------------------------------------------

# Load a model
model = YOLO('yolov8n.pt')  # load a pretrained YOLOv8n model


# Train the model and get training history
history = model.train(data='data.yaml', epochs=5)  # Train for a smaller number of epochs at start to check the code

# --------------------------------------------------------------------------
# Plotting Training Results
# --------------------------------------------------------------------------

# Extract the metrics from the training history
# Check keys in history[0].keys() to know what keys exist and use them below.

train_loss = [x['train/loss'] for x in history]
val_loss = [x['val/loss'] for x in history]
# Extract other metrics as needed. For example to extract precision and recall use.
# precision = [x['metrics/precision'] for x in history]

# Plot training and validation loss
plt.figure(figsize=(10, 5))
plt.plot(train_loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.legend()
plt.grid(True)
plt.show()


# Optionally, evaluate the model on the validation set (after training is complete)
metrics = model.val()  # evaluate model performance on the validation set
print(metrics)  # Print validation metrics after training. This will print the validation result (map, precision recall etc.)