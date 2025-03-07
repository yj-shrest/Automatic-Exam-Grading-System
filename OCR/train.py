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

# --------------------------------------------------------------------------
# Data Splitting (Uncomment if you need to split the data)
# --------------------------------------------------------------------------
# split_data(image_dir, label_dir, base_dir, base_dir, split_ratio=0.8)
# --------------------------------------------------------------------------
# Training the Model
# ------------------------------------------------------
if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()  # Only needed if creating a frozen executable (usually not necessary)

    # Data Splitting (Uncomment if you need to split the data)
    #split_data(image_dir, label_dir, base_dir, base_dir, split_ratio=0.8)
    # --------------------------------------------------------------------------
    # Training the Model
    # --------------------------------------------------------------------------

    # Load a model
    model = YOLO('yolov8n.pt')  # load a pretrained YOLOv8n model
    #model.to(device) #No need to do this. Model will automatically use GPU if available.

    # Train the model and get training history
    results = model.train(data='data.yaml', epochs=50,workers=0)  # Train for a smaller number of epochs at start to check the code

    #Access the model's training history
    #metrics = results.metrics  #This is only for the final result now, not history

    # --------------------------------------------------------------------------
    # Plotting Training Results
    # --------------------------------------------------------------------------

    #The way to retrieve the losses is changed. Now the `results` is what is returned.
    # The loss is stored inside with key 'loss' or 'val_loss'.
    # For a given results.csv file, you can find a loss column

    #In newer versions the results of the training and validation loss are stored directly in a "results.csv" file, so there's no easy access through history object as before

    #Thus in newer versions, the easiest approach for getting loss for plotting is to use the "results.csv" file after training the model
    #Another solution is by accessing the engine and its training/validation loaders and iteratiting through them to get the results

    # Plot training and validation loss
    #In simpler terms, the most direct and reliable way to get the training loss in newer version of YOLOv8 is to load and read the "results.csv" file after training

    print("Training and validation are complete. Check the results.csv file in your results folder. Now exiting");
