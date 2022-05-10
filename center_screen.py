import tkinter as tk

win = tk.Tk()  # Creating instance of Tk class
win.title("Centering windows")
win.resizable(False, False)  # This code helps to disable windows from resizing

window_height = 480
window_width = 200

screen_width = win.winfo_screenwidth()
screen_height = win.winfo_screenheight()

x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))

win.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

win.mainloop()