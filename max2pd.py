import json
import tkinter as tk
from tkinter import filedialog
import os
import sys


class pcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    ORANGE = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

welcome_string = '''

                                         
     ____    ____      _      ____  ____    _____    _______ ______    
    |_   \  /   _|    / \    |_  _||_  _|  / ___ `. |_   __ |_   _ `.  
      |   \/   |     / _ \     \ \  / /   |_/___) |   | |__) || | `. \ 
      | |\  /| |    / ___ \     > `' <     .'____.'   |  ___/ | |  | | 
     _| |_\/_| |_ _/ /   \ \_ _/ /'`\ \_  / /_____   _| |_   _| |_.' / 
    |_____||_____|____| |____|____||____| |_______| |_____| |______.'  
                                                                   

                                      version 0.0.1
==========================================================================================
                 A tool will convert all the Max patches to PD patches.
==========================================================================================
                This tool is a free software distributed under the GPLv3 license. 
------------------------------------------------------------------------------------------

'''

print(welcome_string)

print(f'{pcolors.BLUE} Please, select the Max patch file: {pcolors.ENDC}')

import time
time.sleep(1.5)

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()
FILE = file_path

if FILE == '':
    print(f'{pcolors.FAIL} No file selected. {pcolors.ENDC}')
    print(f'{pcolors.FAIL} Exiting... {pcolors.ENDC}')
    time.sleep(1.4)
    sys.exit()
    
# ====================================

def convert2pd(FILE):
    with open(FILE) as json_file:
        data = json.load(json_file)

    PATCH = max2pd(data)
    PD_FILE = os.path.splitext(FILE)[0] + '.pd'
    print(f'{pcolors.BLUE} PD patch will be saved in: {pcolors.ENDC}', PD_FILE)
    with open(PD_FILE, "w") as f:
        for item in PATCH:
            f.write(item + "\n")
    f.close()
    return PD_FILE

# ====================================

def max2pd(json_data):
    with open("max2pd.json") as json_file:
        max2pd_objects = json.load(json_file)
    INDEX = 0
    PATCH = []
    OBJECTS_ID = {}
    subpatcher = len(json_data.keys())
    key = 'patcher'
    patcher = json_data[key]
    canvas = json_data[key]['rect']
    canvas_string = ''
    for i in canvas: 
        canvas_string += str(i) + ' '
    if subpatcher == 1:
        canvas_string = '#N canvas ' + canvas_string + ' ' + '10' + ';'
    else:
        subpatcher_name = json_data['text']
        canvas_string = '#N canvas ' + canvas_string + '0 ' + subpatcher_name + ';'
    
    PATCH.append(canvas_string)
    boxes = patcher['boxes']
    lines = patcher['lines']
    for box in boxes:
        sub_patch = False
        get_box_id = str(box['box']['id'])
        OBJECTS_ID[get_box_id] = INDEX
        INDEX = INDEX + 1
        get_box_id = get_box_id.split('obj-')[1]
        if box['box']['maxclass'] == 'newobj': # Objetos
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + " " + str(x_y_position[1])
            OBJECT_NAME = box['box']['text']
            OBJECT_NAME = OBJECT_NAME.split(' ')[0]
            try:
                PD_OBJECT_NAME = max2pd_objects['max2pd'][OBJECT_NAME] ## Check if there is a match object in the JSON file
            except:
                try:
                    PD_OBJECT_NAME = max2pd_objects['pdobjects'][OBJECT_NAME] ## Check if it is one PD object
                
                
                except: # if it is not a PD object, it is a subpatcher (p) or a poly~
                    if OBJECT_NAME == 'p':
                        subpatcher_name = box['box']['text']
                        subpatcher_name = subpatcher_name.split('p')[1]
                        print(f'{pcolors.BLUE}Converting {subpatcher_name} subpatch...{pcolors.ENDC}')
                        sub_patch = max2pd(box['box']) # Aqui vai a recursão
                        restore_window = '#X restore ' + x_y_position + ' pd ' + subpatcher_name + ';'
                        sub_patch.append(restore_window)
                        for line in sub_patch:
                            PATCH.append(line)
                        sub_patch = True
                    
                    elif OBJECT_NAME == 'poly~':
                        
                        subpatcher_name = box['box']['text']
                        subpatcher_name = subpatcher_name.split('poly~')[1]
                        print(f'{pcolors.BLUE}Converting {subpatcher_name} subpatch...{pcolors.ENDC}')
                        folder = os.path.dirname(FILE)
                        # Folder + OBJECT_NAME
                        subpatch_filename = folder + '/' + OBJECT_NAME + '.maxpat'
                        if os.path.isfile(subpatch_filename):
                            convert2pd(subpatch_filename)
                        else:
                            print(f'{pcolors.FAIL}Sorry, the poly~ subpath not found: ' + f'{pcolors.BLUE}' + OBJECT_NAME + f'{pcolors.ENDC}')
                            # write names of objects not found
                        # Aqui vai a recursão
                        clone_obj = '#X obj ' + x_y_position + subpatcher_name + ';'
                        PATCH.append(clone_obj)
                    
                    else:    
                        # Get folder of FILE
                        folder = os.path.dirname(FILE)
                        # Folder + OBJECT_NAME
                        subpatch_filename = folder + '/' + OBJECT_NAME + '.maxpat'
                        if os.path.isfile(subpatch_filename):
                            convert2pd(subpatch_filename)
                        else:                      
                            print(f'{pcolors.FAIL}Object not found: ' + f'{pcolors.BLUE}' + OBJECT_NAME + f'{pcolors.ENDC}')
                            # write names of objects not found
                            
                            #
                            with open('objects_not_found.txt', 'a') as f:
                                f.write(OBJECT_NAME + '\n')

                    PD_OBJECT_NAME = OBJECT_NAME
            
            if sub_patch == False:
                OBJECT_ARGS = box['box']['text'].split(' ')[1:]
                OBJECT_ARGS = ' '.join(OBJECT_ARGS)
                VALUE = '#X obj ' + x_y_position + ' ' + PD_OBJECT_NAME + ' ' + OBJECT_ARGS + ' ;'
                PATCH.append(VALUE)

        # elif box['box']['maxclass'] == 'slider': # Sliders
        #     x_y_position = box['box']['patching_rect'][:2]
        #     x_y_position = str(x_y_position[0]) + str(x_y_position[1])
        
        # =====================================================
        # elif box['box']['maxclass'] == 'button': # Bang 
        #     x_y_position = box['box']['patching_rect'][:2]
        #     x_y_position = str(x_y_position[0]) + str(x_y_position[1])
        
        # =====================================================

        elif box['box']['maxclass'] == 'toggle': # Toggle
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + str(x_y_position[1])



        elif box['box']['maxclass'] == 'inlet':
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + " " + str(x_y_position[1])
            VALUE = "#X " + "obj" + " " + x_y_position + " " + "inlet" + " " + ";"
            PATCH.append(VALUE)
        
        # =====================================================
        elif box['box']['maxclass'] == 'outlet':
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + " " + str(x_y_position[1])
            VALUE = "#X " + "obj" + " " + x_y_position + " " + "outlet" + " " + ";"
            PATCH.append(VALUE)
        
        # =====================================================
        elif box['box']['maxclass'] == 'message': # Mensagens
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + " " + str(x_y_position[1])
            try:
                message_text = box['box']['text']
            except:
                message_text = ' '
            VALUE = "#X msg" + " " + x_y_position + " " + message_text + " ;" # E o ID???
            PATCH.append(VALUE)


        elif box['box']['maxclass'] == 'comment': # Textos
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + " " + str(x_y_position[1])
            try:
                message_text = box['box']['text']
            except:
                message_text = ' '
            VALUE = "#X text" + " " + x_y_position + " " + message_text + " ;" 
            PATCH.append(VALUE)
            
        # =====================================================
        else: 
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + str(x_y_position[1])
            print(f'{pcolors.FAIL}NEED TO BE IMPLEMENTEND: ', box['box']['maxclass'] , pcolors.ENDC)
            x_y_position = box['box']['patching_rect'][:2]
                
    ## This will change all the 
    for line in lines:
        connections = []
        connections.append(OBJECTS_ID[line['patchline']['source'][0]])
        connections.append(line['patchline']['source'][1])
        connections.append(OBJECTS_ID[line['patchline']['destination'][0]])
        connections.append(line['patchline']['destination'][1])
        connections = ' '.join(str(x) for x in connections)
        connections = '#X connect ' + connections + ' ;'
        PATCH.append(connections)
    
    time.sleep(1.3)
    print(f'{pcolors.GREEN}Patch created!{pcolors.ENDC}')
    return PATCH

convert2pd(FILE)


## read 
with open('objects_not_found.txt') as f:
    # if file not exists, create it
    lines = f.readlines()
# remove \n from the end of each line
lines = [line.rstrip('\n') for line in lines]
# remove duplicates


seen = set()
result = []
for item in lines:
    if item not in seen:
        seen.add(item)
        result.append(item)

print(result)

## delte objects_not_found.txt
os.remove('objects_not_found.txt')

# write lines to file
with open('PLEASE_REPORT_missing_objects.txt', 'w') as f:
    for line in result:
        f.write(line + '\n')