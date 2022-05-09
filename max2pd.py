import json
 
# opening the file

with open("max2pd.json") as json_file:
    max2pd_objects = json.load(json_file)

# Opening JSON file
PATCH = []
INDEX = 0

with open("max2pd.maxpat") as json_file:
    data = json.load(json_file)
    

def max2pd_objects(json_data):
    key = 'patcher'
    patcher = json_data[key]
    canvas = json_data[key]['rect']
    canvas_string = ''
    for i in canvas: 
        canvas_string += str(i) + ' '
    canvas_string = '#N canvas ' + canvas_string + ' ' + '10' + ';'
    PATCH.append(canvas_string)
    boxes = patcher['boxes']
    lines = patcher['lines']
    for box in boxes:
        get_box_id = str(box['box']['id'])
        get_box_id = get_box_id.split('obj-')[1]
        
        if box['box']['maxclass'] == 'newobj': # Objetos
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + " " + str(x_y_position[1])
            OBJECT_NAME = box['box']['text']
            OBJECT_NAME = OBJECT_NAME.split(' ')[0]
            try:
                PD_OBJECT_NAME = max2pd_objects['max2pd'][OBJECT_NAME]
            except:
                try:
                    PD_OBJECT_NAME = max2pd_objects['pdobjects'][OBJECT_NAME]
                except:
                    if OBJECT_NAME == 'p':
                        print('Subpatch')
                        max2pd_objects(box['box']) # Aqui vai a recursão
                            
                    else:
                        print('Object not found: ' + OBJECT_NAME)
                        print(box['box']['maxclass'])


                    PD_OBJECT_NAME = OBJECT_NAME
                
            OBJECT_ARGS = box['box']['text'].split(' ')[1:]
            OBJECT_ARGS = ' '.join(OBJECT_ARGS)

            
            VALUE = '#X obj ' + x_y_position + ' ' + PD_OBJECT_NAME + ' ' + OBJECT_ARGS + ' ;'
            PATCH.append(VALUE)


        elif box['box']['maxclass'] == 'slider': # Sliders
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + str(x_y_position[1])
        

        elif box['box']['maxclass'] == 'button': # Bang e Toggles
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + str(x_y_position[1])


        elif box['box']['maxclass'] == 'message': # Mensagens
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + " " + str(x_y_position[1])
            try:
                message_text = box['box']['text']
            except:
                message_text = ' '
            
            VALUE = "#X msg" + " " + x_y_position + " " + message_text + " ;" # E o ID???
            PATCH.append(VALUE)

        else: 
            x_y_position = box['box']['patching_rect'][:2]
            x_y_position = str(x_y_position[0]) + str(x_y_position[1])
            print('NEED TO BE IMPLEMENTEND: ', box['box']['maxclass'])
            x_y_position = box['box']['patching_rect'][:2]
            print('-----------------------------------------------------')


    for line in lines:
        destination = line['patchline']['destination']
        source = line['patchline']['source']
    

    return PATCH


PATCH = max2pd_objects(data)


for item in PATCH:
    print(item)


# Writing to file
# with open("Max2PD.pd", "w") as f:
#     for item in PATCH:
#         f.write(item + "\n")
# f.close()