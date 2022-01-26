import cv2
from PIL import Image, ImageOps
from tqdm import tqdm
from functions.folder_check import FOLDER_LIST, OUTPUT_FOLDERS
import os
from functions import folder_check as fldr_chk
import random
import math
import numpy as np

OUTPUT_EXTENSION = '.jpg'
RED = 128
BLUE = 200


class ImgComposer:
    def __init__(self,
                resolution: tuple,
                classes_to_include: list,
                num_of_images:int,
                max_objects_in_image:int,
                output_directory:str,
                efo_directory:str,
                include_negative_examples=[],
                datafolder = './Data'):
        self.classes_to_include = classes_to_include
        self.include_negative_examples = include_negative_examples
        self.num_of_images = num_of_images
        self.max_objects_in_images = max_objects_in_image
        self.output_directory = output_directory
        self.efo_directory = efo_directory
        self.resolution = resolution # (width, height)
        self.datafolder = datafolder
    
    def compose(self):
        for imgno in tqdm(range(self.num_of_images)):
            
            img_number = str(fldr_chk.get_num(self.output_directory,
                                        OUTPUT_EXTENSION))
            final_path = os.path.join(self.output_directory,
                                img_number)
            img_name = f"{final_path}.jpg"
            
            # Coloured annotation mask
            output_dir = os.path.dirname(self.output_directory)
            cm_path = os.path.join(output_dir,
                                    OUTPUT_FOLDERS[2],
                                    img_number)
            cm_name = f"{cm_path}.png"

            # Number of objects to add in the image
            NumObjects = random.randrange(1, 
                        self.max_objects_in_images+1)

            # list of integer values for green
            # for objects in the range of 
            # 0 to 255
            greenlist = list(range(1, 255,
                        int(255/NumObjects)))
            
            Num = 0
            greenval_and_obj = {}

            while Num != NumObjects:
                classinstance = random.choice(self.classes_to_include)
                greenval_and_obj[greenlist[Num]] = classinstance
                Num += 1
            
            # Background image
            bg_folder = os.path.join(self.datafolder,(FOLDER_LIST[0]))
            random_bg = random.choice(os.listdir(bg_folder))
            bg_path = os.path.join(bg_folder, random_bg)
            background = Image.open(bg_path)
            background = background.resize(self.resolution,
                            Image.ANTIALIAS)
            
            # Black image for binary mask
            bin_mask = Image.new('RGBA',
                        background.size,
                        color='black')
            
            # TODO: Adding negative examples

            for green, obj in greenval_and_obj.items():
                fg_point = os.path.join(self.efo_directory, obj)
                if len(os.listdir(fg_point)) != 0:
                    fg = random.choice(os.listdir(fg_point))
                    fg_path = os.path.join(fg_point, fg)
                    msk_fldr = os.path.join(os.path.dirname(self.efo_directory),
                            OUTPUT_FOLDERS[4])
                    msk_path = os.path.join(msk_fldr, obj, fg)
                    mask = Image.open(msk_path).convert('L')
                    foreground = Image.open(fg_path)
                    ColourRGB = (RED, green, BLUE)

                    foreground, mask = scaled(foreground,
                                            background, mask)
                    foreground, mask = rotated(foreground, mask)
                    foreground, mask = flipped(foreground, mask)
                    background, bin_mask = placed(foreground,
                                                background,
                                                mask,
                                                bin_mask,
                                                ColourRGB)
            background.save(img_name)
            bin_mask.save(cm_name)

            # Saving the annotation masks
            save_annotation_masks(bin_mask,
                                img_number,
                                greenval_and_obj,
                                output_dir)

def scaled(foreground, background, mask,
            scaled_to=None):
    """
    Function for scaling the foreground object
    with respect to the background
    Inputs:
    foreground = PIL Image of the foreground
    background = PIL Image of the background
    mask = PIL Image of foreground mask
    scaled_to = float; scaling factor of foreground,
            if None then uses random values
            with respect to the background
    """
    if scaled_to is None:
        bg_width, _ = background.size
        fg_width, fg_height = foreground.size
        new_width = random.randrange((math.floor(0.005*bg_width)),
                        math.ceil(0.6*bg_width))
        new_height = int(fg_height * (new_width/fg_width))
        new_size = (new_width, new_height)
        resized_fg = foreground.resize(new_size,
                        Image.BICUBIC)
        resized_mask = mask.resize(new_size,
                        Image.BICUBIC)
    return resized_fg, resized_mask

def rotated(foreground, mask,
            angle=random.randrange(0,359)):
    """
    Function for rotating the foreground object
    Also performs the same operation for the mask
    Inputs:
    foreground = PIL Image of foreground
    mask = PIL Image of mask
    angle = angle in degrees to rotate the foreground
    Outputs:
    foreground and mask with rotation performed
    """
    foreground = foreground.rotate(angle,
                    resample=Image.BICUBIC)
    mask = mask.rotate(angle,
            resample=Image.BICUBIC)
    return foreground, mask

def flipped(foreground, mask,
            flip_foreground=random.choice((True, False))):
    """
    Performs Mirror operation on the foreground
    object and the mask of the foreground
    Inputs:
    foreground = PIL Image of foreground
    mask = PIL Image of mask
    flip_foreground = Bool to decide whether
    or not to mirror the foreground object
    Outputs:
    foreground and mask with the operation
    performed
    """
    if flip_foreground:
        foreground = ImageOps.mirror(foreground)
        mask = ImageOps.mirror(mask)
    
    return foreground, mask

def placed(foreground, background, mask,
            bin_mask=None,
            mask_colour=None,
            placed_at=None):
    """
    Function for placing the foreground object
    on the background.
    Inputs:
    foreground = PIL Image of the foreground
    background = PIL Image of the background
    mask = PIL Image of the background
    placed_at = Tuple containing x and 
                y co-ordinates
    bin_mask = PIL Image of the final 
                annotation mask
    mask_colour = Tuple of RGB values for mask

    Outputs:
    returns composed image and the final
    coloured annotation mask
    """
    if placed_at == None:
        bg_wide, bg_high = background.size
        # Location on X axis
        x_low_limit = -0.1*bg_wide
        x_up_limit = 0.8*bg_wide
        x = random.randrange(x_low_limit,
                            x_up_limit)
        # Location on Y axis
        y_low_limit = -0.1*bg_high
        y_up_limit = 0.8*bg_high
        y = random.randrange(y_low_limit,
                            y_up_limit)
        placed_at = (x,y)
    
    # Compositing the foreground on the background
    background.paste(foreground,
                    placed_at,
                    mask)

    if bin_mask != None:
        mask_coloured = mask_maker(mask,
                            mask_colour)
        bin_mask.paste(mask_coloured, placed_at,
                        mask)
    return background, bin_mask

def mask_maker(mask, mask_colour):
    """
    Function to create the coloured mask for
    compositing on the annotation mask
    Inputs:
    mask = PIL Image of the foreground mask
    mask_coloured = Tuple of RGB values for mask
    """
    w, h = mask.size
    mask_coloured = Image.new("RGB", (w,h),
                            mask_colour)
    mask_coloured.putalpha(mask)
    return mask_coloured

def save_annotation_masks(bin_mask,
                        img_number:str,
                        dict_color_object:dict,
                        output_dir:str):
    """
    Function for saving the annotation masks
    of the different objects in the format 
    required for PyCocoCreatorTools
    img_number= str; image number to save the
                binary mask
    dict_color_object= dict; dictionary of 
                        green value and 
                        object name
    output_dir = str; Path to directory where
                annotation masks will be saved
    """
    instance_num = 0
    for green, object in dict_color_object.items():
        object = object.lower()
        annotationmask_name = f"{img_number}_{object}_{instance_num}.png"
        ColourBGR = (BLUE, green, RED)
        anno_mask = annotation_mask_maker(bin_mask,
                                        ColourBGR)
        anno_mask_path = os.path.join(output_dir,
                        OUTPUT_FOLDERS[0],
                        annotationmask_name)
        instance_num +=1
        cv2.imwrite(anno_mask_path, anno_mask)

def annotation_mask_maker(bin_mask, ColourBGR):
    """
    Makes a black and white annotation masks for each object instance 
    Input: The binary mask with each object instance in a different colour, Colour is the tuple in BGR corresponding to object instance.
    Output: A binary mask showing the object instance in white while the rest of the image is black.
    """
    kernel = np.ones((3,3),np.uint8)
    thresh_l = ColourBGR
    thresh_h = ColourBGR
    bin_mask = cv2.cvtColor(np.array(bin_mask), cv2.COLOR_RGB2BGR)
    anno_mask = cv2.inRange(bin_mask, thresh_l, thresh_h)
    anno_mask = cv2.morphologyEx(anno_mask, cv2.MORPH_OPEN, kernel)
    return anno_mask