"""
Functions for the chromakey operations
"""
import cv2
import numpy as np
import os

def auto_chroma(image_path):
    """
    This function gets the image with single coloured 
    background, it gives the range for thresholding to 
    extract the foreground object.

    Input: path to image file
    Output: Upper and lower limits of the HSV values of the
    image background.
    """
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    _, c4, _ = image.shape
    c1 = 0
    c2 = int(0.05 * c4)
    c3 = int(c4-c2)
    # This makes two rectangles on the sides of the image 
    # to extract the range of the background HSV values
    roi_1 = image[:, c1:c2]
    roi_2 = image[:, c3:c4]
    # Get the range of hue values from roi_1 & roi_2
    h1, _, _ = roi_1[:, :, 0], roi_1[:, :, 1], roi_1[:, :, 2]
    h2, _, _ = roi_2[:, :, 0], roi_2[:, :, 1], roi_2[:, :, 2]
    MedianH = np.median(np.vstack((h1, h2)))
    #MedianS = np.median(np.vstack((s1,s2)))
    #MedianV = np.median(np.vstack((v1,v2)))
    lower = np.array([(MedianH - 15), 80, 80])
    upper = np.array([(MedianH + 15), 255, 255])
    return lower, upper