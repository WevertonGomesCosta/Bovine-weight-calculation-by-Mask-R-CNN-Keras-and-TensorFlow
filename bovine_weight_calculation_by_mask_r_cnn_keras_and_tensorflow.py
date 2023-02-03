# -*- coding: utf-8 -*-
"""Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DbvpKE0IzBAYDpLz1VQV83ep5ZzHXu_J

## **1. Installation**

Git clone repositorie and install libraries
"""

# Commented out IPython magic to ensure Python compatibility.
!git clone https://github.com/WevertonGomesCosta/Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow.git
# %matplotlib inline
import warnings
warnings.filterwarnings('ignore')

# Update CUDA for TF 2.5
!wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/libcudnn8_8.1.0.77-1+cuda11.2_amd64.deb
!dpkg -i libcudnn8_8.1.0.77-1+cuda11.2_amd64.deb
# Check if package has been installed
!ls -l /usr/lib/x86_64-linux-gnu/libcudnn.so.*
# Upgrade Tensorflow
!pip install --upgrade tensorflow==2.5.0

"""## **2. Root path and functions**
Declare root path and import functions on m_rcnn
"""

import sys
sys.path.append("C:/Users/USUARIO/Documents/GitHub/Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow/mrcnn")
from m_rcnn import *

"""## **3. Image Dataset**

Load your images and annotated dataset

"""

images_path = 'C:/Users/USUARIO/Documents/GitHub/Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow/images1'
annotations_path = "C:/Users/USUARIO/Documents/GitHub/Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow/Seg_imagens_coletas/labels_annotations_coleta1_2023-02-02-04-47-22.json"
dataset_train = load_image_dataset(os.path.join(annotations_path), images_path, "train")
dataset_val = load_image_dataset(os.path.join(annotations_path), images_path, "val")
class_number = dataset_train.count_classes()
print('Train: %d' % len(dataset_train.image_ids))
print('Validation: %d' % len(dataset_val.image_ids))
print("Classes: {}".format(class_number))

"""Load image samples"""

display_image_samples(dataset_train)

"""## **4. Training**

Train Mask RCNN on your custom Dataset.
"""

# Load Configuration
config = CustomConfig(class_number)
#config.display()
model = load_training_model(config)
config.display()
# Start Training
# This operation might take a long time.
train_head(model, dataset_train, dataset_train, config)

"""## **5. Save your model**

Save your model training in "mask_rcnn_shapes.h5"
"""

model_path = os.path.join(ROOT_DIR, "mask_rcnn_shapes_bovine.h5")
model.keras_model.save_weights(model_path)
#Export results
from google.colab import files
files.download("/content/Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow/mask_rcnn_shapes_bovine.h5")

"""## **6. Detection (test your model on a random image)**"""

# Load Test Model
# The latest trained model will be loaded
test_model, inference_config = load_test_model(class_number)

# Test on a random image
test_random_image(test_model, dataset_val, inference_config)

"""## **7. Run Mask-RCNN on Images**

You can load here the image and extract the mask using Mask-RCNN

"""

import os
import glob
import pandas as pd
import cv2
from google.colab.patches import cv2_imshow
from visualize import *

files_images=[]
path_images = '/content/Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow/images1'
images = pd.DataFrame([f for f in glob.glob(path_images + "**/*.jpg", recursive=True)], columns = ['Name'])
n_rows = images.shape[0]

"""Here, you can calculate the area. Only assign a value if you know the actual size of objects."""

RATIO_PIXEL_TO_CM_h = 2.15 # 2.15 pixels are 1cm
RATIO_PIXEL_TO_CM_w = 1.92
RATIO_PIXEL_TO_SQUARE_CM = RATIO_PIXEL_TO_CM_h * RATIO_PIXEL_TO_CM_w
results = {}

def detect_contours_maskrcnn(model, img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = model.detect([img_rgb])
    r = results[0]
    object_count = len(r["class_ids"])
    
    objects_ids = []
    objects_contours = []
    bboxes = []
    for i in range(object_count):
        # 1. Class ID
        class_id = r["class_ids"][i]
        # 2. Boxes
        box = r["rois"][i]
        
        # 3. Mask
        mask = r["masks"][:, :, i]
        contours = get_mask_contours(mask)
        bboxes.append(box)
        objects_contours.append(contours[0])
        objects_ids.append(class_id)
    return objects_ids, bboxes, objects_contours

"""Now, let's create a loop for each image and calculate the size of the pigs."""

for i in range(n_rows):
  # Save image in img
  img = cv2.imread(images.loc[i, "Name"])
  #cv2_imshow(img)
  # Created box
  img_box = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  #Colors to class
  class_names = ["BG", "green", "blue", "light blue", "pink"]
  colors = random_colors(len(class_names))

  # Get objects mask
  class_ids, boxes, masks = detect_contours_maskrcnn(test_model, img)

  for class_id, box, object_contours in zip(class_ids, boxes, masks):
      # 1. Creted polylines Box to calculate size of the pigs
      y1, x1, y2, x2 = box
      #cv2.rectangle(img, (x1, y1), (x2, y2), colors[class_id], 15)
      cv2.polylines(img, [object_contours], True, colors[class_id], 2)
      img = draw_mask(img, [object_contours], colors[class_id])

      # 2. Calculate area
      area_px = cv2.contourArea(object_contours)
      area_cm = round(area_px / RATIO_PIXEL_TO_SQUARE_CM, 2)

      # 3. Calculate perimeter
      perimeter_px = cv2.arcLength(object_contours, True)
      perimeter_cm = round((perimeter_px *  600)/1640,2)

      # 4. Calculate length
      rect = cv2.minAreaRect(object_contours)
      box = cv2.boxPoints(rect)
      box = np.int0(box)
      cv2.drawContours(img, [box], 0, (0,255,0), 2) # this was mostly for debugging you may omit
      (x, y), (w, h), angle = rect
      
      # 5. Get Width and Height of the Objects by applying the Ratio pixel to cm

      object_width = round(w* 600/ 1640,2)
      object_height = round(h *600/ 1640 ,2)

      # 6. Add informations in the images
      cv2.putText(img, "Nome: {}".format(images.loc[i, "Name"][74:-4]), (0, 300), cv2.FONT_HERSHEY_PLAIN, 2, colors[class_id], 2)
      cv2.putText(img, "A: {}px".format(round(area_px,2)), (0, 250), cv2.FONT_HERSHEY_PLAIN, 2, colors[class_id], 2)
      cv2.putText(img, "P: {}px".format(round(perimeter_px,2)), (0, 200), cv2.FONT_HERSHEY_PLAIN,2, colors[class_id], 2)
      cv2.putText(img, "C: {}px".format(round(h,2)), (0, 150), cv2.FONT_HERSHEY_PLAIN, 2, colors[class_id], 2)
      cv2.putText(img, "L: {}px".format(round(w,2)), (0, 100), cv2.FONT_HERSHEY_PLAIN, 2, colors[class_id], 2)
      
      # 7. Save informations in the results
      Nome = images.loc[i, "Name"][78:-4]
      results[i] = {"Nome": Nome,
                    "Area_cm": area_cm,
                    "Perimetro_cm":perimeter_cm,
                    "Largura_cm": object_height,
                    "Comprimento_cm":object_width,
                    "Area_px": area_px,
                    "Perimetro_px":perimeter_px,
                    "Largura_px": w,
                    "Comprimento_px":h}
  # Plot image
  cv2_imshow(img)

"""Save results """

results =  pd.DataFrame(data=results)
results
writer = pd.ExcelWriter('results.xlsx')
results.to_excel(writer,'Sheet1')
writer.save()

#Export results
from google.colab import files
files.download("/content/results.xlsx")

"""### **8. Inference Mask-RCNN on Images**

You can load here the image and extract the mask using Mask-RCNN
"""

import os
import pandas as pd
resultsfiles_images=[]
path_images = '/content/Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow/images1'
images = pd.DataFrame(os.listdir(path_images), columns = ['Name'])
n_rows = images.shape[0]

import cv2
from google.colab.patches import cv2_imshow

RATIO_PIXEL_TO_CM_h = 2.15 # 2.15 pixels are 1cm
RATIO_PIXEL_TO_CM_w = 1.92
RATIO_PIXEL_TO_SQUARE_CM = RATIO_PIXEL_TO_CM_h * RATIO_PIXEL_TO_CM_w
results = {}

"""We can load the calculated weights and now if we have more images we can insert them into the inference model to get their measurements."""

# Model inference
test_model, inference_config = load_inference_model(1, "/content/Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow/mask_rcnn_shapes_bovine.h5")

for i in range(n_rows):

  img = cv2.imread(os.path.join(path_images, images.loc[i, "Name"]))

  img_box = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  class_names = ["BG", "green", "blue", "light blue", "pink"]
  colors = random_colors(len(class_names))

  image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

  # Detect results
  r = test_model.detect([image])[0]
  colors = random_colors(80)

  # Get Coordinates and show it on the image
  object_count = len(r["class_ids"])
  for j in range(object_count):
      # 1. Mask
      mask = r["masks"][:, :, j]
      contours = get_mask_contours(mask)
      for cnt in contours:
          cv2.polylines(img, [cnt], True, colors[j], 2)
          img = draw_mask(img, [cnt], colors[j])
          # 2. Calculate area
          area_px = cv2.contourArea(cnt)
          area_cm = round(area_px / RATIO_PIXEL_TO_SQUARE_CM, 2)

          # 3. Calculate perimeter
          perimeter_px = cv2.arcLength(cnt, True)
          perimeter_cm = round((perimeter_px *  600)/1640,2)

          # 4. Calculate length
          rect = cv2.minAreaRect(cnt)
          box = cv2.boxPoints(rect)
          box = np.int0(box)
          cv2.drawContours(img, [box], 0, colors[j], 2) # this was mostly for debugging you may omit
          (x, y), (w, h), angle = rect
          if (w > h):
              C_px = object_width
              L_px = object_height
          if (h > w):
              L_px = object_width
              C_px = object_height
          
          object_width = round(w* 600/ 1640,2)
          object_height = round(h *600/ 1640 ,2)

          if (object_width > object_height):
              C_cm = object_width
              L_cm = object_height
          if (object_height > object_width):
              L_cm = object_width
              C_cm = object_height
          
          # 5. write in image
          peso = -1.49560824863731 + 0.00284305110419364*area_px
          cv2.putText(img, "Nome: {}".format(images.loc[i, "Name"]), (0, 350), cv2.FONT_HERSHEY_PLAIN, 2, colors[j], 2)
          cv2.putText(img, "Peso predito: {}".format(round(peso,2)), (0, 300), cv2.FONT_HERSHEY_PLAIN, 2, colors[j], 2)
          cv2.putText(img, "A: {}cm^2".format(round(area_cm,2)), (0, 250), cv2.FONT_HERSHEY_PLAIN, 2, colors[j], 2)
          cv2.putText(img, "P: {}cm".format(round(perimeter_cm,2)), (0, 200), cv2.FONT_HERSHEY_PLAIN,2, colors[j], 2)
          cv2.putText(img, "C: {}cm".format(round(C_cm,2)), (0, 150), cv2.FONT_HERSHEY_PLAIN, 2, colors[j], 2)
          cv2.putText(img, "L: {}cm".format(round(L_cm,2)), (0, 100), cv2.FONT_HERSHEY_PLAIN, 2, colors[j], 2)

          results[i] = {"Nome": images.loc[i, "Name"],
                        "Area_cm": area_cm,
                        "Perimetro_cm":perimeter_cm,
                        "Largura_cm": L_cm,
                        "Comprimento_cm":C_cm,
                        "Area_px": area_px,
                        "Perimetro_px":perimeter_px,
                        "Largura_px": L_px,
                        "Comprimento_px":C_px,
                        "Peso": peso}

          cv2_imshow(img)

results =  pd.DataFrame(data=results)
results
writer = pd.ExcelWriter('results_inference_bovine.xlsx')
results.to_excel(writer,'Sheet1')
writer.save()

#Export results
from google.colab import files
files.download("/content/results_inference_bovine.xlsx")

"""### **9. Inference Mask-RCNN on Images 2**

You can load here the image and extract the mask using Mask-RCNN
"""

import os
import pandas as pd
resultsfiles_images=[]
path_images = '/content/Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow/images2'
images = pd.DataFrame(os.listdir(path_images), columns = ['Name'])
n_rows = images.shape[0]

import cv2
from google.colab.patches import cv2_imshow

RATIO_PIXEL_TO_CM_h = 2.15 # 2.15 pixels are 1cm
RATIO_PIXEL_TO_CM_w = 1.92
RATIO_PIXEL_TO_SQUARE_CM = RATIO_PIXEL_TO_CM_h * RATIO_PIXEL_TO_CM_w
results = {}

"""We can load the calculated weights and now if we have more images we can insert them into the inference model to get their measurements."""

# Model inference
test_model, inference_config = load_inference_model(1, "/content/Bovine-weight-calculation-by-Mask-R-CNN-Keras-and-TensorFlow/mask_rcnn_shapes_bovine.h5")

for i in range(n_rows):

  img = cv2.imread(os.path.join(path_images, images.loc[i, "Name"]))

  img_box = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  class_names = ["BG", "green", "blue", "light blue", "pink"]
  colors = random_colors(len(class_names))

  image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

  # Detect results
  r = test_model.detect([image])[0]
  colors = random_colors(80)

  # Get Coordinates and show it on the image
  object_count = len(r["class_ids"])
  for j in range(object_count):
      # 1. Mask
      mask = r["masks"][:, :, j]
      contours = get_mask_contours(mask)
      for cnt in contours:
          cv2.polylines(img, [cnt], True, colors[j], 2)
          img = draw_mask(img, [cnt], colors[j])
          # 2. Calculate area
          area_px = cv2.contourArea(cnt)
          area_cm = round(area_px / RATIO_PIXEL_TO_SQUARE_CM, 2)

          # 3. Calculate perimeter
          perimeter_px = cv2.arcLength(cnt, True)
          perimeter_cm = round((perimeter_px *  600)/1640,2)

          # 4. Calculate length
          rect = cv2.minAreaRect(cnt)
          box = cv2.boxPoints(rect)
          box = np.int0(box)
          cv2.drawContours(img, [box], 0, colors[j], 2) # this was mostly for debugging you may omit
          (x, y), (w, h), angle = rect
          if (w > h):
              C_px = object_width
              L_px = object_height
          if (h > w):
              L_px = object_width
              C_px = object_height
          
          object_width = round(w* 600/ 1640,2)
          object_height = round(h *600/ 1640 ,2)

          if (object_width > object_height):
              C_cm = object_width
              L_cm = object_height
          if (object_height > object_width):
              L_cm = object_width
              C_cm = object_height
          
          # 5. write in image
          peso = -1.49560824863731 + 0.00284305110419364*area_px
          cv2.putText(img, "Nome: {}".format(images.loc[i, "Name"]), (0, 350), cv2.FONT_HERSHEY_PLAIN, 2, colors[j], 2)
          cv2.putText(img, "Peso predito: {}".format(round(peso,2)), (0, 300), cv2.FONT_HERSHEY_PLAIN, 2, colors[j], 2)
          cv2.putText(img, "A: {}cm^2".format(round(area_cm,2)), (0, 250), cv2.FONT_HERSHEY_PLAIN, 2, colors[j], 2)
          cv2.putText(img, "P: {}cm".format(round(perimeter_cm,2)), (0, 200), cv2.FONT_HERSHEY_PLAIN,2, colors[j], 2)
          cv2.putText(img, "C: {}cm".format(round(C_cm,2)), (0, 150), cv2.FONT_HERSHEY_PLAIN, 2, colors[j], 2)
          cv2.putText(img, "L: {}cm".format(round(L_cm,2)), (0, 100), cv2.FONT_HERSHEY_PLAIN, 2, colors[j], 2)

          results[i] = {"Nome": images.loc[i, "Name"],
                        "Area_cm": area_cm,
                        "Perimetro_cm":perimeter_cm,
                        "Largura_cm": L_cm,
                        "Comprimento_cm":C_cm,
                        "Area_px": area_px,
                        "Perimetro_px":perimeter_px,
                        "Largura_px": L_px,
                        "Comprimento_px":C_px,
                        "Peso": peso}

          cv2_imshow(img)

results =  pd.DataFrame(data=results)
results
writer = pd.ExcelWriter('results_inference_bovine2.xlsx')
results.to_excel(writer,'Sheet1')
writer.save()

#Export results
from google.colab import files
files.download("/content/results_inference_bovine2.xlsx")
