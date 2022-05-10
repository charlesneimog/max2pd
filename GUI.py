from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os
import sys
from max2pd import * 

config_name = 'resources'
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
config_path = os.path.join(application_path, config_name)
script_path = config_path

# for Windows 
if os.name == 'nt':
    ICO_PATCH = f'{script_path}\\opensource.ico'
## for Linux Ubuntu
if os.name == 'posix':
    ICO_PATCH = f'{script_path}/opensource.ico'
## for Mac
if os.name == 'posix':
    ICO_PATCH = f'{script_path}/opensource.icns'

# ================================================== Acabou de criar a interface ==================================================
def exit_call():
    res = messagebox.askquestion('Convert new Patch', 'You want to convert a new Patch?')
    if res == 'no' :
        root.destroy()
    else :
        patch_chooser_dialog()


def patch_chooser_dialog():
    global FILE
    patch_chooser = Tk()
    if os.path.exists(ICO_PATCH):
        root.iconbitmap(ICO_PATCH)
    else:
        print('Icon not found')

    patch_chooser.title('Max2PD')
    patch_chooser.geometry("480x400+715+200")
    patch_chooser.withdraw()
    FILE = filedialog.askopenfilename(filetypes=[("Max patch files", "*.maxpat")])
    if FILE == '':
        print_in_thinker(f'No file selected.', 'red', root)
        print_in_thinker(f'Exiting...', 'red', root)
        time.sleep(0.2)
        root.destroy()
        sys.exit()
    else:
        name_of_file = os.path.basename(FILE)
        name_of_file.replace('.maxpat', '')
        message = f'File selected: {name_of_file}'
        print_in_thinker(message, 'blue', root)

    patch_chooser.destroy()
    convert2pd(FILE, root)
    if THERE_IS_ERRORS:
        with open('objects_not_found.txt') as f:
            lines = f.readlines()
        lines = [line.rstrip('\n') for line in lines]
        seen = set()
        result = []
        for item in lines:
            if item not in seen:
                seen.add(item)
                result.append(item)

        try:
            os.remove('objects_not_found.txt')
        except:
            pass

        if result != []:
            with open('PLEASE_REPORT_missing_objects.txt', 'w') as f:
                for line in result:
                    f.write(line + '\n')
        
    exit_call()

def on_closing():
    root.destroy()
    sys.exit()

def close_window(): 
    destroy()

## Create Main Window ==================================================
global root
root = Tk()
if os.path.exists(ICO_PATCH):
    root.iconbitmap(f'{script_path}\\opensource.ico')
else:
    print('Icon not found')


root.title('Max2PD')
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_height = 150
window_width = 430
x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))

root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

root.bind('<Return>', lambda event=None: answer_button.invoke())
root.bind('<Escape>', lambda event=None: finish_button.invoke())

# Create Buttons
button_frame = Frame(root)
button_frame.pack(pady=20)
answer_button = Button(button_frame, text="Choose Max-Patch", command=patch_chooser_dialog)
answer_button.grid(row=0, column=0, padx=20)


root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()