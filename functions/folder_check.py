"""
Functions for making and checking the folder tree that the project uses
"""
import os

# List of folders
FOLDER_LIST = ['Annotations', 'Backgrounds', 'ColouredMasks', 'Classes',
                 'Composed', 'EFObjects', 'Mask', 'PNG']

def check_for_folders(dir_path=os.getcwd(), list_to_check=FOLDER_LIST):
    """
    Iterate through folder list and check if folder exists, if not then it 
    will be created in the directory.
    Input: dir_path = Path of directory to check, default is current working
            directory
            folder_list = List containing folders which should be present
    Output: Folders will be created if they do not yet exist
    """
    if os.listdir(dir_path) is []:
        # Set up everything
        setup_folders(dir_path, list_to_check)
    
    else:
        for folder in FOLDER_LIST:
            if folder not in os.listdir(dir_path):
                folder_path = os.path.join(dir_path, folder)
                os.mkdir(folder_path)

def setup_folders(dir_path, folders_to_setup:list):
    """
    Setup the folders from the list passed in the directory path provided
    """
    for folder in folders_to_setup:
        folder_path = os.path.join(dir_path, folder)
        os.mkdir(folder_path)

def replicate_folder_tree(srcfldr, dstfldr):
    """
    Checks if the folders in the source and destination
    match. If they don't, folders are created in the 
    destination.
    """
    if os.path.isdir(dstfldr):
        print (os.path.isdir(dstfldr))
        if os.listdir(srcfldr) != os.listdir(dstfldr):
            for fldrname in os.listdir(srcfldr): 
                if fldrname not in os.listdir(dstfldr):
                    os.mkdir(os.path.join(dstfldr,fldrname))
        else:
            print(f"""{os.path.basename(srcfldr)} and
                    {os.path.basename(srcfldr)}
                    have the same subfolders""")
    else:
        os.mkdir(dstfldr)
        for fldrname in os.listdir(srcfldr):
            if fldrname not in os.listdir(dstfldr):
                os.mkdir(os.path.join(dstfldr,fldrname))