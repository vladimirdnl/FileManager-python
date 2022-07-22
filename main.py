from turtle import onclick
from PIL import Image, ImageTk
import os, string
import tkinter as tk
from tkinter import Button, Tk, ttk
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        w_wind = 800 
        h_wind = 650
        w_scr = self.winfo_screenwidth()
        h_scr = self.winfo_screenheight()
        x = (w_scr/2) - (w_wind/2)
        y = (h_scr/2) - (h_wind/2)
        self.geometry('%dx%d+%d+%d' % (w_wind, h_wind, x, y))
        self.title("FileManager")

class Folder(ttk.Frame):
    def __init__(self, master, name):
        super().__init__(master=None)
        self.name = name
        self.grid()
        img = (Image.open("icons/icons8-folder-480.png"))
        resized_image= img.resize((30,30))
        self.image_bg= ImageTk.PhotoImage(resized_image)
        self.btn = ttk.Button(self, image = self.image_bg, command=self.clicked)
        self.btn.grid(column=0,row=0)
        self.label = ttk.Label(self, text=self.name)
        self.label.grid(column = 1, row = 0)

    def clicked(self):
        print("Button clicked")


class StartScreen(ttk.Frame):
    folders={}
    def __init__(self, master):
        super().__init__(master=None)
        self.grid()
        '''self.lbl = ttk.Label(self, text="Hello World!")
        self.lbl.grid(column=0, row=0)
        self.btn = ttk.Button(self, text="Quit", command=master.destroy)
        self.btn.grid(column=0, row=1)'''
        self["padding"] = 10
        self.available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
        print(self.available_drives)
        
        for drive in self.available_drives:
            self.add_folder(drive)

    def add_folder(self, name):
        cols = 0
        rows = self.master.grid_size()[1]
        self.folders[f"folder{rows+1}"] = Folder(self, name)
        self.folders[f"folder{rows+1}"].grid(column = cols, row = rows+1)
        


if __name__ == '__main__':
    myapp = App()
    start_page = StartScreen(myapp)
    myapp.mainloop()
