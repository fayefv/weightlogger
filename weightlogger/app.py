"""A simple WeightLogger application to track personal fitness.

@author fayefong
"""
import tkinter as tk
from tkinter import filedialog
from tkcalendar import DateEntry
import tkinter.font as font
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker
from matplotlib.dates import DateFormatter
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import pathlib
import weightlogger.controller as ct
import weightlogger.constant as const
from weightlogger.controller import ViewMode


class App(tk.Tk):
    """GUI application window for data entry and plotting."""

    def __init__(self):  # widgets are attributes of the class
        super().__init__()

        # make empty directory for data
        pathlib.Path(__file__).parent.joinpath('data').mkdir(exist_ok=True)

        # sets commonly used time variables
        self.today = datetime.today()
        delta = timedelta(weeks=1)
        self.lastweek = self.today - delta

        # create static labels
        self.l1 = tk.Label(self, text="Date", font=("Arial", 25)).grid(row=0, column=0, sticky=tk.E)
        self.l2 = tk.Label(self, text="Weight (lbs)", font=("Arial", 25)).grid(row=1, column=0, sticky=tk.E)
        self.trend = tk.Label(self, text="Trends", font=("Arial", 25)).grid(row=5, column=0)

        # create trend report frame
        self.r_frame = tk.Frame(self)
        self.r_frame.grid(row=6, column=0, rowspan=5, columnspan=2, sticky=tk.N, ipadx=45)

        # create trend icons
        # load images
        load1 = Image.open(pathlib.Path(__file__).parent / "images/redarrow.png")
        load2 = Image.open(pathlib.Path(__file__).parent / "images/greenarrow.png")
        # resize images to fit
        resize1 = load1.resize((30, 30), Image.ANTIALIAS)
        resize2 = load2.resize((30, 30), Image.ANTIALIAS)
        self.red_arr_img = ImageTk.PhotoImage(resize1)
        self.green_arr_img = ImageTk.PhotoImage(resize2)

        # make trend report widgets
        self.all_icon = tk.Label(self.r_frame)
        self.week_icon = tk.Label(self.r_frame)
        self.all_trend = tk.Label(self.r_frame, text=self.set_trend(ViewMode.ALL_TIME),
                                  font=("Arial", 25))
        self.week_trend = tk.Label(self.r_frame, text=self.set_trend(ViewMode.WEEK),
                                   font=("Arial", 25))
        self.l3 = tk.Label(self.r_frame, text="Overall: ", font=("Arial", 25))
        self.l4 = tk.Label(self.r_frame, text="Last Week: ", font=("Arial", 25))

        # layout report widgets and icons in trend report frame
        self.l3.grid(row=0, column=0, sticky=tk.E, padx=10, pady=10)
        self.l4.grid(row=1, column=0, sticky=tk.E, padx=10, pady=10)
        self.all_trend.grid(row=0, column=2)
        self.week_trend.grid(row=1, column=2)
        self.all_icon.grid(row=0, column=1, padx=15)
        self.week_icon.grid(row=1, column=1, padx=15)

        # calendar drop-down menu for date selection or entry
        self.cal = DateEntry(self, font=("Arial", 20), width=8)  # returns a str (M/D/YY)
        self.cal.grid(row=0, column=1, padx=30, pady=10, ipady=10, sticky=tk.W)
        self.cal.bind("<<DateEntrySelected>>", self.fill_next)  # binds date selected to fill entry with record

        # weight entry box
        self.e_w = tk.Entry(self, font=("Arial", 20), width=8)
        self.e_w.grid(row=1, column=1, padx=30, pady=10, ipady=10, sticky=tk.W)
        # on startup, autofill today's date and weight
        self.auto_fill()
        # bind keypress events for intuitive data entry
        self.e_w.bind("<Key>", self.handle_keypress)

        # action buttons that do not modify log: "Quit", "Save"
        button_style = font.Font(family="Arial", size=25, weight='bold')
        self.quit_btn = tk.Button(self, text="Quit", font=button_style, command=self.quit)
        self.quit_btn.grid(row=2, column=0, pady=10, padx=50, ipadx=60, ipady=10)
        self.save_btn = tk.Button(self, text="Save", font=button_style, command=self.save_report)
        self.save_btn.grid(row=3, column=0, pady=10, padx=50, ipadx=55, ipady=10)

        # action buttons that modify log: "Submit", "Plot"
        self.submit_btn = tk.Button(self, text="Submit", font=button_style, command=self.submit_handler)
        self.submit_btn.grid(row=2, column=1, pady=10, padx=30, sticky=tk.W, ipadx=50, ipady=10)

        # keep track of plot VIEWMODE
        self.mode = ViewMode.ALL_TIME  # set startup default to ALL_TIME

        # user is likely to write a new value in the entry and hit plot
        # clicking plot button should update the log and redraw the graph
        self.plot_btn = tk.Button(self, text="Plot", font=button_style,
                                  command=self.combine_funcs(self.submit_handler, self.show_graph))
        self.plot_btn.grid(row=3, column=1, pady=10, padx=30, sticky=tk.W, ipadx=75, ipady=10)

        # user can switch between view modes: data over all-time view or last week
        self.all_view_btn = tk.Button(self, text="All-Time", font=button_style)
        self.all_view_btn.config(fg='gray', bg='darkgray',
                                 activebackground='darkgray',
                                 activeforeground='gray')  # startup default mode is ALL-TIME
        self.all_view_btn.grid(row=16, column=6, pady=10, padx=0, sticky=tk.E, ipady=10)
        self.all_view_btn.bind("<Button-1>", self.view_handler)
        self.wk_view_btn = tk.Button(self, text="Week", font=button_style)
        self.wk_view_btn.grid(row=16, column=7, pady=10, padx=0, sticky=tk.W, ipady=10)
        self.wk_view_btn.bind("<Button-1>", self.view_handler)

        # declare instance variables for plot
        self.figure = None
        self.plt = None
        self.canvas = None
        # embed an empty plot on startup
        self.initialize_graph()

    def set_up_graph(self):
        """Helper method to start boiler plate for a new embedded plot."""
        self.figure = Figure(figsize=(9, 8), dpi=100)
        self.plt = self.figure.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=15,
                                         columnspan=10, padx=5, pady=5)
        self.plt.set_title("Weight Change over Time")

    def initialize_graph(self):
        """Initializes startup view with an empty plot."""
        self.set_up_graph()
        self.plt.xaxis.set_major_locator(ticker.NullLocator())  # turns off x, y labels and ticks
        self.plt.yaxis.set_major_locator(ticker.NullLocator())  # for cleaner startup view
        self.plt.set_title("Weight Change over Time")

    def show_graph(self):
        """Plots data from a specified date range."""
        # set up a new embedded plot
        self.set_up_graph()

        x, y = [], []

        # get data from desired date range
        if self.mode == ViewMode.WEEK:
            x, y = ct.get_records(start=self.lastweek, end=self.today)
        elif self.mode == ViewMode.ALL_TIME:
            x, y = ct.get_records()

        # plot data and format graph
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
        img.savefig(const.GRAPH_FILENAME)

    def set_trend(self, date_range):
        """Creates the trend report.
        Calculates weight change over a date range and sets icons to indicate loss/gain.
        This method will be triggered after any change to the log csv.

        Args:
            date_range: date range of interest, only allowed to view over ALL TIME or previous WEEK

        Returns: weight change (to 1 decimal place)

        """
        val = None
        if date_range == ViewMode.ALL_TIME:
            val = ct.calc_trend()
            if val == const.NOTRENDFLAG:  # displays nothing when trend cannot be calculated
                self.all_icon.config(image="")
                return ""

            # sets the corresponding icon
            self.all_icon.config(image=self.green_arr_img if val < 0 else self.red_arr_img if val > 0 else "")
            self.all_icon.image = self.green_arr_img if val < 0 else self.red_arr_img if val > 0 else ""

        elif date_range == ViewMode.WEEK:
            val = ct.calc_trend(start=self.lastweek, end=self.today)
            if val == const.NOTRENDFLAG:  # displays nothing when trend cannot be calculated
                self.week_icon.config(image="")
                return ""

            # sets the corresponding icon
            self.week_icon.config(image=self.green_arr_img if val < 0 else self.red_arr_img if val > 0 else "")
            self.week_icon.image = self.green_arr_img if val < 0 else self.red_arr_img if val > 0 else ""

        return f'{val:+.1f}'

    def update_trend(self):
        """Updates the trend report."""
        self.all_trend.config(text=self.set_trend(ViewMode.ALL_TIME))
        self.week_trend.config(text=self.set_trend(ViewMode.WEEK))

    def view_handler(self, e):
        """Switches user view and plot between selected viewing modes.

        Args:
            e: <<Button-1>> click on the chosen view mode

        """
        self.toggle_view(e)  # configures the window to reflect the view mode
        self.show_graph()  # replots the graph

    def toggle_view(self, e):
        """Switches user view between different date range modes.

        Args:
            e: <<Button-1>> click on the chosen view mode

        """
        if e.widget.cget("text") == "All-Time":
            # sets the view mode to ALL TIME
            self.mode = ViewMode.ALL_TIME
            # deactivates mouse over highlight
            self.all_view_btn.config(fg='gray', bg='darkgray',
                                     activebackground='darkgray',
                                     activeforeground='gray')
            # toggle button selected appearance
            self.wk_view_btn.config(fg='black', bg='lightgray',
                                    activebackground='lightgray',
                                    activeforeground='black')

        elif e.widget.cget("text") == "Week":
            # sets the view mode to WEEK
            self.mode = ViewMode.WEEK
            # deactivates mouse over highlight
            self.wk_view_btn.config(fg='gray', bg='darkgray',
                                    activebackground='darkgray',
                                    activeforeground='gray')
            # toggle button selected appearance
            self.all_view_btn.config(fg='black', bg='lightgray',
                                     activebackground='lightgray',
                                     activeforeground='black')

    @staticmethod
    def combine_funcs(*funcs):
        """Utility wrapper method to allow binding two functions to button click
        Presently used to bind button click on "Plot" button to updating the log csv and re-plotting the graph.

        Args:
            *funcs: two or more funcs

        Returns: the reference of inner_combined_func
                which will have the called result of all
                the functions that are passed to the combined_funcs

        """

        def inner_combined_func(*args, **kwargs):
            for f in funcs:
                f(*args, **kwargs)

        return inner_combined_func

    def handle_keypress(self, e):
        """Binds <Enter> keypress to updating the log and the plot, then greys out
        the entry to indicate that the weight has been logged.
            All other keypresses are the user modifying the current record, so the font
            is returned to black to indicate active editing.

        Args:
            e: <KeyPress> event

        """
        if e.char == '\r':  # log new weight when user hits <Enter>
            self.e_w.config(fg='grey')
            self.submit_handler()
            self.show_graph()
        else:  # switch font back to black to indicate active editing
            self.e_w.config(fg='black')  # when entry is changed, change text back to black

    def auto_fill(self):
        """Populates the weight entry box with previously recorded data for selected date."""
        self.e_w.config(fg='gray')  # existing records appear greyed out
        lookup_date = self.cal.get_date().strftime('%b-%d-%Y')
        text = ct.lookup_record(lookup_date)
        self.e_w.delete(0, "end")
        self.e_w.insert(0, text)

    def fill_next(self, e):
        """Wrapper method for auto_fill() that accepts event arg, so that auto_fill() can be bound bound to DateEntry
        selection event.

        Args: <<DateEntrySelected>> event

        """
        self.auto_fill()

    def submit_handler(self):
        """Adds/deletes/modifies weight records for a specified date."""
        date_sel = self.cal.get_date().strftime('%b-%d-%Y')  # formats selected date (Jan-01-2010)
        weight_ent = self.e_w.get()
        self.e_w.config(fg=ct.submit_handler(date_sel, weight_ent))  # greys out text after new value submitted
        self.update_trend()  # recalculates statistics report based on new data

    @staticmethod
    def save_report():
        """Saves fitness report to a chosen folder."""
        ct.save_report()


if __name__ == '__main__':
    app = App()
    app.geometry("+200+800")
    app.title("WeightLogger")
    app.mainloop()
