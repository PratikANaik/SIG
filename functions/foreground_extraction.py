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
import PIL
import cv2
import numpy as np
import folder_check as fldr_chk
import chroma_key as chr_key
import os


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

        fldr_chk.check_for_folders(dir_path="../Data")
        Classes_path = os.path.join("../Data", "Classes")
        EFObjects_path = os.path.join("../Data", "EFObjects")
        Mask_path = os.path.join("../Data", "Mask")

        # Check for folder structure in Classes
        # EFObjects and Mask
        fldr_chk.replicate_folder_tree(Classes_path,
                                       EFObjects_path)

        fldr_chk.replicate_folder_tree(Classes_path,
                                       Mask_path)

        # The folders are in place. Now to go through them
        # and extract the fg objects from images

# %%
