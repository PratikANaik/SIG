"""
Functions for extracting foreground objects from images
There are two ways of doing this:
1.) Using U^2 Net from https://github.com/xuebinqin/U-2-Net. Salient Object
Detection network which runs at ~30fps. Requires output to binarized and then 
CascadePSP is used for cleaning the foreground image.
2.) Using ChromaKey methods. Faster but restriction on what kind of 
images can be used.
"""
# %%

import folder_check as fldr_chk
import chroma_key as chr_key
import os
from tqdm import tqdm
from folder_check import FOLDER_LIST, OUTPUT_FOLDERS

fldr_chk.check_for_folders(dir_path="./Data",
                     list_to_check = FOLDER_LIST)
fldr_chk.check_for_folders(dir_path="./Output",
                    list_to_check= OUTPUT_FOLDERS)

CLASSES_PATH = os.path.join("../Data", "Classes")
EFOBJECTS_PATH = os.path.join("../Output", "EFObjects")
MASK_PATH = os.path.join("../Output", "Mask")

Extensions = ['.jpg', '.png', '.jpeg', '.bmp']

# The Foreground Extractor class
class FgExtractor:
    def __init__(self, dir_images: str,
                 extractor: str,
                 clean_after_extract: bool):
        """
        Initializing the foreground extractor
        dir_images : Directory containing the subfolders with the images.
            Subfolder names should be names of the objects
        extractor : either 'ChromaKey' or 'U2Net'
        clean_after_extract : bool for using CascadePSP network to clean up
            foreground object
        """
        self.dir_images = dir_images
        self.extractor = extractor
        self.clean_after_extract = clean_after_extract

    def print_settings(self):
        return (f"""Path to directory is {self.dir_images}, 
                Extraction is done using {self.extractor},
                clean_after_extract is {self.clean_after_extract}.""")

    def extract_foregrounds(self):
        """
        Function to extract the foregrounds for the 
        FgExtractor class.
        """
        # Check for folder structure in Classes
        # EFObjects and Mask
        fldr_chk.replicate_folder_tree(CLASSES_PATH,
                                       EFOBJECTS_PATH)

        fldr_chk.replicate_folder_tree(CLASSES_PATH,
                                       MASK_PATH)

        # The folders are in place. Now to go through them
        # and extract the fg objects from images
        for subfolder in tqdm(os.listdir(CLASSES_PATH)):
            cls_subfldr = os.path.join(CLASSES_PATH,
                         subfolder)
            efo_subfldr = os.path.join(EFOBJECTS_PATH,
                            subfolder)
            msk_subfldr = os.path.join(MASK_PATH, 
                            subfolder)
            

            # Switch could be used here when Python gets it
            if self.extractor == "U2Net":
                pass

            elif self.extractor == "ChromaKey":
                for file in tqdm(cls_subfldr):
                    if file.endswith(tuple(Extensions)):
                        img_path = os.path.join(cls_subfldr,
                                    file)
                        chr_key.extract_with_chromakey(img_path,
                                mask_folder=msk_subfldr,
                                extracted_fg_folder=efo_subfldr)

        
            
# %%
