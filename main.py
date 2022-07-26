from genericpath import isdir
from operator import is_
import os
from pathlib import Path
from turtle import onclick
from PIL import Image, ImageTk
import os, string
import tkinter as tk
from tkinter import Button, Label, Tk, ttk
from ctypes import windll

DPI_aware = True
if DPI_aware:   
    windll.shcore.SetProcessDpiAwareness(1)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        w_wind = 800 
        h_wind = 650
        if not DPI_aware:
            w_wind/=1.5
            h_wind/=1.5
        w_scr = self.winfo_screenwidth()
        print(f"w_scr: {w_scr}")
        h_scr = self.winfo_screenheight()
        print(f"h_scr: {h_scr}")
        x = (w_scr/2) - (w_wind/2)
        y = (h_scr/2) - (h_wind/2)
        self.geometry('%dx%d+%d+%d' % (w_wind, h_wind, x, y))
        self.title("File Manager")

class FolderButton:
    padding_lr = [20,20]
    padding_ud = [5,0]
    img_size = [30,30]
    icon_path = "icons/icons8-folder-480.png"
    def __init__(self, master=None, path="", button=None):
        if not DPI_aware:
            self.padding_lr=[x / 1.5 for x in self.padding_lr]
            self.padding_ud=[x / 1.5 for x in self.padding_ud]
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
        print(self.abs_path)
        print(self.name)
        update_content(self.parent, self.abs_path)

class FileButton(FolderButton):
    def __init__(self, master, path, button):
        self.icon_path = "icons/icons8-blank-file-100.png"
        self.extension = Path(path).suffix
        super().__init__(master, path, button)

    def clicked(self):
        print("File clicked")
        print(self.name)

class ParFolderButton(FolderButton):
    def __init__(self, master, path, button):
        self.icon_path="icons/icons8-parent-folder-480.png"
        super().__init__(master, path, button)
        self.abs_path = path

    def clicked(self):
        print("Parent Folder clicked")
        update_content(self.parent, self.abs_path)

def fill_content(parent, path):
    print(path)
    available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    current_folders = {}
    current_files = {}
    if path == "":
        print(available_drives)
        for row, drive in enumerate(available_drives):
            print(drive)
            button = ttk.Button(parent)
            button.grid(row = row, column = 0)
            current_folders[f"folder{row}"] = FolderButton(parent, drive+'\\', button)
            label = ttk.Label(parent, text = drive)
            label.grid(row = row, column=1, sticky='w')
    else:
        par_butt = ttk.Button(parent)
        par_butt.grid(row=0, column=0)
        par_path = str(Path(path).parent)
        if par_path == path:
            par_path = ""
        current_folders["parent_folder"] = ParFolderButton(parent, par_path, par_butt)
        ttk.Label(parent, text='...').grid(row=0, column=1, sticky='w')
        dir_list = Path(path).iterdir()
        for row, instance in enumerate(dir_list):
            print(instance)
            if instance.is_dir():
                button = ttk.Button(parent)
                button.grid(row = row+1, column = 0)
                current_folders[f"folder{row}"] = FolderButton(parent, str(instance), button)
            else:
                button = ttk.Button(parent)
                button.grid(row = row+1, column = 0)
                current_files[f"file{row}"] = FileButton(parent, str(instance), button)
            label = ttk.Label(parent, text = instance.name)
            label.grid(row=row+1, column = 1, sticky='w')


    return [available_drives, current_folders, current_files]

def update_content(parent, path):
    current_folders = {}
    current_files = {}
    for widget in parent.winfo_children():
        widget.destroy()
    fill_content(parent, path)
    return [current_folders, current_files]

if __name__ == '__main__':

    start_path = ""
    myapp = App()
    ico = Image.open('icons/icons8-app-icon-240.png')
    photo = ImageTk.PhotoImage(ico)
    myapp.wm_iconphoto(False, photo)
    myapp.grid_rowconfigure(0, weight=1)
    myapp.grid_columnconfigure(0, weight=1)

    frame_main = ttk.Frame(myapp)
    frame_main.pack(fill=tk.BOTH, expand=1)

    # Create a frame for the canvas with non-zero row&column weights
    canvas = tk.Canvas(frame_main)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # Link a scrollbar to the canvas
    scroll_bar = ttk.Scrollbar(frame_main, orient="vertical", command=canvas.yview)
    scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scroll_bar.set)
    #canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox("all")))

    working_screen = ttk.Frame(canvas)
    canvas_frame = canvas.create_window((0, 0), window=working_screen, anchor='nw')

    def FrameWidth(event):
        canvas.itemconfig(canvas_frame, width=event.width)

    def OnFrameConfigure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    working_screen.bind("<Configure>", OnFrameConfigure)
    canvas.bind('<Configure>', FrameWidth)

    fill_content(working_screen, start_path)

    myapp.mainloop()
