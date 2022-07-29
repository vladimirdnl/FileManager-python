#import py libraries
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from ctypes import windll
#import from the local folder
import tools
import sys
tools_mod = sys.modules["tools"]

loaded = tools.load_settings()
if loaded != "load error":
    tools_mod.DPI_aware = loaded
#set dpi awareness according to the variable
if tools_mod.DPI_aware:   
    windll.shcore.SetProcessDpiAwareness(1)

class App(tk.Tk):
    def __init__(self, current_path=""):
        super().__init__()
        self.current_path = current_path
        w_wind = 800 
        h_wind = 650
        max_w = 1000
        max_h = 800
        if not tools_mod.DPI_aware:
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
        min_height = 450
        if not tools_mod.DPI_aware:
            min_height = round(min_height/1.5)
        self.minsize(round(w_wind), min_height)
        self.title("File Manager")

class AppMenu(tk.Menu):
    def __init__(self, master=None):
        super().__init__(master)
        self.parent = master
        self.filemenu = tk.Menu(self, tearoff = False)
        self.add_cascade(label="    File    ", menu=self.filemenu)
        self.var = tk.IntVar(value = 0)
        if tools_mod.DPI_aware:
            print("yey")
            self.var = tk.IntVar(value = 1)
           
        self.filemenu.add_checkbutton(label="DPI Scaling", variable=self.var, command=self.oncheck)
            
        print(tools_mod.DPI_aware)
        self.filemenu.add_separator()
        self.filemenu.add_command(label= "Exit", command=self.parent.quit)

        self.openmenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label = "    Open    ", menu = self.openmenu)
        self.openmenu.add_command(label="Open Path")
    
    def oncheck(self):
        print("DPI Checked")
        messagebox.showinfo(title="Settings", \
            message="For the settings to change, you may restart the application")
        if tools_mod.DPI_aware:
            tools_mod.DPI_aware = False
        else:
            tools_mod.DPI_aware = True



#function to return the image for the application
def get_app_icon(path):
    png = Image.open(path)
    ico = ImageTk.PhotoImage(png)
    return ico

    
#* The main part of the program
if __name__ == '__main__':
    #create global variables, which resemble
    # available drives, current folders and current files
    #set the path for application icon
    app_iconpath = 'icons/icons8-app-icon-240.png' 
    #set the start path of the application
    start_path = ""
    
    #create the instance of application (class App)
    fm_app = App()
    #set the iconphoto by the function get_app_icon
    # which opens image then returns it
    fm_app.wm_iconphoto(False, get_app_icon(app_iconpath))
    fm_menu = AppMenu(fm_app)
    fm_app.config(menu = fm_menu)
    #create the main frame of the app
    frame_main = ttk.Frame(fm_app)
    #make it fill both X and Y, and expand with the window
    frame_main.pack(fill=tk.BOTH, expand=1)

    #create a canvas, which can be scrolled
    canvas = tk.Canvas(frame_main)
    #pack it to the left side, so that scrollbar could be
    # packed to the right side, make it also fill both X and Y,
    # and expand proportionally to the window
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    #create custom view function, which allows to
    # prevent scrollbar from scrolling when
    # everything on canvas is visible
    def custom_yview(*args):
        if canvas.yview() == (0.0, 1.0):
            return
        canvas.yview(*args)

    #create a vertical scrollbar, whi has custom_yview as a command
    scroll_bar = ttk.Scrollbar(frame_main, orient="vertical", command=custom_yview)
    #pack it to the right side and make it fill Y
    scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
    #connect canvas and scrollbar
    canvas.configure(yscrollcommand=scroll_bar.set)

    #create our working screen which has canvas as a parent
    working_screen = ttk.Frame(canvas)
    #create a window of working screen inside the canvas
    canvas_frame = canvas.create_window((0, 0), window=working_screen, anchor='nw', tags= ["canv_frame"])
     
    # w_screen_pastePopup = tk.Menu(canvas, tearoff=False)
    # w_screen_pastePopup.add_command(label = "Paste here", command=paste_here)

    # def rclick_popup(event):
    #     print("popup assigned!")
    #     w_screen_pastePopup.tk_popup(event.x_root, event.y_root)
    # canvas.bind("<Button-3>", rclick_popup)

    #function to control the width of the working screen
    def FrameWidth(event):
        canvas.itemconfig(canvas_frame, width=event.width)
    #function to control the scrollregion of canvas
    def OnFrameConfigure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    #function to bind mouse wheel and to control scrolling
    def OnMousewheel(event):
        if canvas.yview() == (0.0, 1.0):
            return
        canvas.yview_scroll(round(-1*(event.delta/120)), "units")

    #bind mouse wheel
    canvas.bind_all("<MouseWheel>", OnMousewheel)
    #bind definition of scroll region
    working_screen.bind("<Configure>", OnFrameConfigure)
    #bind frame width change
    canvas.bind('<Configure>', FrameWidth)

    #assign global variables from other module to return values of fill content
    tools_mod.drives, tools_mod.folders, tools_mod.files = tools_mod.fill_content(working_screen, start_path)
    #start the main loop of the app
    fm_app.mainloop()
    print(f"DPI_aware on exit: {tools_mod.DPI_aware}")
    tools_mod.save_settings(tools_mod.DPI_aware)