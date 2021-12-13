import os
from segmentation_refinement.main import Refiner
import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import cv2
import glob
import segmentation_refinement as refine
from tqdm import tqdm
from functions.data_loader import RescaleT
from functions.data_loader import ToTensor
from functions.data_loader import ToTensorLab
from functions.data_loader import SalObjDataset
import functions.folder_check as fldr_chk
from PIL import Image
import numpy as np
from model import U2NET

def normPRED(d):
    ma = torch.max(d)
    mi = torch.min(d)

    dn = (d-mi)/(ma-mi)

    return dn

def u2_loader(model_dir):
    """
    Loads the model for inferences.
    It will be called inside the function for foreground extraction
    'model_dir' is path to the directory where model is located
    """
    net = U2NET(3,1)
    if torch.cuda.is_available():
        net.load_state_dict(torch.load(model_dir, map_location='cuda'))
        net.cuda()
    else:
        net.load_state_dict(torch.load(model_dir, map_location='cpu'))
    net.eval()
    model_state = "loaded"
    return net, model_state

def dataloader(source_folder):
    """
    Takes the path to the subfolder and loads the images in the subfolder to make masks
    """
    img_name_list = glob.glob(source_folder + os.sep + '*')
    test_salobj_dataset = SalObjDataset(img_name_list = img_name_list,
                                        lbl_name_list = [],
                                        transform=transforms.Compose([RescaleT(320),
                                                                      ToTensorLab(flag=0)])
                                        )
    test_salobj_dataloader = DataLoader(test_salobj_dataset,
                                        batch_size=1,
                                        shuffle=False,
                                        num_workers=1)
    return test_salobj_dataset, test_salobj_dataloader,img_name_list

def extract_foregrounds_U2(source_folder : str,
                            target_folder : str,
                            mask_folder : str,
                            clean_up_post : bool):
    """
    Extracting foregrounds from source folder
    and saving them as .png files in target 
    folder and binary masks in mask_folder.
    Inputs = 
    source_folder: path to directory of 
    images to extract; This is a subfolder
    target_folder: path to directory where 
    images are to be saved
    mask_folder: path to directory where masks
    are to be saved
    clean_up_post: Bool for using the segmentation
    refinement network 'CascadePSP' to fix the 
    masks prepared by the U2Net.
    Recommended to have hardware acceleration
    when using this
    """
    if clean_up_post:
        if torch.cuda.is_available():
            refiner = refine.Refiner(device='cuda:0')
        else:
            refiner = refine.Refiner(device='cpu')

    model_dir = './model/saved_models/u2net.pth'
    model_state = 'empty'
    if model_state == 'empty':
        net, model_state = u2_loader(model_dir)
    
    # Get subfolder in Dataloader
    tsds, tsdl, img_name_list = dataloader(source_folder)
    # tsds = test salient data set
    # tsdl = test salient data loader
    for i_test, data_test in tqdm(enumerate(tsdl)):
        inputs_test = data_test['image']
        inputs_test = inputs_test.type(torch.FloatTensor)

        if torch.cuda.is_available():
            inputs_test = Variable(inputs_test.cuda())
        else:
            inputs_test = Variable(inputs_test)
        
        d1, d2, d3, d4, d5, d6, d7 = net(inputs_test)

        # Normalization
        pred = d1[:,0,:,:]
        pred = normPRED(pred)

        # Making mask from prediction
        image_name = img_name_list[i_test]
        predict = pred.squeeze()
        predict_np = predict.cpu().data.numpy()
        mask = Image.fromarray(predict_np*255).convert('RGB')
        mask = cv2.cvtColor(np.array(mask), cv2.COLOR_BGR2GRAY)
        image = cv2.imread(image_name)
        mask = cv2.resize(mask,(image.shape[1],
                            image.shape[0]))
        del d1,d2, d3, d4, d5, d6, d7

        # Cleaning up mask
        if clean_up_post:
            mask = post_process_mask(refine_net=refiner,
                        image=image,
                        mask=mask)

        # Saving the extracted foreground and mask
        number = str(fldr_chk.get_num(target_folder=mask_folder,
                                extension='png'))
        fg_path = os.path.join(target_folder,number)
        mask_path = os.path.join(mask_folder, number)
        mask_path = f'{mask_path}.png'
        fg_path = f'{fg_path}.png'
        save_extractedfg_and_mask(image, mask,
                                fg_path,
                                mask_path)

def save_extractedfg_and_mask(image,
                                mask,
                                fg_path,
                                mask_path):
    """
    Saves the extracted foreground and mask as
    png files
    Input: 
    image: image to save 
    mask : mask to save
    number: number will be used as the name
    to save the image and mask 
    """
    # Saving the mask
    cv2.imwrite(mask_path, mask)
    # Extracting foreground with mask and image
    image = Image.fromarray(image)
    mask = Image.fromarray(mask)
    image.putalpha(mask)
    image.save(fg_path)

def post_process_mask(refine_net: Refiner,
                        image,
                        mask):
    """
    Function for post processing with the PSPCascade
    mask refinement network
    Inputs:
    refiner: refinement network
    image: image corresponding to mask
    mask: the mask that needs to be cleaned up
    fast
    """
    output_mask = refine_net(image, mask,
                            fast=True,
                            L=900)

    # Binarizing the image to avoid gray areas
    ret, mask = cv2.threshold(output_mask,
                            210, 255,
                            cv2.THRESH_BINARY)
    return mask