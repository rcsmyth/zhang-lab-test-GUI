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

        plot_win = LabelFrame(self, text="Strain vs Time Plot", height=400, width=550)
        plot_win.grid()


        self.fig = Figure(figsize = (10,5), dpi=100)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.fig.tight_layout()
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Strain") 

        self.ani_status = 0
        self.xList = controller.xList
        self.yList = controller.yList


        canvas = FigureCanvasTkAgg(self.fig, plot_win)
        canvas.draw()
        canvas.get_tk_widget().grid()
 


        self.ani = animation.FuncAnimation(fig = self.fig, func = self.animate, interval=100)

        start_button = Button(self, text ="START", command = lambda : self.ani_off())
        start_button.grid()
    

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
        
        test_param = LabelFrame(self, text="Test parameters:", height=100, width=200) 
        name = Label(test_param, text="Name:")
        name_input = Text(test_param, height=1, width=25)
        material = Label(test_param, text="Material:")
        material_input = Text(test_param, height=1, width=25)



        test_param.grid() 
        name.grid(column=0, row=0)
        name_input.grid(column=1,row=0)
        material.grid(column=0, row=1)
        material_input.grid(column=1,row=1)


 



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

 


        self.frames = {}

        for F in (StrainPlot, setOptions, OutputLog):
            frame = F(parent, self)
            self.frames[F] = frame
            self.show_frame(F)

        

        self.frames[setOptions].grid(column = 0, row=0, padx=5)
        self.frames[OutputLog].grid(column = 0, row=1)
        self.frames[StrainPlot].grid(column = 1, row=0, rowspan=2, padx=20)


    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
    

    def get_frame(self, page_name):
        frame = self.frames[page_name]
        return frame


    


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry('1300x600')
    root.title('Zhang Lab')
    root.resizable(False, False)

    mainApp(root).grid()


    root.mainloop()