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


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()  # Only needed if creating a frozen executable (usually not necessary)

    model = YOLO('yolov8n.pt')  # load a pretrained YOLOv8n model
    #model.to(device) #No need to do this. Model will automatically use GPU if available.

    # Train the model and get training history
    results = model.train(data='data.yaml', epochs=50,workers=0)  # Train for a smaller number of epochs at start to check the code
    print("Training and validation are complete. Check the results.csv file in your results folder. Now exiting");
