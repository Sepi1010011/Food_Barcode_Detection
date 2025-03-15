import os
import cv2
import numpy as np


def preprocess_barcode_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Convert back to BGR for visualization
    preprocessed_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    return preprocessed_image


def run_preprocess(img):

    processed_image = preprocess_barcode_image(img)

    return processed_image
