from genericpath import isdir
from operator import is_
import os
from pathlib import Path
from turtle import bgcolor, onclick
from PIL import Image, ImageTk
import os, string
import tkinter as tk
from tkinter import CENTER, Button, Label, Tk, ttk
from ctypes import windll

DPI_aware = True
if DPI_aware:   
    windll.shcore.SetProcessDpiAwareness(1)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        w_wind = 800 
        h_wind = 650
        max_w = 1000
        max_h = 800
        if not DPI_aware:
            w_wind/=1.5
            h_wind/=1.5
            max_w/=1.5
            max_h/=1.5
        w_scr = self.winfo_screenwidth()
        print(f"w_scr: {w_scr}")
        h_scr = self.winfo_screenheight()
        print(f"h_scr: {h_scr}")
        x = (w_scr/2) - (w_wind/2)
        y = (h_scr/2) - (h_wind/2)
        #self.maxsize(max_w, max_h)
        self.geometry('%dx%d+%d+%d' % (w_wind, h_wind, x, y))
        self.title("File Manager")

class FolderButton:
    img_size = [60,60]
    icon_path = "icons/icons8-folder-480.png"
    def __init__(self, master=None, path="", button=None):
        if not DPI_aware:
            self.img_size=[round(x / 1.5) for x in self.img_size]
        img = (Image.open(self.icon_path))
        resized_image= img.resize(tuple(self.img_size))
        self.image_bg= ImageTk.PhotoImage(resized_image)

        self.button = button
        self.button.configure(image = self.image_bg, command = self.clicked)

        self.name = Path(path).name
        self.abs_path = os.path.abspath(path)
        self.parent = master
        

    def clicked(self):
        print("Folder clicked")
        print(f"Folder Path: {self.abs_path}")
        print(f"Folder Name: {self.name}\n")
        update_content(self.parent, self.abs_path)

class FileButton(FolderButton):
    def __init__(self, master, path, button):
        self.icon_path = "icons/icons8-blank-file-100.png"
        self.extension = Path(path).suffix
        super().__init__(master, path, button)

    def clicked(self):
        print("File clicked")
        print(f"File Name: {self.name}")
        print(f"File Extension: {self.extension}\n")

class ParFolderButton(FolderButton):
    def __init__(self, master, path, button):
        self.icon_path="icons/icons8-parent-folder-480.png"
        super().__init__(master, path, button)
        self.abs_path = path

    def clicked(self):
        print("Parent Folder clicked")
        print(f"Path of parent folder: {self.abs_path}\n")
        update_content(self.parent, self.abs_path)

def fill_content(parent, path):
    print(f'Current path is "{path}"')
    padding_lr = [10,10]
    padding_ud = [5,0]
    font_size = 12
    l_font = "Courier New"
    if not DPI_aware:
            padding_lr=[x / 1.5 for x in padding_lr]
            padding_ud=[x / 1.5 for x in padding_ud]
    available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    current_folders = {}
    current_files = {}
    if path == "":
        print(f"List of drives available: {available_drives}\n")
        for row, drive in enumerate(available_drives):
            button = ttk.Button(parent)
            button.grid(row = row, column = 0, padx = tuple(padding_lr), pady = tuple(padding_ud))
            current_folders[f"folder{row}"] = FolderButton(parent, drive+'\\', button)
            label = ttk.Label(parent, text = drive, font = (l_font, font_size))
            label.grid(row = row, column=1, sticky='w')
    else:
        par_butt = ttk.Button(parent)
        par_butt.grid(row=0, column=0, padx = tuple(padding_lr), pady = tuple(padding_ud))
        par_path = str(Path(path).parent)
        if par_path == path:
            par_path = ""
        current_folders["parent_folder"] = ParFolderButton(parent, par_path, par_butt)
        ttk.Label(parent, text='...', font = (l_font, font_size)).grid(row=0, column=1,\
                                                             sticky='w', padx=(padding_lr[0], 0))

        dir_list = [x for x in Path(path).iterdir() if not x.name.startswith(".")]
        print("Content of the folder:")
        row = 0
        for instance in dir_list:
            print(instance)
            if instance.is_dir():
                button = ttk.Button(parent)
                button.grid(row = row+1, column = 0, padx = tuple(padding_lr), pady = tuple(padding_ud))
                current_folders[f"folder{row+1}"] = FolderButton(parent, str(instance), button)
                label = ttk.Label(parent, text = instance.name, font = (l_font, font_size))
                label.grid(row=row+1, column = 1, sticky = 'w', padx=(padding_lr[0], 0))
                row+=1
            
        for instance in dir_list:
            print(instance)
            if instance.is_file():
                button = ttk.Button(parent)
                button.grid(row = row+1, column = 0, padx = tuple(padding_lr), pady = tuple(padding_ud))
                current_files[f"file{row+1}"] = FileButton(parent, str(instance), button)
                label = ttk.Label(parent, text = instance.name, font = (l_font, font_size))
                label.grid(row=row+1, column = 1, sticky = 'w', padx=(padding_lr[0], 0))
                row+=1
        print("")


    return [available_drives, current_folders, current_files]

def update_content(parent, path):
    for widget in parent.winfo_children():
        widget.destroy()
    grandparent_name = parent.winfo_parent()
    grandparent = parent._nametowidget(grandparent_name)
    grandparent.yview_moveto(0.0)
    _, folders, files = fill_content(parent, path)

def get_app_icon(path):
    png = Image.open(path)
    ico = ImageTk.PhotoImage(png)
    return ico

if __name__ == '__main__':
    global drives, folders, files
    app_iconpath = 'icons/icons8-app-icon-240.png' 
    start_path = ""
    fm_app = App()
    fm_app.wm_iconphoto(False, get_app_icon(app_iconpath))

    frame_main = ttk.Frame(fm_app)
    frame_main.pack(fill=tk.BOTH, expand=1)

    # Create a frame for the canvas with non-zero row&column weights
    canvas = tk.Canvas(frame_main)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # Link a scrollbar to the canvas
    def custom_yview(*args):
        if canvas.yview() == (0.0, 1.0):
            return
        canvas.yview(*args)
    scroll_bar = ttk.Scrollbar(frame_main, orient="vertical", command=custom_yview)
    scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scroll_bar.set)
    #canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox("all")))

    working_screen = ttk.Frame(canvas)
    canvas_frame = canvas.create_window((0, 0), window=working_screen, anchor='nw')

    def FrameWidth(event):
        canvas.itemconfig(canvas_frame, width=event.width)

    def OnFrameConfigure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def OnMousewheel(event):
        if canvas.yview() == (0.0, 1.0):
            return
        canvas.yview_scroll(round(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", OnMousewheel)
    working_screen.bind("<Configure>", OnFrameConfigure)
    canvas.bind('<Configure>', FrameWidth)

    drives, folders, files = fill_content(working_screen, start_path)

    fm_app.mainloop()
