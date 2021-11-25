"""
Functions for the chromakey operations
"""
import cv2
import numpy as np
import os
from PIL import Image
import folder_check as fldr_chk
#%%
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


def get_fg(img_path : str,
            mask_path : str, 
            extracted_fg_folder: str):
    """
    Extracts the foreground when paths to the image and
    the mask are passed. Additional inputs are the folder
    where the extracted foreground is to be saved. And the
    image number to use as filename.
    Inputs: img_path = string of path to image
            mask_path = string of path to mask
            extracted_fg_folder = string of path to
                                location for saving
                                extracted foreground
    """
    image = Image.open(img_path).convert('RGBA')
    mask = Image.open(mask_path).convert('L')
    image.putalpha(mask)
    # Creating the filename
    base_name = os.path.basename(mask_path)
    save_path = os.path.join(extracted_fg_folder, base_name)
    image.save(save_path)
    # return image


def get_mask(img_path : str,
            mask_folder: str):
    """
    Generates the binary mask for the image path
    Input: img_path = string for path to image
            mask_folder = string for path to where mask
                        will be saved
    Output: Saves the generated mask to the mask_folder
            and returns string for path to mask
    """
    image = cv2.imread(img_path)
    img_mask = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower, upper = auto_chroma(img_path)
    # Generating the mask
    mask = cv2.inRange(img_mask, lower, upper)
    mask = cv2.bitwise_not(mask)

    number = str(fldr_chk.get_num(target_folder=mask_folder,
                                extension='png'))
    mask_path = os.path.join(mask_folder, number)
    mask_path = f'{mask_path}.png'
    cv2.imwrite(mask_path, mask)
    return mask_path


def extract_with_chromakey(img_path : str,
            mask_folder : str, 
            extracted_fg_folder: str):
    """
    Function which calls the get_mask and get_fg
    Inputs: img_path = string for path to image
    """
    mask_path = get_mask(img_path, mask_folder)
    get_fg(img_path, mask_path, extracted_fg_folder)