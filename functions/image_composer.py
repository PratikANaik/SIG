import cv2
from PIL import Image
from tqdm import tqdm
from functions.folder_check import FOLDER_LIST, OUTPUT_FOLDERS
import os
from functions import folder_check as fldr_chk
import random

OUTPUT_EXTENSION = '.jpg'

class ImgComposer:
    def __init__(self,
                resolution: tuple,
                classes_to_include: list,
                num_of_images:int,
                max_objects_in_image:int,
                output_directory:str,
                efo_directory:str,
                include_negative_examples=[]):
        self.classes_to_include = classes_to_include
        self.include_negative_examples = include_negative_examples
        self.num_of_images = num_of_images
        self.max_objects_in_images = max_objects_in_image
        self.output_directory = output_directory
        self.efo_directory = efo_directory
        self.resolution = resolution # (width, height)
    
    def compose(self):
        for imgno in tqdm(range(self.num_of_images)):
            
            img_number = str(fldr_chk.get_num(self.output_directory,
                                        OUTPUT_EXTENSION))
            final_path = os.path.join(self.output_directory,
                                img_number)
            img_name = f"{final_path}.jpg"
            
            # Coloured annotation mask
            cm_path = os.path.join(self.output_directory,
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
            random_bg = random.choice(os.listdir(FOLDER_LIST[0]))
            to_background = os.path.join(FOLDER_LIST[0],
                            random_bg)
            background = Image.open(to_background)
            background = background.resize(self.resolution,
                            Image.ANTIALIAS)
            
            # Black image for binary mask
            bin_mask = Image.new('RGBA',
                        background.size,
                        color='black')
            

