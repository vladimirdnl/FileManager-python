#importing libraries
import tkinter as tk
from tkinter import ttk, messagebox
import os
import string
from PIL import Image, ImageTk
from pathlib import Path
import shutil
from distutils.dir_util import copy_tree

#DPI aware setting variable
DPI_aware = False

#*global variables:
#drives - available list of drives
#folders - current list of folder instances
#files - current list of file instances
#curr_path - current path 
#copy_buff - address of file to cut/copy
#cut - controls whether to cut file or not
global drives, folders, files, curr_path, copy_buff, cut
cut = False
curr_path = ""
copy_buff = ""

#create file\folder popup class
class createInstance(tk.Toplevel):
    #set standard path of the icon to "add folder" icon
    icon_path = 'icons/icons8-add-folder-80.png'
    #initialize new_name variable
    new_name = ""
    #initialize variable, which controls correctness of the name 
    is_correct=False
    #intialization function
    def __init__(self, master=None, type="folder", master_type="frame", frame=None):
        #call a parent class initialization function
        super().__init__(master)
        #make global curr_path into the class
        global curr_path
        #assign parent variable to master widget
        self.parent = master
        #assign parent type to master type + assign frame
        #? Why so -- in case the parent is canvas, the frame for update
        #? is still provided to the class, we don't have to iterate 
        #? through children
        self.parent_type = master_type
        self.frame=frame
        #set type variable to type
        self.type = type
        #if type of created instance is a file, correct the icon path of the popup
        if self.type == "file":
            self.icon_path = "icons/icons8-add-file-96.png"
        png = Image.open(self.icon_path)
        self.icon = ImageTk.PhotoImage(png)
        #set the icon
        self.tk.call('wm', 'iconphoto', self._w, self.icon)
        #make only popup accessible for a user
        self.grab_set()
        #create title according to the instance type
        if self.type == "folder":
            self.title("Create Folder")
        else:
            self.title("Create File")
        #assign width and height of the popup
        w_popup = 400
        h_popup = 150
        #set padding on x axis
        padding_lr = [10,10]
        #set paddin on y axis
        padding_ud = [5,0]
        #correct if scaling isn't enabled
        if not DPI_aware:
            w_popup /= 1.5
            h_popup /= 1.5
            padding_lr = [x / 1.5 for x in padding_lr]
            padding_ud = [x / 1.5 for x in padding_ud]
        #get window screen width and height
        w_scr = self.winfo_screenwidth()
        h_scr = self.winfo_screenheight()
        #get coordinates to place the popup in the center
        x = (w_scr/2) - (w_popup/2)
        y = (h_scr/2) - (h_popup/2)
        #place the popup in the center
        self.geometry("%dx%d+%d+%d" % (w_popup, h_popup, x, y))
        #make it unable to resize
        self.resizable(False, False)
        #set columnconfigure with weights to make the popup
        # grid fill the X axis of the popup 
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        #create a label widget with a call for the user to enter the name
        # of the instance, which is being created
        self.label = ttk.Label(self, text = "Enter the Name:")
        #place it in the top left corner with columnspan 2 + add padding
        self.label.grid(column=0, row=0, columnspan=2, sticky='ew',\
             padx=tuple(padding_lr), pady=tuple(padding_ud))
        #create an entry widget to make it possible for the user
        self.entry = ttk.Entry(self)
        #place it below the label, make it also take up the space of 2 columns
        self.entry.grid(column=0, row=1, columnspan=2, sticky = 'ew', \
            padx=tuple(padding_lr), pady= tuple(padding_ud))
        #create an empty error message label, make the text red
        self.error_msg = ttk.Label(self, text= "", foreground="red")
        #place it below the entry widget, make it centered
        self.error_msg.grid(column=0, row =2, columnspan=2)
        #create OK button, which checks the written name and proceeds
        self.button_ok = ttk.Button(self, text="OK", command= self.check)
        #place it to the left side, with 0 padding to the right
        self.button_ok.grid(column=0,row=3, sticky = 'ew', \
            padx=(padding_lr[0], 0), pady=tuple(padding_ud))
        #create Cancel button, which destroys the popup
        self.button_cancel = ttk.Button(self, text="Cancel", command=self.destroy)
        #place it to the right, beside the OK button, make the left padding 0
        self.button_cancel.grid(column=1,row=3, sticky = 'ew', \
            padx=(0, padding_lr[1]), pady=tuple(padding_ud))
        #create a list of directrories to access and prevent entering existing names
        dir_list = Path(curr_path).iterdir()
        self.dir_list = [str(x) for x in dir_list]

    #function to check instance name and create it
    def check(self):
        #make curr_path enter the function
        global curr_path
        #set is_correct to true ceforehand 
        self.is_correct = True
        #enter the array of unallowed symbols
        unallowed_s = '/\:;"<>|*'
        #get the instance name out of the entry
        name = self.entry.get()
        #check for unallowed symbols
        for s in name:
            if s in unallowed_s:
                #if there is one - set is_correct to false
                self.is_correct = False
                #and print the error message
                self.error_msg.config(text = "Don't use: / \ : ; \" < > | *")
                #break the cycle
                break
        #check for already existing instances with such name
        for ins_name in self.dir_list:
            #for every instance in the current folder check its type
            ins_is_dir = Path(ins_name).is_dir()
            #variable which is true when both (checked instance and created instance) are folders
            thesame_folder = self.type == "folder" and ins_is_dir
            #variable which is true when both (checked instance and created instance) are files
            thesame_file = self.type == "file" and not ins_is_dir
            #variable which is true when both the created instance and checked instance have the same type
            thesame = thesame_folder or thesame_file
            #if they share the same name and the same type
            if ins_name.endswith(name) and thesame:
                #set is_correct to false and print the correct message to the user
                self.is_correct = False
                if self.type == "folder":
                    self.error_msg.config(text = "Folder with such name already exists!")
                if self.type == "file":
                    self.error_msg.config(text = "File with such name already exists!")
                #break the cycle of checking
                break
        #lastly, if is_correct is stayed true, then create an instanse
        if self.is_correct:
            #assign new_name to what we got from the entry widget 
            self.new_name = name
            #create the instance according to its type
            if self.type == "folder":
                os.mkdir(curr_path + "\\" + self.new_name)
            elif self.type == "file":
                new_file = open(curr_path + '\\' + self.new_name, 'x')
                new_file.close()
            #destroy the popup
            self.destroy()
            #if the parent is canvas, pass the frame which was given to update
            if self.parent_type == "canvas":
                update_content(self.frame, curr_path, stay=True)
            #else -- just pass the parent widget (which means frame)
            else:
                update_content(self.parent, curr_path, stay=True)

#class which resembles popup on sub-menu command "Open > Open Path"
class goToPath(tk.Toplevel):
    #set the icon path
    icon_path = "icons/icons8-folder-480.png"
    #initialize the newpath variable
    new_path = ""

    #initialization function
    def __init__(self, master=None):
        #call the parent class initialization function 
        super().__init__(master)
        #make curr_path enter the function
        global curr_path
        #assign parent variable to master widget
        self.parent = master
        #set the image for a popup
        png = Image.open(self.icon_path)
        self.icon = ImageTk.PhotoImage(png)
        self.tk.call('wm', 'iconphoto', self._w, self.icon)
        #make only the popup accessible to the user
        self.grab_set()
        #write the title of the popup 
        self.title("Open Path")
        #initialize width and height of the popup
        w_popup = 450
        h_popup = 150
        #set padding on x axis
        padding_lr = [10,10]
        #set padding on y axis
        padding_ud = [5,0]
        #change values according to scaling 
        if not DPI_aware:
            w_popup /= 1.5
            h_popup /= 1.5
            padding_lr = [x / 1.5 for x in padding_lr]
            padding_ud = [x / 1.5 for x in padding_ud]
        #get scrren width and height
        w_scr = self.winfo_screenwidth()
        h_scr = self.winfo_screenheight()
        #get coordinates to place the popup in the center
        x = (w_scr/2) - (w_popup/2)
        y = (h_scr/2) - (h_popup/2)
        #place the popup
        self.geometry("%dx%d+%d+%d" % (w_popup, h_popup, x, y))
        #disable resizing
        self.resizable(False, False)
        #make grid columns as wide as the popup
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        #create a label widget with a call for the user to enter the name
        # of the instance, which is being created
        self.label = ttk.Label(self, text = "Enter the Path:")
        #place it in the top left corner with columnspan 2 + add padding
        self.label.grid(column=0, row=0, columnspan=2, sticky='ew',\
             padx=tuple(padding_lr), pady=tuple(padding_ud))
        #create an entry widget to make it possible for the user
        self.entry = ttk.Entry(self)
        #place it below the label, make it also take up the space of 2 columns
        self.entry.grid(column=0, row=1, columnspan=2, sticky = 'ew', \
            padx=tuple(padding_lr), pady= tuple(padding_ud))
        #create an empty error message label, make the text red
        self.error_msg = ttk.Label(self, text= "", foreground="red")
        #place it below the entry widget, make it centered
        self.error_msg.grid(column=0, row =2, columnspan=2)
        #create OK button, which checks the written name and proceeds
        self.button_ok = ttk.Button(self, text="OK", command= self.check)
        #place it to the left side, with 0 padding to the right
        self.button_ok.grid(column=0,row=3, sticky = 'ew', \
            padx=(padding_lr[0], 0), pady=tuple(padding_ud))
        #create Cancel button, which destroys the popup
        self.button_cancel = ttk.Button(self, text="Cancel", command=self.destroy)
        #place it to the right, beside the OK button, make the left padding 0
        self.button_cancel.grid(column=1,row=3, sticky = 'ew', \
            padx=(0, padding_lr[1]), pady=tuple(padding_ud))
    
    #to check the path
    def check(self):
        #make curr_path enter the function
        global curr_path
        #get a path from the entry widget
        path = str(Path(self.entry.get()))
        #if the path exists and it is not a file - update with the new path 
        if os.path.exists(path) and not Path(path).is_file():
            self.new_path = path
            update_content(self.parent, self.new_path)
        else:
            #else - pring that the path is invalid
            self.error_msg.config(text="Not a valid path!")

#class of the right click menu for current path
class rclickMenu(tk.Menu):
    #initialization function
    def __init__(self, master=None, master_type = "frame", frame=None):
        #call the parent class initialization function
        super().__init__(master, tearoff=False)
        #assign parent variable to master variable
        self.parent = master
        #assign parent_type to master type and set frame, if the master is canvas
        self.parent_type = master_type
        self.frame = frame
        #bind the parent to make menu visible on rclick
        self.parent.bind("<Button-3>", self.make_menu_visible)
        #add command create a File
        self.add_command(label = "Create a File", command=self.create_file)
        #add command create a Folder
        self.add_command(label = "Create a Folder", command=self.create_folder)
        #add the separator
        self.add_separator()
        #add command Paste here
        self.add_command(label = "Paste here", command=self.paste_here)

    #command to paste files
    def paste_here(self):
        #make the global variables into the function
        global copy_buff, curr_path, cut
        #if the copy buffer isn't empty
        if copy_buff != "":
            #and if the instance was COPIED
            if not cut:
                #if copied instance is a directory
                if Path(copy_buff).is_dir():
                    #try pasting (create a new folder with such name and paste the inners)
                    try:
                        os.mkdir(curr_path + '\\' + str(Path(copy_buff).name))
                        copy_tree(copy_buff, curr_path + '\\' + str(Path(copy_buff).name))
                        #reset copy buffer
                        copy_buff = ""
                    #if such folder exists - sent the messagebox that copying folder failed
                    except FileExistsError:
                        messagebox.showinfo(title="Copying Directory", message="The directory with such name exists")
                #if copied instance is not a directory, use shutil.copy2 to copy the file
                else:
                    shutil.copy2(copy_buff, curr_path)
                    #reset copy buffer
                    copy_buff = ""

            #if the instance was CUT
            else:
                #move the instance, reset cut variable and copy buffer
                shutil.move(copy_buff, curr_path)
                cut = False
                copy_buff=""
            #if the parent was a canvas -- pass the frame and update
            if self.parent_type == "canvas":
                update_content(self.frame, curr_path, stay=True)
            #otherwise, just pass the parent-frame
            else:
                update_content(self.parent, curr_path, stay=True)

    #function which makes menu visible
    def make_menu_visible(self, event):
        self.tk_popup(event.x_root, event.y_root)

    #function which creates file
    def create_file(self):
        #for console
        print("File is being created")
        #if parent is canvas - create a createInstance class and pass the frame 
        # + set type to file
        if self.parent_type == "canvas":
            cr_file = createInstance(self.parent, type = "file",\
                 master_type = "canvas", frame = self.frame)
        #else - just create and pass the parent
        else:
            cr_file = createInstance(self.parent, type = "file")
    
    def create_folder(self):
        #for console
        print("Folder is being created")
        #if parent is canvas - create a createInstance class and pass the frame 
        # + set type to folder
        if self.parent_type == "canvas":
            cr_file = createInstance(self.parent, type = "folder", \
                master_type= "canvas", frame = self.frame)
        #else - just create and pass the parent
        else:
            cr_file = createInstance(self.parent, type = "folder")

#Rename Popup class
class RenamePopup(tk.Toplevel):
    #icon path for the popup
    icon_path = 'icons/icons8-rename-80.png'
    #standard values
    new_name = ""
    is_correct=False
    #initialization function
    def __init__(self, master=None, old_name="",  type="folder"):
        #calling parent initialization function
        super().__init__(master)
        #assigning parent variable to master
        self.parent = master
        #assigning type of instance beign renamed
        self.type = type
        #get the old name of the instance
        self.old_name = old_name
        #set the image for the popup
        png = Image.open(self.icon_path)
        self.icon = ImageTk.PhotoImage(png) 
        self.tk.call('wm', 'iconphoto', self._w, self.icon)
        #make only the popup accessible to interact with
        self.grab_set()
        #set the title of the popup
        self.title("Rename")
        #set the popup size
        w_popup = 400
        h_popup = 150
        #set padding on x axis
        padding_lr = [10,10]
        #set padding on y axis
        padding_ud = [5,0]
        #if DPI Scaling is off, scale the values down
        if not DPI_aware:
            w_popup /= 1.5
            h_popup /= 1.5
            padding_lr = [x / 1.5 for x in padding_lr]
            padding_ud = [x / 1.5 for x in padding_ud]
        #get the heigth and the width of the screen
        w_scr = self.winfo_screenwidth()
        h_scr = self.winfo_screenheight()
        #get the x and y to position it in the center
        x = (w_scr/2) - (w_popup/2)
        y = (h_scr/2) - (h_popup/2)
        #assign geometry
        self.geometry("%dx%d+%d+%d" % (w_popup, h_popup, x, y))
        #disable resizable property
        self.resizable(False, False)
        #set up columnconfigure with equal weigth
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        #create a label, which asks the user to enter a name
        self.label = ttk.Label(self, text = "Enter a New Name:")
        #position it and make it 2 columns wide
        self.label.grid(column=0, row=0, columnspan=2, sticky='ew',\
             padx=tuple(padding_lr), pady=tuple(padding_ud))
        #create an entry instance, in which person should write
        self.entry = ttk.Entry(self)
        #position it for it to be two columns wide
        self.entry.grid(column=0, row=1, columnspan=2, sticky = 'ew', \
            padx=tuple(padding_lr), pady= tuple(padding_ud))
        #if we are renaming te file, create the text with extencion
        if self.type == "file":
            self.extension = str(Path(self.old_name).suffix)
            self.ext_label = ttk.Label(self, text = self.extension)
            self.ext_label.grid(column = 3, row = 1, sticky = 'ew', padx =(0, padding_lr[1]))
        #create empty message error Label
        self.error_msg = ttk.Label(self, text= "", foreground="red")
        #position it also 2 columns wide
        self.error_msg.grid(column=0, row =2, columnspan=2)
        #create OK button, which command is custom function check
        self.button_ok = ttk.Button(self, text="OK", command=self.check)
        #place it in the first column
        self.button_ok.grid(column=0,row=3, sticky = 'ew', \
            padx=(padding_lr[0], 0), pady=tuple(padding_ud))
        #create cancel button, which destroys the popup
        self.button_cancel = ttk.Button(self, text="Cancel", command=self.destroy)
        #position it in the second column
        self.button_cancel.grid(column=1,row=3, sticky = 'ew', \
            padx=(0, padding_lr[1]), pady=tuple(padding_ud))

        #create the list of instances in the current path
        dir_list = Path(self.old_name).parent.iterdir()
        self.dir_list = [str(x) for x in dir_list]

    #checking the entered name
    def check(self):
        #setting is_correct beforehand
        self.is_correct = True
        #creating an array with prohibited symbols
        unallowed_s = '/\:;"<>|*'
        #if the type is file, then add file's extension
        if self.type == "file":
            name = self.entry.get() + self.extension
        #else - just get what was input in the entry widget
        else:
            name = self.entry.get()
        #check for prohibited symbols
        for s in name:
            #if there is one
            if s in unallowed_s:
                #set is_correct to false
                self.is_correct = False
                #display the error message
                self.error_msg.config(text = "Don't use: / \ : ; \" < > | *")
                #break the cycle
                break
        #check the instance in the curr_path
        for ins_name in self.dir_list:
            #get if the instance is a directory
            ins_is_dir = Path(ins_name).is_dir()
            #variable which is true if the checked and renamed instances are both dirs
            thesame_folder = self.type == "folder" and ins_is_dir
            #variable which is true if the checked and renamed instances are both file
            thesame_file = self.type == "file" and not ins_is_dir
            ##variable which is true if the checked and renamed instances are the same type
            thesame = thesame_folder or thesame_file
            #if the name and type are the same
            if ins_name.endswith(name) and thesame:
                #set is_correct to false
                self.is_correct = False
                #display the error message according to the instance type
                if self.type == "folder":
                    self.error_msg.config(text = "Folder with such name already exists!")
                if self.type == "file":
                    self.error_msg.config(text = "File with such name already exists!")
                break
        #if the renamed name is correct
        if self.is_correct:
            #set new_name to the entered name 
            self.new_name = name
            os.rename(self.old_name, str(Path(self.old_name).parent)+ "\\" + self.new_name)
            self.destroy()
            #update the content of the path
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

    #create a popup menu bind to class
    def initialise_popup(self):
        #create a menu
        self.popup = tk.Menu(self.button, tearoff=False)
        #add command Open folder written in bold
        self.popup.add_command(label = "Open Folder", font=('Lucida', 9, 'bold'), command=self.open)
        #if the path is not root (there are files and folders except drives)
        if self.abs_path.split('\\')[1] != "":
            #add command Rename folder
            self.popup.add_command(label = "Rename Folder", command = self.rename)
            #add command Copy folder
            self.popup.add_command(label = "Copy Folder", command=self.copy)
            #add command Cut folder
            self.popup.add_command(label = "Cut Folder", command = self.cut)
            #add a separator
            self.popup.add_separator()
            #add command Delete folder
            self.popup.add_command(label = "Delete Folder", command=self.delete)
        #bind rclick to create a popup
        self.button.bind("<Button-3>", self.instance_popup)
    
    #popup appearence
    def instance_popup(self, event):
        self.popup.tk_popup(event.x_root, event.y_root)

    #open function
    def open(self):
        #for console
        print("Folder opened")
        #update content, going inside the folder
        update_content(self.parent, self.abs_path)

    #rename function
    def rename(self):
        #for console
        print("Folder is being renamed")
        #create rename popup with type "folder"
        rename_pop = RenamePopup(self.parent, self.abs_path, "folder")

    #copy function
    def copy(self):
        #for console
        print(f"{self.abs_path} is being copied")
        #write address to global variable copy buffer
        # and set cut to false
        global copy_buff, cut
        copy_buff = self.abs_path
        cut = False
    
    #cut function
    def cut(self):
        #for console
        print(f"{self.abs_path} is being cut")
        #copying address to global variable copy buffer
        # and setting global cut to True
        global copy_buff, cut
        copy_buff = self.abs_path
        cut = True

    #remove function for folder
    def delete(self):
        #for console
        print("Folder is being deleted")
        #remove the folder and update the content
        shutil.rmtree(self.abs_path)
        update_content(self.parent, curr_path, True)
        
    #function if folder button is clicked
    def clicked(self):
        #print for console:
        print(f"Folder Path: {self.abs_path}")
        print(f"Folder Name: {self.name}\n")
        #update the content of the parent frame with the self path
        update_content(self.parent, self.abs_path)

#class for the file button, which is a child to folderbutton
class FileButton(FolderButton):
    #initialize suffix strings
    video_sfxs='.mp4.mov.wmv.avi.avchd.mpeg.mpg'
    audio_sfxs='.m4a.flac.mp3.wav.wma.aac'
    text_sfxs='.doc.docx.odt.pdf.rtf.tex.txt.wpd'
    photo_sfxs='.ai.bmp.gif.ico.jpeg.jpg.png.ps.svg.tif.tiff'
    archive_sfxs='.7z.arj.deb.pkg.rar.rpm.z.zip'

    #initialization function
    def __init__(self, master, path, button):
        #add new variable which has the extension of the file
        self.extension = Path(path).suffix
        #change icon path according to the type of the file
        if self.extension in self.video_sfxs:
            self.icon_path = "icons/icons8-cinema-80.png"
        elif self.extension in self.audio_sfxs:
            self.icon_path = "icons/icons8-audio-file-80.png"
        elif self.extension in self.photo_sfxs:
            self.icon_path = "icons/icons8-picture-480.png"
        elif self.extension in self.text_sfxs:
            self.icon_path = "icons/icons8-document-480.png"
        elif self.extension in self.archive_sfxs:
            self.icon_path = "icons/icons8-archive-80.png"
        else:
            self.icon_path = "icons/icons8-blank-file-100.png"
        #call the parent class init method
        super().__init__(master, path, button)

    #rewrite the popup from FolderButton
    def initialise_popup(self):
        #create a menu for popup
        self.popup = tk.Menu(self.button, tearoff=False)
        #add command Open File, which is written in bold
        self.popup.add_command(label = "Open File", font=('Lucida', 9, 'bold'), command=self.open)
        #add command Rename file
        self.popup.add_command(label = "Rename File", command=self.rename)
        #add command Copy file
        self.popup.add_command(label = "Copy File", command = self.copy)
        #add command Cut file
        self.popup.add_command(label = "Cut File", command = self.cut)
        #add the separator
        self.popup.add_separator()
        #add delete file command
        self.popup.add_command(label = "Delete File", command=self.delete)
        #bind rclick to the menu popup
        self.button.bind("<Button-3>", self.instance_popup)

    #opening a file function
    def open(self):
        #for console
        print("File opened")
        #start the file
        os.startfile(self.abs_path)
    
    #rename a file function
    def rename(self):
        #for console
        print("File is being renamed")
        #create a rename popup with type "file"
        rename_pop = RenamePopup(self.parent, self.abs_path, "file")

    #delete function, rewritten for file
    def delete(self):
        #for console
        print("File is being deleted")
        #remove file and update
        os.remove(self.abs_path)
        update_content(self.parent, curr_path, True)

    #rewrite the function clicked
    def clicked(self):
        #print in console
        print("File clicked")
        print(f"File Name: {self.name}")
        print(f"File Extension: {self.extension}\n")
        #start the file
        self.open()

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

    #rewriting standart FolderButton initialise_popup function
    def initialise_popup(self):
        #creating a popup
        self.popup = tk.Menu(self.button, tearoff=False)
        #adding only one command - to opent the parent folder
        self.popup.add_command(label = "Open Folder", font=('Lucida', 9, 'bold'), command=self.open)
        #binding rclick on popup appereance
        self.button.bind("<Button-3>", self.instance_popup)

    #rewrite the function clicked
    def clicked(self):
        #print in console
        print("Parent Folder clicked")
        print(f"Path of parent folder: {self.abs_path}\n")
        #update the content of the parent with the self path
        update_content(self.parent, self.abs_path)

#filling content inside forking frame with folders and files
def fill_content(parent, path):
    global curr_path
    curr_path = path
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
        paste_menu_parent = rclickMenu(parent)
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
    global drives, folders, files, curr_path
    #firstly, destroy all the widgets on the working screen
    for widget in parent.winfo_children():
        widget.destroy()
    
    #then, get the canvas and assure the scroll is on top
    # if stay isn't specified
    if not stay:
        #get grandparent
        grandparent_name = parent.winfo_parent()
        grandparent = parent._nametowidget(grandparent_name)
        #move to up
        grandparent.yview_moveto(0.0)
        #if path is not empty - assign rclickMenu to grandparent 
        # (to wide) the zone of using popup Menu
        if path != "":
            paste_menu_canvas = rclickMenu(grandparent, "canvas", parent)

    #fill content with new path passed, refresh global variables
    curr_path = path
    drives, folders, files = fill_content(parent, path)

#save settings function, which saves the DPI state
def save_settings(DPI_awareness):
    #opening the binary file
    with open("settings.bin", "wb") as file:
        #converting DPI_aware to bytes and writing it into the file
        DPI_b = DPI_awareness.to_bytes(1, "little")
        file.write(DPI_b)
        file.close()

#load settigs function, which loads the DPI state
def load_settings():
    #if file exists and the contents are not empty, read it
    if os.path.isfile("settings.bin"):
        if os.stat("settings.bin").st_size != 0:
            with open("settings.bin", "rb") as file:
                DPI_b = file.read(1)
                DPI_awareness = bool.from_bytes(DPI_b, "little")
                file.close()
                return DPI_awareness
    #else - return the load error, which uses standard "False"
    return "load error"