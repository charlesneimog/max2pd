import json
import tkinter as tk
from tkinter import filedialog
import os
import sys
import time

THERE_IS_ERRORS = False

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


def print_in_thinker(string, color, root):
    # Draw the string always on the same line
    root.title(string)
    msg = tk.Message(root, text = string)
    msg.config(fg=color, font=('Palatino', 12), width=500, justify='center')
    # msg pack in the same line
    msg.pack()
    root.update()
    msg.destroy()
    time.sleep(0.3) ## To take time to see the messages and errors

# ====================================

def convert2pd(FILE, TK_GUI):
    with open(FILE) as json_file:
        data = json.load(json_file)
    # took the folder of FILE
    MAIN_FOLDER = os.path.dirname(FILE)
    PATCH = max2pd(data, MAIN_FOLDER, TK_GUI)
    PD_FILE = os.path.splitext(FILE)[0] + '.pd'
    # GET NAME OF PATCH
    PATCH_MSG = os.path.basename(FILE)
    PATCH_MSG = PATCH_MSG.replace('.maxpat', '')
    print_in_thinker(f'PD patch saved in:  {PATCH_MSG}', 'green', TK_GUI)
    with open(PD_FILE, "w") as f:
        for item in PATCH:
            f.write(item + "\n")
    f.close()
    return PD_FILE

# ====================================

def max2pd(json_data, MAIN_FOLDER, TK_GUI):
    with open("./resources/max2pd.json") as json_file:
        max2pd_objects = json.load(json_file)
    INDEX = 0
    MULTISLIDER_INDEX = 0
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
        special_case = False
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
                    ## SOME SPECIAL CASES
                                        
                    if OBJECT_NAME == 'p':
                        subpatcher_name = box['box']['text']
                        subpatcher_name = subpatcher_name.split('p')[1]
                        print_in_thinker(f' Converting {subpatcher_name} subpatch... ', 'green', TK_GUI)
                        sub_patch = max2pd(box['box'], MAIN_FOLDER, TK_GUI) # Aqui vai a recursão
                        restore_window = '#X restore ' + x_y_position + ' pd ' + subpatcher_name + ';'
                        sub_patch.append(restore_window)
                        for line in sub_patch:
                            PATCH.append(line)
                        special_case = True
                        print_in_thinker(f'Subpatch {subpatcher_name} done! ', 'green', TK_GUI)
                    
                    elif OBJECT_NAME == 'in':
                        special_case = True
                        VALUE = '#X obj ' + x_y_position + ' ' + "inlet" + ' ' ' ;'
                        PATCH.append(VALUE)
                    
                    elif OBJECT_NAME == 'out~':
                        special_case = True
                        VALUE = '#X obj ' + x_y_position + ' ' + "outlet~" + ' ' ' ;'
                        PATCH.append(VALUE)
                        
                    elif OBJECT_NAME == 'poly~':
                        subpatcher_name = box['box']['text']
                        subpatcher_name = subpatcher_name.split('poly~ ')[1]
                        subpatcher_name = subpatcher_name.split(' ')[0]
                        print_in_thinker(f' Converting {subpatcher_name} subpatch... ', 'green', TK_GUI)

                        # Folder + OBJECT_NAME
                        subpatch_filename = MAIN_FOLDER + '/' + subpatcher_name + '.maxpat'
                        if os.path.isfile(subpatch_filename):
                            convert2pd(subpatch_filename, TK_GUI)
                        else:
                            print_in_thinker(f'Sorry, the poly~ subpath not found: {OBJECT_NAME}', 'red', TK_GUI)
                        clone_obj = '#X obj ' + x_y_position + " clone " + subpatcher_name + " 32" + ';'
                        PATCH.append(clone_obj)
                        special_case = True                   
                    
                    else:    
                       # Folder + OBJECT_NAME
                        subpatch_filename = MAIN_FOLDER + '/' + OBJECT_NAME + '.maxpat'
                        if os.path.isfile(subpatch_filename):
                            convert2pd(subpatch_filename, TK_GUI)
                        else:                      

                            print_in_thinker(f'Object not found: {OBJECT_NAME}', 'red', TK_GUI)
                            with open('objects_not_found.txt', 'a') as f:
                                f.write(OBJECT_NAME + '\n')
                            global THERE_IS_ERRORS
                            THERE_IS_ERRORS = True
                          
                    PD_OBJECT_NAME = OBJECT_NAME
            
            if special_case == False:
                OBJECT_ARGS = box['box']['text'].split(' ')[1:]
                OBJECT_ARGS = ' '.join(OBJECT_ARGS)
                VALUE = '#X obj ' + x_y_position + ' ' + PD_OBJECT_NAME + ' ' + OBJECT_ARGS + ' ;'
                PATCH.append(VALUE)

        elif box['box']['maxclass'] == 'slider': # Sliders
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + " " + str(x_y_position[1])
            tamanho = 15
            VALUE = '#X obj ' + x_y_position + ' ' + 'hsl 128 ' + str(tamanho) + ' 0 127 0 0 empty empty empty -2 -8 0 10 -262144 -1 -1 0 1;'
            PATCH.append(VALUE)
        
        elif box['box']['maxclass'] == 'multislider': # Multislider
            MINMAX = box['box']['setminmax']
            
            ## SUBPATCH
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + " " + str(x_y_position[1])
            multislider_patch = []
            PD2MAX_multislider_NAME = 'PD2MAX_multislider_' +  str(MULTISLIDER_INDEX)
            ## START SUBPATCH
            multislider_patch.append('#N canvas 606 43 1226 621 10;')
            multislider_patch.append('#X obj 369 76 f \$1;')
            multislider_patch.append('#X obj 369 31 loadbang;')
            multislider_patch.append('#X obj 414 76 f \$2;')
            multislider_patch.append('#X obj 369 52 t b b, f 8;')
            multislider_patch.append('#N canvas 0 50 450 250 (subpatch) 0;')
            multislider_patch.append(f'#X array {PD2MAX_multislider_NAME} 100 float 3;')
            multislider_patch.append('#A 0 0 1 2 3 4 5 6 7 8 9 10 9 8 7 5 4 2 0 -1 -3 -4 -6 -8 -9 -11 -12 -13 -15 -16 -17 -18 -19 -20 -102 -103 -104 -105 -106 -105 -104 -101 -95 -92 -88 -86 -82 -79 -76 -73 -70 -67 -65 -62 -59 -58 -55 -53 -52 -50 -48 -46 -44 -43 -41 -40 -38 -36 -35 -34 -33 -32 -31 -29 -28 -27 -26 -25 -24 -23 -22 -21 -20 -19 -18 -17 -16 -15 -14 -13 -12 -11 -10 -9 -8 -6 -5 -4 -3 -2 0;')
            multislider_patch.append('#X coords 0 1 100 0 200 140 1 100 100;')
            multislider_patch.append('#X restore 2 1 graph;')
            multislider_patch.append('#X obj 340 104 else/rescale 0 1 0 1;')
            multislider_patch.append('#X obj 340 132 t f b;')
            multislider_patch.append('#X obj 367 154 int 1;')
            multislider_patch.append('#X obj 367 183 + 1, f 6;')
            multislider_patch.append('#X obj 367 209 mod 100;')
            multislider_patch.append('#X obj 367 230 + 1;')
            multislider_patch.append(f'#X obj 280 259 tabwrite {PD2MAX_multislider_NAME};')
            multislider_patch.append('#X obj 333 76 inlet;')
            multislider_patch.append('#X connect 0 0 5 1;')
            multislider_patch.append('#X connect 1 0 3 0;')
            multislider_patch.append('#X connect 2 0 5 2;')
            multislider_patch.append('#X connect 3 0 0 0;')
            multislider_patch.append('#X connect 3 1 2 0;')
            multislider_patch.append('#X connect 5 0 6 0;')
            multislider_patch.append('#X connect 6 0 11 0;')
            multislider_patch.append('#X connect 6 1 7 0;')
            multislider_patch.append('#X connect 7 0 8 0;')
            multislider_patch.append('#X connect 8 0 9 0;')
            multislider_patch.append('#X connect 8 0 7 1;')
            multislider_patch.append('#X connect 9 0 10 0;')
            multislider_patch.append('#X connect 10 0 11 1;')
            multislider_patch.append('#X connect 12 0 5 0;')
            multislider_patch.append('#X coords 0 0 1 1 200 140 1 2 1;')
            ## END SUBPATCH

            multislider_patch_NAME =  f'multislider_{MULTISLIDER_INDEX}.pd'
            multislider_patch_FILE = MAIN_FOLDER + '/' + multislider_patch_NAME 
            MULTISLIDER_INDEX = MULTISLIDER_INDEX + 1
            multislider_patch_NAME.replace('.pd', ' ')
            message = f'  Multislider abstraction saved in: {multislider_patch_NAME}'
            print_in_thinker(message, 'green', TK_GUI)

            with open(multislider_patch_FILE, "w") as f:
                for item in multislider_patch:
                    f.write(item + "\n")
                f.close()
            multislider_patch_NAME = multislider_patch_NAME.replace('.pd', '')
            VALUE = '#X obj ' + x_y_position + ' ' + multislider_patch_NAME + ' ' + str(MINMAX[0]) + ' ' + str(MINMAX[1]) + ' ;', 
            PATCH.append(VALUE[0])

        # numbers
        elif box['box']['maxclass'] == 'number' or box['box']['maxclass'] == 'flonum':
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + " " + str(x_y_position[1])
            tamanho = 5
            #X obj 175 114 nbx 5 14 -1e+037 1e+037 0 0 empty empty empty 0 -8 0
            VALUE = '#X obj ' + x_y_position + ' nbx ' + str(tamanho) + "14 -1e+037 1e+037 0 0 empty empty empty 0 -8 0 ;"
            PATCH.append(VALUE)


        elif box['box']['maxclass'] == 'number~':
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + " " + str(x_y_position[1])
            OBJECT_NAME = 'cyclone/number~'
            VALUE = '#X obj ' + x_y_position + ' ' + OBJECT_NAME + ' ' + ' ;'

        # =====================================================
        elif box['box']['maxclass'] == 'button': # Bang 
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + ' ' + str(x_y_position[1])
            tamanho = 15 ## GET THE SIZE OF THE BANG
            VALUE = '#X obj ' + x_y_position + f' bng {tamanho}  250 50 0' + ' empty empty empty 17 7 0 10 -262144' + ' ;'
            PATCH.append(VALUE)
            
        # =====================================================

        elif box['box']['maxclass'] == 'toggle': # Toggle
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + ' ' + str(x_y_position[1])
            tamanho = 15 ## GET THE SIZE OF THE TOGGLE TODO
            VALUE = '#X obj ' + x_y_position + f' tgl {tamanho}  250 50 0' + ' empty empty empty 17 7 0 10 -262144' + ' ;'
            PATCH.append(VALUE)


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
            NEED_IMPLEMENTED = box["box"]["maxclass"]
            print_in_thinker(f'NEED TO BE IMPLEMENTEND: {NEED_IMPLEMENTED}', 'red', TK_GUI)
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + " " + str(x_y_position[1])
            VALUE = "#X " + "obj" + " " + x_y_position + " " + "NEED_TO_BE_IMPLEMENTED!" + " ;"
            PATCH.append(VALUE)
        
        
        # UPDATE THE GUI
        
        
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
    
    print_in_thinker('Patch created!', 'green', TK_GUI)
    return PATCH

## read 
