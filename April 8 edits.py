import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from dataclasses import dataclass
from typing import List
import numpy as np
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import SubplotParams
import matplotlib.pyplot as plt


@dataclass
class Reading:
    elapsedMin: float
    strain: float
    strainRate: float


class Test:
    def __init__(self):
        self.name = tk.StringVar()
        self.material = tk.StringVar()
        self.freq: tk.StringVar() = "100"
        self.notes = tk.StringVar()
        self.readings: List[Reading] = []


class TestHandler:
    def __init__(self, name: str = "Test 1"):
        self.name = name
        self.root: tk.Tk = StrainApp.ROOT
        self.test = Test()
        self.readings: List[Reading] = []
        self.elapsed_min: float = float()
        self.strain: float = float()
        self.strain_rate: float = float()
        self.is_running = False
        self.request_stop = False
        self.views: List[tk.Widget] = []

    def start_test(self):
        self.start_time = time.time()
        self.is_running = True
        self.take_readings()

    def stop_test(self):
        self.is_running = False

    def take_readings(self):
        while self.is_running:
            self.get_strain()
            self.get_time()
            self.get_strain_rate()
            reading = Reading(
                elapsedMin=self.elapsed_min, strain=self.strain, strainRate=self.strain_rate
            )
            self.readings.append(reading)
            time.sleep(0.1)

    def get_strain(self):
        self.strain = np.sqrt(self.elapsed_min)

    def get_time(self):
        self.elapsed_min = (time.time() - self.start_time)

    def get_strain_rate(self):
        if self.elapsed_min > 0:
            strain_diff = self.strain - self.readings[-1].strain
            time_diff = self.elapsed_min - self.readings[-1].elapsedMin
            self.strain_rate = strain_diff / time_diff
        else:
            self.strain_rate = 0

    def rebuild_views(self):
        for widget in self.views:
            if widget.winfo_exists():
                self.root.after_idle(widget.build, {"reload": True})
            else:
                self.views.remove(widget)


class TestInfoEntry(tk.Frame):
    def __init__(self, parent: tk.Widget, handler: TestHandler):
        super().__init__(parent)
        self.handler: TestHandler = handler
        self.build()

    def build(self):
        self.grid_columnconfigure(1, weight=1)

        name_lbl = tk.Label(self, text="Name:", anchor="e")
        name_lbl.grid(row=0, column=0, sticky="ew")
        name_ent = tk.Entry(self, textvariable=self.handler.test.name)
        name_ent.grid(row=0, column=1, sticky="ew")

        matr_lbl = tk.Label(self, text="Material:", anchor="e")
        matr_lbl.grid(row=1, column=0, sticky="ew")
        matr_ent = tk.Entry(self, textvariable=self.handler.test.material)
        matr_ent.grid(row=1, column=1, sticky="ew")

        freq_lbl = tk.Label(self, text="Frequency:", anchor="e")
        freq_lbl.grid(row=2, column=0, sticky="ew")
        freq_ent = tk.Entry(self, textvariable=self.handler.test.freq)
        freq_ent.grid(row=2, column=1, sticky="ew")

        notes_lbl = tk.Label(self, text="Notes:", anchor="e")
        notes_lbl.grid(row=3, column=0, sticky="ew")
        notes_ent = tk.Entry(self, textvariable=self.handler.test.notes)
        notes_ent.grid(row=3, column=1, sticky="ew")


class TestControls(tk.Frame):
    def __init__(self, parent: tk.Widget, handler: TestHandler):
        super().__init__(parent)
        self.handler: TestHandler = handler
        self.build()

    def build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.start_btn = tk.Button(self)
        self.start_btn.configure(text="Start", state="normal", command=self.handler.start_test)
        self.start_btn.grid(row=0, column=0, sticky="ew")

        self.stop = tk.Button(self)
        self.stop.configure(text="Stop", state="disabled", command=self.handler.stop_test)
        self.stop.grid(row=0, column=1, sticky="ew")

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


class StrainPlot(tk.Frame):
    def __init__(self, parent: tk.Frame, handler: TestHandler):
        super().__init__(parent)
        self.handler = handler
        self.build()

    def build(self):
        self.fig, (self.strainplt, self.strainrateplt) = plt.subplots(
            2,
            figsize=(15, 8),
            dpi=100,
            constrained_layout=True,
            subplotpars=SubplotParams(left=0.5, bottom=0.1, right=0.95, top=0.95),
            sharex=True,
        )

        self.strainplt.set_ylabel("Strain")
        self.strainplt.grid(color="darkgrey", alpha=0.65, linestyle="")
        self.strainplt.set_facecolor("w")
        self.strainrateplt.set_xlabel("Time (s)")
        self.strainrateplt.set_ylabel("Strain Rate")
        self.strainrateplt.grid(color="darkgrey", alpha=0.65, linestyle="")
        self.strainrateplt.set_facecolor("w")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.fig.canvas.mpl_connect('scroll_event', self.zoom)

### part that zooms ###
    def zoom(self, event):
        if event.button == 'up':
            scale_factor = 1.1
        elif event.button == 'down':
            scale_factor = 0.9
        else:
            scale_factor = 1.0

        xdata, ydata = event.xdata, event.ydata
        self.strainplt.set_xlim(xdata - 0.5 * scale_factor, xdata + 0.5 * scale_factor)
        self.strainrateplt.set_xlim(xdata - 0.5 * scale_factor, xdata + 0.5 * scale_factor)

        self.canvas.draw()


class MainFrame(tk.Frame):
    def __init__(self, parent: tk.Frame):
        super().__init__(parent)

        self.parent: tk.Frame = parent
        self.handler = TestHandler()
        self.strainplot: StrainPlot = None
        self.build()

    def build(self):
        self.grid_columnconfigure(0, weight=1)

        test_info = TestInfoEntry(self, self.handler)
        test_info.grid(row=0, column=0, sticky="new")

        test_controls = TestControls(self, self.handler)
        test_controls.grid(row=1, column=0, sticky="nsew")

        plt_frm = tk.Frame(self)
        self.strainplot = StrainPlot(plt_frm, self.handler)
        self.strainplot.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        plt_frm.grid(row=0, column=1, rowspan=2)


class StrainApp(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        parent.resizable(0, 0)
        parent.tk_setPalette(background="#FAFAFA")

        self.winfo_toplevel().protocol("WM_DELETE_WINDOW", self.close)

        MainFrame(self).grid()

    def close(self) -> None:
        self.quit()


def main():
    root = tk.Tk()
    StrainApp.ROOT = root
    StrainApp(root).grid()
    root.mainloop()


if __name__ == "__main__":
    main()
