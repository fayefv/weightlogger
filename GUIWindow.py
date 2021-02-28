"""A GUI version of WeightLogger application.

@author fayefong

TODO bind widget events appropriately
"""
import tkinter as tk
from tkcalendar import Calendar, DateEntry
import tkinter.font as font
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker
import controller as ct


# from functools import partial
# import logger as lg
# import csv

# from datetime import date, datetime
# import matplotlib
# import matplotlib.dates as mdates
# from matplotlib.dates import DateFormatter
# import os
# matplotlib.use("TkAgg")


class App(tk.Tk):
    def __init__(self):  # widgets are attributes of the class
        super().__init__()
        self.l1 = tk.Label(self, text="Date", font=("Arial", 25)).grid(row=0)
        self.l2 = tk.Label(self, text="Weight (lbs)", font=("Arial", 25)).grid(row=1)

        self.cal = DateEntry(self, year=2021, font=("Arial", 20))  # returns a str (M/D/YY)
        self.cal.grid(row=0, column=1, padx=30, pady=10, ipady=10)

        self.e_w = tk.Entry(self, font=("Arial", 20))
        self.e_w.grid(row=1, column=1, padx=30, pady=10, ipady=10)

        button_style = font.Font(family="Arial", size=25, weight='bold')
        self.quit_btn = tk.Button(self, text="Quit", font=button_style, command=self.quit)
        self.quit_btn.grid(row=3, column=0, sticky=tk.W, pady=10, padx=100)
        self.submit_btn = tk.Button(self, text="Submit", font=button_style, command=self.submit_handler)
        self.submit_btn.grid(row=3, column=1, sticky=tk.W, pady=10, padx=100)
        self.plot_btn = tk.Button(self, text="Plot", font=button_style, command=self.update_graph)
        self.plot_btn.grid(row=4, column=1, sticky=tk.W, pady=10, padx=100)
        self.report_btn = tk.Button(self, text='Send Report', font=button_style, command=self.send_report)
        self.report_btn.grid(row=4, column=0, sticky=tk.W, pady=10, padx=100)

        # embed empty plot for startup view
        self.figure = Figure(figsize=(9, 8), dpi=100)
        self.plt = self.figure.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=15, padx=5, pady=5)
        self.plt.xaxis.set_major_locator(ticker.NullLocator())
        self.plt.yaxis.set_major_locator(ticker.NullLocator())
        self.plt.set_title("Weight Change over Time")

    def submit_handler(self):
        date_sel = self.cal.get_date().strftime('%b-%d-%Y')
        weight_ent = self.e_w.get()
        self.e_w.config(fg=ct.submit_handler(date_sel, weight_ent))  # grey out text when new value submitted

    def update_graph(self):
        print("plot button clicked")

    def send_report(self):
        ct.email_report()


if __name__ == '__main__':
    app = App()
    app.geometry("+200+800")
    app.title("WeightLogger")
    app.mainloop()
