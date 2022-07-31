#import py libraries
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from ctypes import windll
#import from the local folder
import tools
#widen the default scope
import sys
tools_mod = sys.modules["tools"]

#load DPI settings 
loaded = tools.load_settings()
if loaded != "load error":
    tools_mod.DPI_aware = loaded
#print DPI Scaling state
print(f"DPI Scaling: {tools_mod.DPI_aware}")
#set dpi awareness according to the variable
if tools_mod.DPI_aware:   
    windll.shcore.SetProcessDpiAwareness(1)

#main application class
class App(tk.Tk):
    #initialization function
    def __init__(self):
        #parent initialization function
        super().__init__()
        #entering starting width and height of the app
        w_wind = 800 
        h_wind = 550
        #if DPI Scaling is not enabled, scale the values:
        if not tools_mod.DPI_aware:
            w_wind/=1.5
            h_wind/=1.5
        #print the width and the height of the screen
        w_scr = self.winfo_screenwidth()
        print(f"w_scr: {w_scr}")
        h_scr = self.winfo_screenheight()
        print(f"h_scr: {h_scr}")
        #get coordinates for the window to be in the center
        x = (w_scr/2) - (w_wind/2)
        y = (h_scr/2) - (h_wind/2)
        #assign geometry and the position on the screen
        self.geometry('%dx%d+%d+%d' % (w_wind, h_wind, x, y))
        #assign minimal height and minimal width for the window
        min_height = 450
        #scale if DPI scaling isn't turned on
        if not tools_mod.DPI_aware:
            min_height = round(min_height/1.5)
        self.minsize(round(w_wind), min_height)
        #set the title
        self.title("File Manager")

#the upper menu of an app
class AppMenu(tk.Menu):
    #initialization function
    def __init__(self, master=None):
        #call the parent initialization function
        super().__init__(master)
        #set parent variable to master
        self.parent = master
        #create a sub-menu (File submenu), turn off the tearoff
        self.filemenu = tk.Menu(self, tearoff = False)
        #add cascade to main menu and assign the submenu
        self.add_cascade(label="    File    ", menu=self.filemenu)
        #create a variable for checkbutton for DPI Scaling
        self.var = tk.IntVar(value = 0)
        if tools_mod.DPI_aware:
            #in case DPI Scaling is on, turn it to 1
            self.var = tk.IntVar(value = 1)
        #add a checkbutton for DPI Scaling, assign custom command oncheck
        self.filemenu.add_checkbutton(label="DPI Scaling", variable=self.var, command=self.oncheck)
        #add a separator
        self.filemenu.add_separator()
        #add an Exit command, which exits the application
        self.filemenu.add_command(label= "Exit", command=self.parent.quit)

        #create a new sub-menu (Open sub-menu)
        self.openmenu = tk.Menu(self, tearoff=False)
        #add the name and assing it to main menu
        self.add_cascade(label = "    Open    ", menu = self.openmenu)
        #create a command open path, which lets the user open the custom path
        self.openmenu.add_command(label="Open Path", command= self.open_path)
    
    #oncheck for checkbutton
    def oncheck(self):
        #for console
        print("DPI Checked")
        #show the info for the user
        messagebox.showinfo(title="Settings", \
            message="For the settings to change, you may restart the application")
        #change DPI_aware variable to its opposite
        if tools_mod.DPI_aware:
            tools_mod.DPI_aware = False
        else:
            tools_mod.DPI_aware = True
        self.quit()

    #open path function
    def open_path(self):
        #for console
        print("Opening Path")
        #get our main frame
        global working_screen
        #call the goToPath popup class
        goto_path = tools_mod.goToPath(working_screen)


#function to return the image for the application
def get_app_icon(path):
    png = Image.open(path)
    ico = ImageTk.PhotoImage(png)
    return ico

    
#* The main part of the program
if __name__ == '__main__':
    #assign the global variable working_screen, as our main screen
    global working_screen
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
    #print the DPI state on exit
    print(f"DPI_aware on exit: {tools_mod.DPI_aware}")
    #save DPI Scaling state
    tools_mod.save_settings(tools_mod.DPI_aware)