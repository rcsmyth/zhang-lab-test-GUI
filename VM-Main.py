import random 
import time

import matplotlib.pyplot as plt 
import matplotlib.animation as animation 
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
 

import tkinter as tk
from tkinter import *
 

fig = Figure(figsize = (5,5), dpi=100)
ax = fig.add_subplot(1, 1, 1)

xList = []
yAList = [] 
yBList = []
yA = 1 
start_time = time.time() 


def animate(i, xList, yAList, yBList):
    global yA

    xList.append(time.time() - start_time)
    yAList.append(random.random())
    yBList.append(random.random())

    ax.clear()
    if yA == 1:
        ax.plot(xList[-20:], yAList[-20:])
    else:
        ax.plot(xList[-20:], yBList[-20:], 'm')

    ax.set_ylim(ymin=0.0, ymax=1.01)


def switchOn():
    global yA
    if yA==1:
        yA = 0
    else:
        yA = 1


class tkinterApp(tk.Tk):
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)    


        container = tk.Frame(self)  
        container.pack(side = "top", fill = "both", expand = True) 
        
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
  

        self.frames = {}   


        for F in (PageOne, PageTwo):
            frame = F(container, self)
            self.frames[F] = frame 
            frame.grid(row = 0, column = 0, sticky ="nsew")
  
        self.show_frame(PageTwo)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()




class PageOne(tk.Frame):

    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)

        label = Label(self, text="Page One")
        label.pack(pady=10, padx=10)

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        button = Button(self, text="Switch Graphs", command=switchOn)
        button.pack()




class PageTwo(tk.Frame):
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)

        label = Label(self, text="Start Page!!")
        label.pack(pady=10, padx=10)

        button1 = Button(self, text ="Click to start graph", 
        command = lambda : controller.show_frame(PageOne))

        button1.pack()






if __name__ == "__main__":
    app = tkinterApp()
    ani = animation.FuncAnimation(fig, animate, fargs=(xList, yAList, yBList), interval=100)
    app.mainloop()



