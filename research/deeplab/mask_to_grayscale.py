# -*- coding: utf-8 -*-
"""Mask_to_grayscale.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GREjiciq9ICj_SH5GP5UyzAFeeNFUYVR
"""


import os
import cv2
import numpy as np
import json
import os

import sys
VH_INPUTS_DIR = os.getenv('VH_INPUTS_DIR')
VH_OUTPUTS_DIR = os.getenv('VH_OUTPUTS_DIR')

def mFileListPNG(vPathOfFile):
    """This section is created in fetching only .png files """
    vPath = vPathOfFile
    vFilesNamesPNG = []
    for vRootDir, vCurrentDir, vFile in os.walk(vPath):
        del vCurrentDir[:]
        for file in vFile:
            if '.png' in file:
                vFilesNamesPNG.append(os.path.join(vRootDir, file))
    return vFilesNamesPNG


def m_create_segmentation(rgb_masks_directory, output_masks_directory, colours_dict):

    colour_lists = colours_dict.keys()
    for img_elm in mFileListPNG(rgb_masks_directory):
        image_path = img_elm
        output_image_name = os.path.basename(image_path) 
        output_image_path = os.path.join(output_masks_directory, output_image_name) 
        image_bgr = cv2.imread(image_path,cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        unique_rgb = np.unique(image.reshape(-1, image.shape[2]), axis=0)
        img_height, img_width ,channels = image.shape
        new_image = np.full((img_height, img_width), 255,dtype=np.uint8)
        r,g,b=0,1,2

        vHexColorList = []
        for i in unique_rgb:
            x=tuple(i)
            hex= '#%02x%02x%02x' % x
            if hex in colour_lists:

                if hex == '#000000':
                    continue 
                index_colour = colours_dict[hex]
                vHexColorList.append(hex)
                r_query = x[0]
                g_query = x[1]
                b_query = x[2]
                array_x_y = (np.where((image[:,:,r] == r_query) & (image[:,:,g] == g_query) & (image[:,:,b] == b_query)))
                array_x,array_y = array_x_y
                coordinates = zip(array_x,array_y)
                list_cod = list(coordinates)
                for x,y in list_cod:
                    new_image[x][y] = index_colour

        
        
        cv2.imwrite(output_image_path,new_image)



def create_labels(metadata_file_path, labels_lists, labels_dict):
    # returns JSON object as  
    # a dictionary 
    with open(metadata_file_path,'r') as read_json:
        data = json.load(read_json) 
          
        # Iterating through the json 
        # list 
        labels_metadata_dict={}
        colours_metadata_dict={}
        value_list = data['roots']

        for index,value in enumerate(value_list): 
          label = value["value"]
          label_colour =  label["color"]
          label_name = label["displayLabel"]

          if label_name in labels_lists:
            grayscale_index = labels_dict[label_name]
            labels_metadata_dict[grayscale_index] ={'gray_scale_value': grayscale_index, 
                                'label_name': label_name,
                                'label_colour': label_colour
                                }
            colours_metadata_dict[label_colour] = grayscale_index
        return colours_metadata_dict,labels_metadata_dict  




def create_segmentation(rgb_images_dir, class_index_file, img_output_dir , metadata_file_path):
    index_scale_dict={}
    file = open(class_index_file,'r')
    labels_dict = {}
    labels_list = []
    for index,labels in enumerate(file):
        label = labels.strip('\n')
        labels_dict[label]=index
        labels_list.append(label)

    print('labels_lists',labels_list)    
    print('metadata_file_path',metadata_file_path)
    colours_dict,labels_metadata_dict = create_labels(metadata_file_path, labels_list, labels_dict) 
    
    m_create_segmentation(rgb_images_dir, img_output_dir, colours_dict)    

    return labels_metadata_dict


    # #print(json_dir, class_index_file, img_path)
    # entry = {}
    # entry["logger"] = "AVSI"
    # entry["source"] = "tensorflow"
    # entry["message"] = 'labels and corresponding label ids {}'.format(index_scale_dict)  # LoggerManipulationMessage
    # log.info(entry)

rgb_images_dir = os.path.join(VH_INPUTS_DIR, 'RGB-Masks-folder')
class_index_file = os.path.join(VH_INPUTS_DIR, 'class-index-file')
metadata_file_path = os.path.join(VH_INPUTS_DIR, 'metadata-filepath')
img_output_dir = os.path.join(VH_OUTPUTS_DIR, 'Output-Directory')

import time 
startTime = time.perf_counter()
labels_metadata_dict = create_segmentation(rgb_images_dir, class_index_file, img_output_dir , metadata_file_path)
endTime = time.perf_counter()
print("Time taken: ", startTime - endTime)



