import tkinter as tk
from tkinter import *
import matplotlib.animation as animation 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import random



class StrainPlot(tk.Frame):

    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        label = Label(self, text="strain plot")
        label.pack(pady=10, padx=10)


        self.fig = Figure(figsize = (5,5), dpi=100)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ani_status = 0

        self.xList = controller.xList
        self.yList = controller.yList


        canvas = FigureCanvasTkAgg(self.fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)


        self.ani = animation.FuncAnimation(fig = self.fig, func = self.animate, interval=100)

        start_button = Button(self, text ="START", command = lambda : self.ani_off())
        start_button.pack()
    

    def ani_off(self):
        self.ani_status = not self.ani_status


    def animate(self, i):
        if self.ani_status:
            self.xList.append(time.time())
            self.yList.append(random.random())

            self.ax.clear()
            self.ax.plot(self.xList[-20:], self.yList[-20:])

            self.ax.set_ylim(ymin=0.0, ymax=1.01) 






class setOptions(tk.Frame):
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        
        label = Label(self, text="options blank")
        label.pack(pady=10, padx=10)



class OutputLog(tk.Frame):
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)

        label = Label(self, text="output log")
        label.pack(pady=10, padx=10)
    




class mainApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        ## TEST MODEL ##
        self.name = "Test 1"
        self.frequency = 100
        self.xList = []
        self.yList = []  

        self.running = 0


        ## CONTAINER ## 
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        self.frames = {}


        for F in (StrainPlot, setOptions, OutputLog):
            frame = F(container, self)
            self.frames[F] = frame
            self.show_frame(F)

        self.frames[StrainPlot].grid(column=1, row=0, columnspan=1, rowspan=3)
        self.frames[setOptions].grid(column=0, row=0, columnspan=1, rowspan=3)
        self.frames[OutputLog].grid(column=2, row=0, columnspan=1, rowspan=3, sticky ='swse')


    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
    

    def get_frame(self, page_name):
        frame = self.frames[page_name]
        return frame


    


if __name__ == "__main__":
    root = tk.Tk()
    mainApp(root).pack(side="top", fill="both", expand=True)
    root.mainloop()