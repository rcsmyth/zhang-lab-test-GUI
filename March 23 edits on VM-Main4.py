import tkinter as tk 
from tkinter import * 
from tkinter.scrolledtext import ScrolledText 
from dataclasses import dataclass 
from typing import List 
import numpy as np 

import time, random 


from matplotlib.animation import FuncAnimation 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
from matplotlib.figure import Figure 
import matplotlib.pyplot as plt 
from matplotlib.figure import SubplotParams 


from concurrent.futures import ThreadPoolExecutor 


## DataClass: Reading ##
@dataclass
class Reading:
    elapsedMin: float
    strain: float 
    strainRate: float



## Model: Test.py ##
class Test:
    """Object for holding all the data associated with a Test."""

    def __init__(self):  
        self.name = tk.StringVar()
        self.material = tk.StringVar()
        self.freq: tk.StringVar() = "100"
        self.notes = tk.StringVar()

        self.readings: List[Reading] = []

    



## TestHandler.py ## 
class TestHandler:
    def __init__(self, name: str = "Test 1"):
        self.name = name
        self.root: tk.Tk = strainApp.ROOT
        self.test = Test()
        self.readings: List[Reading] = []
        self.elapsed_min: float = float()
        self.strain: float = float()
        self.strain_rate: float = float()
        self.is_running = False
        self.request_stop = False
        self.views: List[tk.Widget] = []
        self.pool = ThreadPoolExecutor(max_workers=4)

    def start_test(self): 
        self.start_time = time.time() 
        self.is_running = True
        #self.root.start_btn.configure(state="disabled")
        self.pool.submit(self.cont_test)

    def cont_test(self):
        self.is_running = True
        self.request_stop = False
        self.take_readings()

    def stop_test(self):
        self.request_stop = True 
        #self.rebuild_views()

    def take_readings(self):
        # loop -------------------------------------
        while self.is_running and not self.request_stop:
            self.pool.submit(self.get_strain) 
            self.pool.submit(self.get_time) 
            self.pool.submit(self.get_strain_rate) 
            reading = Reading(
                elapsedMin=self.elapsed_min, strain=self.strain, strainRate=self.strain_rate
            )
            self.readings.append(reading)

    def get_strain(self):
        self.strain = np.sqrt(self.elapsed_min) 

    def get_time(self):
        self.elapsed_min = (time.time() - self.start_time) 
    
    def get_strain_rate(self): 
        if self.elapsed_min > 0: 
            strain_diff = self.strain - self.readings[-1].strain 
            time_diff = self.elapsed_min - self.readings[-1].elapsedMin
            #strain_diff = self.strain - self.readings[-2].strain 
            #time_diff = self.elapsed_min - self.readings[-2].elapsedMin
            self.strain_rate = strain_diff / time_diff  
        else:
            self.strain_rate = 0 


    def rebuild_views(self): 
        for widget in self.views: 
            if widget.winfo_exists():
                self.root.after_idle(widget.build, {"reload": True})
            else:
                self.views.remove(widget)




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
 

    def build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # row 0 col 0 --------------------------------------
        self.start_btn = tk.Button(self)
        self.start_btn.configure(text="Start", state="normal", command=self.handler.start_test)
        self.start_btn.grid(row=0, column=0, sticky="ew")

        # row 0 col 1 --------------------------------------
        self.stop = tk.Button(self) 
        self.stop.configure(text="Stop", state="disabled", command=self.handler.stop_test)
        self.stop.grid(row=0, column=1, sticky="ew")

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



## StrainPlot.py ## 
class StrainPlot(tk.Frame):
    """Renders data from a TestHandler as it is collected."""

    def __init__(self, parent: tk.Frame, handler: TestHandler):
        super().__init__(parent)
        self.handler = handler
        self.build()

    def build(self):
        
        self.fig, (self.strainplt, self.strainrateplt) = plt.subplots(2,
            figsize=(15,8),
            dpi=100,
            constrained_layout=True,
            subplotpars=SubplotParams(left=0.5, bottom=0.1, right=0.95, top=0.95),
            sharex=True
        )
        

        self.strainplt.set_ylabel("Strain")
        self.strainplt.grid(color="darkgrey", alpha=0.65, linestyle='') ##### removed marker from .grid
        #self.strainplt.grid(color="darkgrey", alpha=0.65, marker='o', linestyle='')
        self.strainplt.set_facecolor("w")
        self.strainrateplt.set_xlabel("Time (s)")
        self.strainrateplt.set_ylabel("Strain Rate")
        self.strainrateplt.grid(color="darkgrey", alpha=0.65, linestyle='') ##### removed marker from .grid
        #self.strainrateplt.grid(color="darkgrey", alpha=0.65, marker='o', linestyle='')
        self.strainrateplt.set_facecolor("w")
 

        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.get_tk_widget().grid()
        
        
        interval = float(self.handler.test.freq)
        self.ani = FuncAnimation(self.fig, self.animate, interval=interval)



    def animate(self, interval):
        if self.handler.is_running:
            elapsedMin = []
            strain = []
            strainRate = []
            readings = tuple(self.handler.readings)

            for reading in readings:
                elapsedMin.append(reading.elapsedMin)
                strain.append(reading.strain)
                strainRate.append(reading.strainRate)

            
            self.strainplt.clear()
            self.strainrateplt.clear()


            with plt.style.context("bmh"):
                self.strainplt.set_ylabel("Strain")
                self.strainplt.grid(color="darkgrey", linestyle='dashed') ##### removed marker
                #self.strainplt.grid(color="darkgrey", linestyle='dashed', marker='o', markerfacecolor='blue')
                self.strainplt.set_facecolor("w")
                self.strainplt.margins(0, tight=True) 
                self.strainplt.plot(elapsedMin, strain)

                self.strainrateplt.set_xlabel("Time (s)")
                self.strainrateplt.set_ylabel("Strain Rate")
                self.strainrateplt.grid(color="darkgrey", linestyle='dashed') ##### removed marker
                #self.strainrateplt.grid(color="darkgrey", linestyle='dashed', marker='o', markerfacecolor='blue')
                self.strainrateplt.set_facecolor("w")
                self.strainrateplt.margins(0, tight=True) 
                self.strainrateplt.plot(elapsedMin, strainRate)







## MainFrame.py ##
class MainFrame(tk.Frame):
    """Main Frame for the application."""      

    def __init__(self, parent: tk.Frame):
        super().__init__(parent)

        self.parent: tk.Frame = parent
        self.handler = TestHandler()
        self.strainplot: StrainPlot = None
        self.strainplot2: StrainPlot = None
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
        self.strainplot = StrainPlot(plt_frm, self.handler)
        self.strainplot.grid(row=0, column=0, sticky="nsew") ##### changed stick to sticky
        plt_frm.grid(row=0, column=1, rowspan=2)

                

        

## strainApp.py ##
class strainApp(tk.Frame):
    """Core object for the application.

    Used to define widget styles.
    """
    def __init__(self, parent):
        super().__init__(parent)
        parent.resizable(0, 0)
        parent.tk_setPalette(background="#FAFAFA")
        
        self.winfo_toplevel().protocol("WM_DELETE_WINDOW", self.close)

        MainFrame(self).grid() 

    def close(self) -> None:
        self.quit()



## VM - MAIN  ## 
def main():
    """The Tkinter entry point of the program; enters mainloop."""
    root = tk.Tk()
    strainApp.ROOT = root
    strainApp(root).grid()
    root.mainloop()


     

if __name__ == "__main__":
    main()