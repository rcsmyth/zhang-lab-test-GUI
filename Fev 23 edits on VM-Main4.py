import tkinter as tk
##
import numpy as np
##
from tkinter import * 
from tkinter.scrolledtext import ScrolledText
from dataclasses import dataclass
from typing import List

import time, random


from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.figure import SubplotParams

from concurrent.futures import ThreadPoolExecutor
 
# things to fix
# 1) graph is slow / slagging and  refreshing
# 2) strain rate vs time plot (how to take derivative?)
# 3) fix the xaxis labels

# 4) maybe gray out the start button when starting test (instead of button changing test)
# 5) make a pause button
# 6) make freqnecy to work (might need multiple threads)



## DataClass: Reading ##
@dataclass
class Reading:
    elapsedMin: float
    strain: float 


## Model: Test.py ##
class Test:
    """Object for holding all the data associated with a Test."""

    def __init__(self): #def update name, material, etc ??? where in scalewiz
        self.name = tk.StringVar()
        self.material = tk.StringVar()
        self.freq: tk.StringVar() = "1000"
        self.notes = tk.StringVar()

        self.readings: List[Reading] = []

    
##### ^^^ those are like default settings when you make a new test


## TestHandler.py ## 
class TestHandler:
    def __init__(self, name: str = "Test 1"):
        self.name = name
        self.root: tk.Tk = strainApp.ROOT  #### what does this do?
        self.test = Test() 
        self.readings: List[Reading] = []
        self.elapsed_min: float = float() #current duration
        self.strain: float = float()
        #
        self.is_running = False
        self.request_stop = False
        self.views: List[tk.Widget] = []  #### what does this do?
        self.pool = ThreadPoolExecutor(max_workers=3)
    
    def start_test(self): 
        self.start_time = time.time() 
        self.is_running = True
        self.pool.submit(self.cont_test)
        self.rebuild_views()

    def cont_test(self):
        self.is_running = True
        self.request_stop = False
        self.take_readings()

    def stop_test(self):
        self.request_stop = True 
        self.rebuild_views()

    def take_readings(self):
        # loop -------------------------------------
        while self.is_running and not self.request_stop:
            self.elapsed_min = (time.time() - self.start_time) ####### took out the /60
            #self.strain = random.random() ### random data to generate the graph
            self.strain = np.sqrt(self.elapsed_min) ###### commented out above and added
            reading = Reading(
                elapsedMin=self.elapsed_min, strain=self.strain
            )
            self.readings.append(reading) ### adds times and strain values into array


### what does this do?
#doesnt work rn, start should change to stop
    def rebuild_views(self): 
        for widget in self.views: 
            if widget.winfo_exists():
                self.root.after_idle(widget.build, {"reload": True})
            else:
                self.views.remove(widget)



## these are just the buttons, but they dont do anything yet right? (i cant run the thing)
## TestInfoEntry.py ##
class TestInfoEntry(tk.Frame):
    """A widget for inputting Test information."""
    def __init__(self, parent:tk.Widget, handler: TestHandler):
        super().__init__(parent)
        self.handler: TestHandler = handler 
        self.build()
    
    def build(self):
        self.grid_columnconfigure(1, weight=1)


        # row 0 ---------------------------------------------
        name_lbl = tk.Label(self, text="Name:", anchor="e")
        name_lbl.grid(row=0, column=0, sticky="ew")       
        name_ent = tk.Entry(self, textvariable=self.handler.test.name)
        name_ent.grid(row=0, column=1, sticky="ew")
        
        # row 1 ---------------------------------------------  
        matr_lbl = tk.Label(self, text="Material:", anchor="e")
        matr_lbl.grid(row=1, column=0, sticky="ew")      
        matr_ent = tk.Entry(self, textvariable=self.handler.test.material)
        matr_ent.grid(row=1, column=1, sticky="ew")

        # row 2 ---------------------------------------------  
        freq_lbl = tk.Label(self, text="Frequency:", anchor="e")
        freq_lbl.grid(row=2, column=0, sticky="ew")  
        freq_ent = tk.Entry(self, textvariable=self.handler.test.freq)
        freq_ent.grid(row=2, column=1, sticky="ew")    

        # row 3 ---------------------------------------------  
        notes_lbl = tk.Label(self, text="Notes:", anchor="e")
        notes_lbl.grid(row=3, column=0, sticky="ew")  
        notes_ent = tk.Entry(self, textvariable=self.handler.test.notes)
        notes_ent.grid(row=3, column=1, sticky="ew")    




## TestControls.py ##
class TestControls(tk.Frame):
    """A widget for Test Controls."""
    def __init__(self, parent: tk.Widget, handler: TestHandler):
        super().__init__(parent)
        self.handler: TestHandler = handler 
        self.build()

    def make_start_btn(self):
        if self.handler.is_running and not self.handler.request_stop:
            self.start_btn.configure(text="Stop", command=self.handler.stop_test)
        elif not self.handler.is_running and self.handler.request_stop:
            self.start_btn.configure(text="Continue")
        elif not self.handler.is_running and not self.handler.request_stop:
            self.start_btn.configure(text="Start", command=self.handler.start_test)


    def build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # row 0 col 0 --------------------------------------
        self.start_btn = tk.Button(self)
        self.make_start_btn()
        self.start_btn.grid(row=0, column=0, sticky="ew")

        # row 0 col 1 --------------------------------------
        self.save = tk.Button(self) 
        self.save.configure(text="Save")
        self.save.grid(row=0, column=1, sticky="ew")

        # row 1 --------------------------------------
        self.log_text = ScrolledText(
            self, background="white", height=5, width=44, state="disabled"
        )
        self.log_text.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.display("Hello, this is a log - welcome!")

    def display(self, msg: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", "".join((msg, "\n")))
        self.log_text.configure(state="disabled")
        self.log_text.yview("end") 




## LivePlot.py ## 
class LivePlot(tk.Frame):
    """Renders data from a TestHandler as it is collected."""

    def __init__(self, parent: tk.Frame, handler: TestHandler):
        super().__init__(parent)
        self.handler = handler
        self.build()

    def build(self):
        
        
        self.fig = Figure(figsize =(10,5), dpi=100)
        self.axis = self.fig.add_subplot(1,1,1)
        self.fig.tight_layout()

        self.axis.set_xlabel("Time (s)", visible=True)
        self.axis.set_ylabel("Strain Rate", visible=True)
        self.axis.grid(color="darkgrey", alpha=0.65, linestyle="-")
        self.axis.set_facecolor("w")
 
        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.get_tk_widget().grid()
        interval = float(self.handler.test.freq)
        self.ani = FuncAnimation(fig = self.fig, func = self.animate, interval=interval)
        

    def animate(self, interval):
        if self.handler.is_running:
            elapsedMin = []
            strain = []
            readings = tuple(self.handler.readings)

            for reading in readings:
                elapsedMin.append(reading.elapsedMin)
                strain.append(reading.strain)
            
            self.axis.clear()
            self.axis.plot(elapsedMin, strain) ####### removed the 50 ( only plotted most recent pts )





## MainFrame.py ##
class MainFrame(tk.Frame):
    """Main Frame for the application."""      

    def __init__(self, parent: tk.Frame):
        super().__init__(parent)

        self.parent: tk.Frame = parent
        self.handler = TestHandler()
        self.plot: LivePlot = None
        self.build()

    def build(self):
        """Builds the UI"""
        self.grid_columnconfigure(0, weight=1)

        # row 0 ---------------------------------------------
        test_info = TestInfoEntry(self, self.handler)
        test_info.grid(row=0, column=0, sticky="new")

        # row 1 ---------------------------------------------
        test_controls = TestControls(self, self.handler)
        test_controls.grid(row=1, column=0, sticky="nsew")

        # row 0 col 1 ---------------------------------------
        plt_frm = tk.Frame(self)
        self.plot = LivePlot(plt_frm, self.handler)
        self.plot.grid(row=0, column=0, stick="nsew")
        plt_frm.grid(row=0, column=1, rowspan=2)

        

## strainApp.py ## # ##for visuals ??
class strainApp(tk.Frame): #the main frame for the whole program, like how everything starts here
    """Core object for the application.

    Used to define widget styles.
    """
    def __init__(self, parent):
        super().__init__(parent)
        parent.resizable(0, 0)
        parent.tk_setPalette(background="#FAFAFA")
        
        MainFrame(self).grid() 



## VM - MAIN  ## 
def main():
    """The Tkinter entry point of the program; enters mainloop."""
    root = tk.Tk()
    strainApp.ROOT = root
    strainApp(root).grid()
    root.mainloop()
 
if __name__ == "__main__":
    main()