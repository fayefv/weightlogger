"""A GUI version of WeightLogger application.

@author fayefong
"""
import tkinter as tk
from tkcalendar import Calendar, DateEntry
import tkinter.font as font
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker
import controller as ct
from matplotlib.dates import DateFormatter
import constant as const

class App(tk.Tk):
    def __init__(self):  # widgets are attributes of the class
        super().__init__()
        self.l1 = tk.Label(self, text="Date", font=("Arial", 25)).grid(row=0, column=0, sticky=tk.E)
        self.l2 = tk.Label(self, text="Weight (lbs)", font=("Arial", 25)).grid(row=1, column=0, sticky=tk.E)

        self.cal = DateEntry(self, font=("Arial", 20), width=8)  # returns a str (M/D/YY)
        self.cal.grid(row=0, column=1, padx=30, pady=10, ipady=10, sticky=tk.W )
        self.cal.bind("<<DateEntrySelected>>", self.fill_next)  # binds date selected to fill entry with record

        self.e_w = tk.Entry(self, font=("Arial", 20), width=8)
        self.e_w.grid(row=1, column=1, padx=30, pady=10, ipady=10, sticky=tk.W )
        # on startup, autofill today's date and weight
        self.auto_fill()
        # bind keypress events for intuitive data entry
        self.e_w.bind("<Key>", self.handle_keypress)

        button_style = font.Font(family="Arial", size=25, weight='bold')
        self.quit_btn = tk.Button(self, text="Quit", font=button_style, command=self.quit)
        self.quit_btn.grid(row=3, column=0, pady=10, padx=50, ipadx=20, ipady=10)

        self.report_btn = tk.Button(self, text='Report', font=button_style, command=self.send_report)
        self.report_btn.grid(row=4, column=0, pady=10, padx=50, ipady=10)

        self.submit_btn = tk.Button(self, text="Submit", font=button_style, command=self.submit_handler)
        self.submit_btn.grid(row=3, column=1, pady=10, padx=30, sticky=tk.W, ipadx=50, ipady=10)

        # user is likely to write a new value in the entry and hit plot
        # clicking plot button should update the log and redraw the graph
        # combine funcs and bind to plot button
        self.plot_btn = tk.Button(self, text="Plot", font=button_style,
                                  command=self.combine_funcs(self.submit_handler, self.show_graph))
        self.plot_btn.grid(row=4, column=1, pady=10, padx=30, sticky=tk.W, ipadx=75, ipady=10)



        # embed empty plot for startup view
        self.initialize_graph()

        '''May add user statistics report to Report function
            Average weight
            Variance
            Rate of weight loss over last week
        '''

    def combine_funcs(self, *funcs):
        def inner_combined_func(*args, **kwargs):
            for f in funcs:
                f(*args, **kwargs)

        # returning the reference of inner_combined_func
        # this reference will have the called result of all
        # the functions that are passed to the combined_funcs
        return inner_combined_func

    def handle_keypress(self, e):
        if e.char == '\r':  # log new weight when user hits <Enter>
            self.e_w.config(fg='grey')
            self.submit_handler()
            self.show_graph()
        else:  # switch font back to black to indicate active editing
            self.e_w.config(fg='black')  # when entry is changed, change text back to black

    def initialize_graph(self):
        self.set_up_graph();
        self.plt.xaxis.set_major_locator(ticker.NullLocator())  # turns off x, y labels and ticks
        self.plt.yaxis.set_major_locator(ticker.NullLocator())  # for cleaner startup view
        self.plt.set_title("Weight Change over Time")

    def auto_fill(self):  # general method to fill entry
        self.e_w.config(fg='black')
        lookup_date = self.cal.get_date().strftime('%b-%d-%Y')
        text = ct.lookup_record(lookup_date)
        self.e_w.delete(0, "end")
        if text != None:  # a valid record may be empty str but not null
            self.e_w.insert(0, text)

    def fill_next(self, e):  # wraps auto_fill so that for binding
        self.auto_fill()

    def set_up_graph(self):
        self.figure = Figure(figsize=(9, 8), dpi=100)
        self.plt = self.figure.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=15, columnspan=10, padx=5, pady=5)
        self.plt.set_title("Weight Change over Time")

    '''Desire to add additional view modes for all-time, just last week, or any duration
        Requires investigation for xrange of plotter
    '''
    def show_graph(self):
        self.set_up_graph()
        # since no more lazy loading of data entry
        # actually CSV file is always kept up to date
        x, y = ct.get_records()

        self.plt.plot(x, y, color='lightgray', marker='o', markerfacecolor='black')
        self.plt.set_xlabel('Date')
        self.plt.set_ylabel('Weight (lbs)')
        self.plt.set_autoscaley_on(False)
        self.plt.set_ylim([80.0, 125.0])
        self.plt.xaxis.set_major_locator(ticker.MaxNLocator(12))
        self.plt.xaxis.set_major_formatter(DateFormatter('%b-%d-%Y'))
        self.plt.tick_params(axis='x', labelrotation=25)

        # save graph as png
        img = self.plt.get_figure()
        img.savefig(const.OUTPUTFILENAME)

    def submit_handler(self):
        date_sel = self.cal.get_date().strftime('%b-%d-%Y')
        weight_ent = self.e_w.get()
        self.e_w.config(fg=ct.submit_handler(date_sel, weight_ent))  # grey out text when new value submitted

    def send_report(self):
        ct.email_report()


if __name__ == '__main__':
    app = App()
    app.geometry("+200+800")
    app.title("WeightLogger")
    app.mainloop()
