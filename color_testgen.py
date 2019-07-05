import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
from os import listdir
from os.path import isfile, join
import xml.etree.cElementTree as ET
import cv2
from tqdm import tqdm
import time
import os

'''
Software originally written by Andress Mafalda
Tweaked by Mohammed Al-Rawi

You can download further fonts from:
https://fonts.google.com/

After downloading the fonts, extract them into the "fonts" folder within this project
Output images are stored into the folder "output_images", and annotations 
(i.e. bounding boxes) are stored into a folder called "annotations""

Becareful with changing the parameters, as it might get into an infinite loop, 
This program still need imporovements, by finding the relation between the font, 
text size, and some other parameters to prevent it from entering an infinite loop.

'''

nimages = 30
dictionary_size = 88623
upper_case_prob = 0.5
use_single_font_per_image = True # not working yet!
text_scale_distributoin = 1 # 1: will produce all text in the same sacle, if sizeX is equatl to sizeY, for each image; the higher the value, more scales are included
sizeX, sizeY = (256, 256)
r_background, g_background,  b_background = (0,0,0)
rMin, gMin, bMin = (200, 200, 200) # lower bound colors used to draw the text
rMax, gMax, bMax = (255, 255, 255) # lower bound colors used to draw the text
min_num_words, max_num_words = (1,2)
text_size_based_on_num_words = True
if not text_size_based_on_num_words:
    min_txt_size, max_txt_size = (sizeX//16, sizeY//4) # (32, 8) # 
upper_bound_bounding_box_to_x_ratio = 1 #0.75 
generate_bounding_box_annotations = False
font_dir = './fonts/' # folder containig TTF fonts, https://fonts.google.com/ can be used, just download the fonts to this folder
seed_value = time.time()
np.random.seed(int(seed_value))
random.seed(int(seed_value))

os.makedirs('./Results/%s' % 'output_images/', exist_ok=True)
os.makedirs('./Results/%s' % 'annotations/', exist_ok=True)

annotation_folder = './Results/annotations/'
out_image_folder = './Results/output_images/'


def text_cleaner (dirty_text):
    # CLEANS NOT WANTED CHARACTERES AND SENDS STRING IN LOWERCASE
    clean_text = ''.join(c for c in dirty_text if c not in '\|"?>.<,`~(){}<>;:!@#$%^&*_-=+-*\\ \/[]\' \|"?>.<,`~')
    return clean_text.lower()

def area(coords, posXmax, posXmin, posYmax, posYmin):  # returns None if rectangles don't intersect
    dx = min(coords[1], posXmax) - max(coords[0], posXmin)
    dy = min(coords[3], posYmax) - max(coords[2], posYmin)
    if (dx >= 0) and (dy >= 0):
        return dx * dy
    return None

fontFiles = [f for f in listdir(font_dir) if isfile(join(font_dir, f))]
# Read file of words

with open ("90K dictionary Jaderberg for IAM and numbers.txt") as f:
    data = f.read()
    words = data.split("\n")
    # Delete the end of file:
    del words[-1]
print("Data Loaded...!")
length = np.shape(words)[0]
print (length," Total words")
# y = np.arange(0, length, 1)

# CLEAN THE WORDS:
for i in range (0, len(words)):
    words[i] = text_cleaner(words[i])

print (dictionary_size+1," Dictionary size")
print('Generating images:')

time.sleep(1)
pbar = tqdm(total=nimages); 
time.sleep(1)

R=r_background; G=g_background; B=b_background
for i in range(0, nimages):
    pbar.update(1)        
    coords = list()
    textlist = list()    
    image = Image.new("RGB", (sizeX, sizeY), (R, G, B))
    
    draw = ImageDraw.Draw(image)

    number_words = random.randint(min_num_words, max_num_words)
    if text_size_based_on_num_words:
        min_txt_size, max_txt_size = \
        (sizeX//(text_scale_distributoin*(number_words+5)), sizeY//(number_words+5))       


    for j in range(0, number_words):
        
        word_index = random.randint(0, dictionary_size)
        text = words[word_index]
        if (random.random() >= upper_case_prob):
            text = text.upper()
        text_size = random.randint(min_txt_size, max_txt_size)
        if use_single_font_per_image and j==0:
            randomFont = random.randint(0, len(fontFiles)-1)
        font = ImageFont.truetype(font_dir + fontFiles[randomFont], text_size, encoding="unic")            
        bound = font.getsize(text)
        text_size = random.randint(min_txt_size, max_txt_size)
        randomFont = random.randint(0, len(fontFiles)-1)
        while bound[0] > (sizeX*upper_bound_bounding_box_to_x_ratio):           
            font = ImageFont.truetype(font_dir + fontFiles[randomFont], text_size, encoding="unic")
            bound = font.getsize(text)
            text_size = text_size - 1
            

        if j == 0:
            posX = random.randint(0, (sizeX - bound[0]))
            posY = random.randint(0, (sizeY - bound[1]))
            coordinates = [posX, posX + bound[0], posY, posY + bound[1]]
            coords.append(coordinates)
            textlist.append(text)
            Rt = random.randint(rMin, rMax)
            Gt = random.randint(gMin, gMax)
            Bt = random.randint(bMin, bMax)
            draw.text((posX, posY), text, (Rt, Gt, Bt), font=font)
            # draw.rectangle(((posX, posY), (posX + bound[0], posY + bound[1])), outline = "blue")
            continue

        verif = False
        
        while verif == False:
            text_size = random.randint(min_txt_size, max_txt_size)
            if not (use_single_font_per_image and j!=0):                
                randomFont = random.randint(0, len(fontFiles)-1)
            font = ImageFont.truetype(font_dir + fontFiles[randomFont], text_size, encoding="unic")
            bound = font.getsize(text)
            text_size = random.randint(min_txt_size, max_txt_size)
            if not (use_single_font_per_image and j!=0):                
                randomFont = random.randint(0, len(fontFiles)-1)                
                font = ImageFont.truetype(font_dir + fontFiles[randomFont], text_size, encoding="unic")
            while bound[0] > (sizeX * upper_bound_bounding_box_to_x_ratio):                                
                bound = font.getsize(text)
                text_size = text_size - 1

            # Position of X
            posX = random.randint(0, (sizeX - bound[0]))

            # Postion of Y
            posY = random.randint(0, (sizeY - bound[1]))

            for k in range(0, len(coords)):

                exist = area(coords[k], posX + bound[0], posX, posY + bound[1], posY)

                if exist != None:
                    verif = False
                    break
                if exist == None:
                    verif = True
                    continue

        coordinates = [posX, posX + bound[0], posY, posY + bound[1]]
        coords.append(coordinates)
        Rt = random.randint(rMin, rMax)
        Gt = random.randint(gMin, gMax)
        Bt = random.randint(bMin, bMax)
        draw.text((posX, posY), text, (Rt, Gt, Bt), font=font)
        textlist.append(text)

        # draw.rectangle(((posX, posY), (posX + bound[0], posY + bound[1])), outline = "blue")

    image.save( out_image_folder + 'img_' + str(i) + '_'+ str(int(time.time()))+'.png')
    image = cv2.imread(out_image_folder + 'img_' + str(i) + '.png')
    if generate_bounding_box_annotations:
        root = ET.Element("annotation")
        image_name = str('img_' + str(i) + '.png')
        ET.SubElement(root, "filename").text = image_name
        size = ET.SubElement(root, "size")
        ET.SubElement(size, "width").text = str(image.shape[1])
        ET.SubElement(size, "height").text = str(image.shape[0])
        ET.SubElement(size, "depth").text = str(image.shape[2])
    
        for m in range(0, len(textlist)):
            obj = ET.SubElement(root, "object")
            ET.SubElement(obj, "name").text = textlist[m]
            xmlbbox = ET.SubElement(obj, "bndbox")
            ET.SubElement(xmlbbox, "xmin").text = str(coords[m][0])
            ET.SubElement(xmlbbox, "ymin").text = str(coords[m][2])
            ET.SubElement(xmlbbox, "xmax").text = str(coords[m][1])
            ET.SubElement(xmlbbox, "ymax").text = str(coords[m][3])
    
        tree = ET.ElementTree(root)
        image_name = image_name[:-4] + ".xml"
        tree.write(annotation_folder+"%s" % (image_name))
pbar.close();   del pbar    
print("\n Generation of Images and Annotations Done..!")
