from operator import iconcat
from struct import pack
import tkinter as tk
from tkinter import ttk
import os
import string
from PIL import Image, ImageTk
from pathlib import Path

#DPI aware setting
DPI_aware = True

class RenamePopup(tk.Toplevel):
    icon_path = 'icons/icons8-app-icon-240.png'
    new_name = ""
    is_correct=False
    def __init__(self, master=None, old_name="",  type="folder"):
        super().__init__(master)
        self.parent = master
        self.type = type
        self.old_name = old_name
        png = Image.open(self.icon_path)
        self.icon = ImageTk.PhotoImage(png)
        self.grab_set()
        self.title("Rename")
        self.tk.call('wm', 'iconphoto', self._w, self.icon)
        w_popup = 400
        h_popup = 150
        #set padding on x axis
        padding_lr = [10,10]
        #set paddin on y axis
        padding_ud = [5,0]
        if not DPI_aware:
            w_popup /= 1.5
            h_popup /= 1.5
            padding_lr = [x / 1.5 for x in padding_lr]
            padding_ud = [x / 1.5 for x in padding_ud]
        w_scr = self.winfo_screenwidth()
        h_scr = self.winfo_screenheight()
        x = (w_scr/2) - (w_popup/2)
        y = (h_scr/2) - (h_popup/2)
        self.geometry("%dx%d+%d+%d" % (w_popup, h_popup, x, y))
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.label = ttk.Label(self, text = "Enter a New Name:")
        self.label.grid(column=0, row=0, columnspan=2, sticky='ew',\
             padx=tuple(padding_lr), pady=tuple(padding_ud))
        self.entry = ttk.Entry(self)
        self.entry.grid(column=0, row=1, columnspan=2, sticky = 'ew', \
            padx=tuple(padding_lr), pady= tuple(padding_ud))
        self.error_msg = ttk.Label(self, text= "", foreground="red")
        self.error_msg.grid(column=0, row =2, columnspan=2)
        self.button_ok = ttk.Button(self, text="OK", command=self.check)
        self.button_ok.grid(column=0,row=3, sticky = 'ew', \
            padx=(padding_lr[0], 0), pady=tuple(padding_ud))
        self.button_cancel = ttk.Button(self, text="Cancel", command=self.destroy)
        self.button_cancel.grid(column=1,row=3, sticky = 'ew', \
            padx=(0, padding_lr[1]), pady=tuple(padding_ud))

    def check(self):
        self.is_correct = True
        if self.type == "folder":
            unallowed_s = '/\:;"<>|*'
        name = self.entry.get()
        for s in name:
            if s in unallowed_s:
                self.is_correct = False
                break

        if not self.is_correct:
            self.error_msg.config(text = "Not a valid name!")
        else: 
            self.new_name = name
            os.rename(self.old_name, str(Path(self.old_name).parent)+ "\\" + self.new_name)
            self.destroy()
            update_content(self.parent, str(Path(self.old_name).parent), stay=True)

#class for button for folders
class FolderButton:
    #inside it, let it be the img size
    img_size = [60,60]
    #and the icon path for the folder button
    icon_path = "icons/icons8-folder-480.png"

    #initialize function, passing master, path and button
    def __init__(self, master=None, path="", button=None):
        #if dpi awareness isn't turned on
        if not DPI_aware:
            #rescale image size
            self.img_size=[round(x / 1.5) for x in self.img_size]
        
        #open image, resize image, and return image background for the button
        img = (Image.open(self.icon_path))
        resized_image= img.resize(tuple(self.img_size))
        self.image_bg= ImageTk.PhotoImage(resized_image)
        #create a variable button inside a class, assigned to a button
        self.button = button
        #set background image and command for the button
        self.button.configure(image = self.image_bg, command = self.clicked)

        #create a name variable, which resembles folder name
        self.name = Path(path).name
        #create an absolute path variable, which resembles the absolute path of the folder
        self.abs_path = os.path.abspath(path)
        #create parent variable and assign it to master
        self.parent = master
        #go to method initialise_popup
        self.initialise_popup()

    def initialise_popup(self):
        self.popup = tk.Menu(self.button, tearoff=False)
        self.popup.add_command(label = "Open Folder", command=self.open)
        if self.abs_path.split('\\')[1] != "":
            self.popup.add_command(label = "Rename Folder", command = self.rename)
            self.popup.add_separator()
            self.popup.add_command(label = "Paste to Folder")
            self.popup.add_command(label = "Copy Folder")
            self.popup.add_command(label = "Cut Folder")
        self.button.bind("<Button-3>", self.instance_popup)
    
    def instance_popup(self, event):
        self.popup.tk_popup(event.x_root, event.y_root)

    def open(self):
        print("Folder opened")
        update_content(self.parent, self.abs_path)

    def rename(self):
        global rename_pop
        rename_pop = RenamePopup(self.parent, self.abs_path)


        
    #function if folder button is clicked
    def clicked(self):
        #print for console:
        print("Folder clicked")
        print(f"Folder Path: {self.abs_path}")
        print(f"Folder Name: {self.name}\n")
        #update the content of the parent frame with the self path
        update_content(self.parent, self.abs_path)

#class for the file button, which is a child to folderbutton
class FileButton(FolderButton):
    #initialization function
    def __init__(self, master, path, button):
        #change icon path
        self.icon_path = "icons/icons8-blank-file-100.png"
        #add new variable which has the extension of the file
        self.extension = Path(path).suffix
        #call the parent class init method
        super().__init__(master, path, button)

    def initialise_popup(self):
        if self.abs_path.split('\\')[1] != "":
            self.popup = tk.Menu(self.button, tearoff=False)
            self.popup.add_command(label = "Open File", command=self.open)
            self.popup.add_command(label = "Rename File")
            self.popup.add_separator()
            self.popup.add_command(label = "Copy File")
            self.popup.add_command(label = "Cut File")
            self.button.bind("<Button-3>", self.instance_popup)
    
    def instance_popup(self, event):
        self.popup.tk_popup(event.x_root, event.y_root)
    
    def open(self):
        print("File opened")
        os.startfile(self.abs_path)

    #rewrite the function clicked
    def clicked(self):
        #print in console
        print("File clicked")
        print(f"File Name: {self.name}")
        print(f"File Extension: {self.extension}\n")

#class for the parent folder button, which is a child to folderbutton
class ParFolderButton(FolderButton):
    #initialization function
    def __init__(self, master, path, button):
        #set another icon path
        self.icon_path="icons/icons8-parent-folder-480.png"
        #call the init parent method
        super().__init__(master, path, button)
        #rewrite absolute path to path
        self.abs_path = path

    def initialise_popup(self):
        self.popup = tk.Menu(self.button, tearoff=False)
        self.popup.add_command(label = "Open Folder", command=self.open)
        self.button.bind("<Button-3>", self.instance_popup)
    
    def instance_popup(self, event):
        self.popup.tk_popup(event.x_root, event.y_root)

    #rewrite the function clicked
    def clicked(self):
        #print in console
        print("Parent Folder clicked")
        print(f"Path of parent folder: {self.abs_path}\n")
        #update the content of the parent with the self path
        update_content(self.parent, self.abs_path)

#filling content inside forking frame with folders and files
def fill_content(parent, path):
    #print current path in the console
    print(f'Current path is "{path}"')
    #set padding on x axis
    padding_lr = [10,10]
    #set paddin on y axis
    padding_ud = [5,0]
    #sent font size
    font_size = 12
    #set font family
    l_font = "Courier New"
    #if the program does not have DPI aware turned on,
    # scale the absolute values of padding
    if not DPI_aware:
            padding_lr=[x / 1.5 for x in padding_lr]
            padding_ud=[x / 1.5 for x in padding_ud]
    #get available drives
    available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    #initialize current folders and files dicts
    current_folders = {}
    current_files = {}
    #if path is empty (i.o.w. root path), display all the available disks
    if path == "":
        #print the list of drives to the console
        print(f"List of drives available: {available_drives}\n")
        #enumerate available drive, and for every row/drive combination
        for row, drive in enumerate(available_drives):
            #create a button inside the frame
            button = ttk.Button(parent)
            #place it using row from enumeration, and in column 0, also assign padding
            button.grid(row = row, column = 0, padx = tuple(padding_lr), pady = tuple(padding_ud))
            #add the button to current folders dictionary, for it to be available and
            # customized by the class FolderButton
            current_folders[f"folder{row}"] = FolderButton(parent, drive+'\\', button)
            #create a label with a drive name, assing font and its size
            label = ttk.Label(parent, text = drive, font = (l_font, font_size))
            #place it in the same row, in the column 1, and make it sticky to the left
            # and assign padding
            label.grid(row = row, column=1, sticky='w', padx=(padding_lr[0], 0))
    
    #if the path isn't empty, meaning there're not only drives
    else:
        #create a parrent button folder
        par_butt = ttk.Button(parent)
        #place it in the top left corner
        par_butt.grid(row=0, column=0, padx = tuple(padding_lr), pady = tuple(padding_ud))
        #get parent path
        par_path = str(Path(path).parent)
        #! if parent path is the same as path, then the parent path is ""
        if par_path == path:
            par_path = ""
        #add parent folder to the current folders dict
        current_folders["parent_folder"] = ParFolderButton(parent, par_path, par_butt)
        #add the label and place it simultaneously to the right of the button
        ttk.Label(parent, text='...', font = (l_font, font_size)).grid(row=0, column=1,\
                                                             sticky='w', padx=(padding_lr[0], 0))

        #create a directories list in the path, skipping the hidden ones
        dir_list = [x for x in Path(path).iterdir() if not x.name.startswith(".")]
        #for console
        print("Content of the folder:")
        #assign that the row 0 already exists (parent folder)
        row = 0

        #*cycles to show folders first, then the files:
        #for instance in the directory list
        for instance in dir_list:
            #if it is a folder, then
            if instance.is_dir():
                #print to the console
                print(instance)
                #create a button in a frame
                button = ttk.Button(parent)
                #place it using row+1 and to the left(column=0), assign padding
                button.grid(row = row+1, column = 0, padx = tuple(padding_lr), pady = tuple(padding_ud))
                #add it to current folders to get the style and make it accessible
                current_folders[f"folder{row+1}"] = FolderButton(parent, str(instance), button)
                #after that create a lable with the name of instance, assign font and font size
                label = ttk.Label(parent, text = instance.name, font = (l_font, font_size))
                #place it to the right of the button, aligned to the left and padding assigned
                label.grid(row=row+1, column = 1, sticky = 'w', padx=(padding_lr[0], 0))
                #increase the row variable by 1
                row+=1
        
        #one more time, for every instance in dir_list
        for instance in dir_list:
            #if it is a file, then
            if instance.is_file():
                #print to the console
                print(instance)
                #create a button in a frame
                button = ttk.Button(parent)
                #place it using row+1 and to the left(column=0), assign padding
                button.grid(row = row+1, column = 0, padx = tuple(padding_lr), pady = tuple(padding_ud))
                #add it to current files to get the style and make it accessible
                current_files[f"file{row+1}"] = FileButton(parent, str(instance), button)
                #after that create a lable with the name of instance, assign font and font size
                label = ttk.Label(parent, text = instance.name, font = (l_font, font_size))
                #place it to the right of the button, aligned to the left and padding assigned
                label.grid(row=row+1, column = 1, sticky = 'w', padx=(padding_lr[0], 0))
                #increase the row variable by 1
                row+=1
        #for pretty console
        print("")
    #return the available drives and current folders and files instances
    return [available_drives, current_folders, current_files]

#function to update content of the working screen
def update_content(parent, path, stay = False):
    #for refreshing global variables
    global drives, folders, files
    #firstly, destroy all the widgets on the working screen
    for widget in parent.winfo_children():
        widget.destroy()
    
    #then, get the canvas and assure the scroll is on top
    # if stay isn't specified
    if not stay:
        grandparent_name = parent.winfo_parent()
        grandparent = parent._nametowidget(grandparent_name)
        grandparent.yview_moveto(0.0)

    #fill content with new path passed, refresh global variables
    drives, folders, files = fill_content(parent, path)

def create_file(parent, path):
    pass

def create_folder(parent, path):
    pass

def open_path(parent):
    pass