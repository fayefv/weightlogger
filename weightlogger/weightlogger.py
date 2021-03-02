"""A simple WeightLogger application to track personal fitness.

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
from datetime import datetime, timedelta
from functools import partial
from controller import ViewMode
from PIL import Image, ImageTk


class App(tk.Tk):
    def __init__(self):  # widgets are attributes of the class
        super().__init__()
        # static labels
        self.l1 = tk.Label(self, text="Date", font=("Arial", 25)).grid(row=0, column=0, sticky=tk.E)
        self.l2 = tk.Label(self, text="Weight (lbs)", font=("Arial", 25)).grid(row=1, column=0, sticky=tk.E)
        self.trend = tk.Label(self, text="Trends", font=("Arial", 25)).grid(row=5, column=0)

        # trend report frame
        self.r_frame = tk.Frame(self)
        self.r_frame.grid(row=6, column=0, rowspan=5, columnspan=2, sticky=tk.N, ipadx=45)

        # create icons
        # load images
        load1 = Image.open("misc/redarrow.png")
        load2 = Image.open("misc/greenarrow.png")
        # resize images to fit
        resize1 = load1.resize((30,30), Image.ANTIALIAS)
        resize2 = load2.resize((30,30), Image.ANTIALIAS)
        self.red_arr_img = ImageTk.PhotoImage(resize1)
        self.green_arr_img = ImageTk.PhotoImage(resize2)

        # make report widgets
        self.all_icon = tk.Label(self.r_frame)
        self.week_icon = tk.Label(self.r_frame)
        self.all_trend = tk.Label(self.r_frame, text=self.get_trend(ViewMode.ALL_TIME),
                                  font=("Arial", 25))
        self.week_trend = tk.Label(self.r_frame, text=self.get_trend(ViewMode.WEEK),
                                   font=("Arial", 25))
        self.l3 = tk.Label(self.r_frame, text="Overall: ", font=("Arial", 25))
        self.l4 = tk.Label(self.r_frame, text="Last Week: ", font=("Arial", 25))

        # finish rendering
        # image=self.green_arr_img or self.red_arr_img
        # image=self.green_arr_img or self.red_arr_img
        # self.all_icon.image= self.green_arr_img or self.red_arr_img
        # self.week_icon.image= self.green_arr_img or self.red_arr_img

        # layout report widgets in report frame
        self.l3.grid(row=0, column=0, sticky=tk.E, padx=10, pady=10)
        self.l4.grid(row=1, column=0, sticky=tk.E, padx=10, pady=10)
        self.all_trend.grid(row=0, column=2)
        self.week_trend.grid(row=1, column=2)
        # layout icons in the report frame
        self.all_icon.grid(row=0, column=1, padx=15)
        self.week_icon.grid(row=1, column=1, padx=15)

        # calendar drop down menu
        self.cal = DateEntry(self, font=("Arial", 20), width=8)  # returns a str (M/D/YY)
        self.cal.grid(row=0, column=1, padx=30, pady=10, ipady=10, sticky=tk.W)
        self.cal.bind("<<DateEntrySelected>>", self.fill_next)  # binds date selected to fill entry with record

        # weight entry
        self.e_w = tk.Entry(self, font=("Arial", 20), width=8)
        self.e_w.grid(row=1, column=1, padx=30, pady=10, ipady=10, sticky=tk.W)
        # on startup, autofill today's date and weight
        self.auto_fill()
        # bind keypress events for intuitive data entry
        self.e_w.bind("<Key>", self.handle_keypress)

        # actions that do not modify log
        button_style = font.Font(family="Arial", size=25, weight='bold')
        self.quit_btn = tk.Button(self, text="Quit", font=button_style, command=self.quit)
        self.quit_btn.grid(row=2, column=0, pady=10, padx=50, ipadx=20, ipady=10)

        self.report_btn = tk.Button(self, text='Report', font=button_style, command=self.send_report)
        self.report_btn.grid(row=3, column=0, pady=10, padx=50, ipady=10)

        # actions that modify log
        self.submit_btn = tk.Button(self, text="Submit", font=button_style, command=self.submit_handler)
        self.submit_btn.grid(row=2, column=1, pady=10, padx=30, sticky=tk.W, ipadx=50, ipady=10)

        # keep track of VIEWMODE
        self.mode = ViewMode.ALL_TIME  # set startup default to ALL_TIME

        # user is likely to write a new value in the entry and hit plot
        # clicking plot button should update the log and redraw the graph
        self.plot_btn = tk.Button(self, text="Plot", font=button_style,
                                  command=self.combine_funcs(self.submit_handler, self.show_graph))
        self.plot_btn.grid(row=3, column=1, pady=10, padx=30, sticky=tk.W, ipadx=75, ipady=10)

        # user can switch between all-time view or last week
        self.all_view_btn = tk.Button(self, text="All-Time", font=button_style)
        self.all_view_btn.config(fg='gray', bg='darkgray',
                                 activebackground='darkgray',
                                 activeforeground='gray')  # set startup default appearance to ALL-TIME
        self.all_view_btn.grid(row=16, column=6, pady=10, padx=0, sticky=tk.E, ipady=10)
        self.all_view_btn.bind("<Button-1>", self.view_handler)

        self.wk_view_btn = tk.Button(self, text="Week", font=button_style)

        self.wk_view_btn.grid(row=16, column=7, pady=10, padx=0, sticky=tk.W, ipady=10)
        self.wk_view_btn.bind("<Button-1>", self.view_handler)

        # embed an empty plot on startup
        self.initialize_graph()

        '''May change symbols from unicode to embedded images to make more robust against encoding differences
        however, these are pretty standard unicode characters with UTF-8 encoding, so it might be OK
        
        Embedded symbols also useful so that you can have custom character
        '''

    # need to bind trend reporting to all updates to CSV (Plot, Enter, Submit)
    def get_trend(self, range):
        today = datetime.today()
        delta = timedelta(weeks=1)
        lastweek = today - delta

        if range == ViewMode.ALL_TIME:
            val = ct.calc_trend()
            if (val < 0):  # weight loss
                # print("all time weight loss")
                self.all_icon.config(image=self.green_arr_img)
                self.all_icon.image=self.green_arr_img
            elif (val > 0):  # weight gain
                # print("weight gain")
                self.all_icon.config(image=self.red_arr_img)
                self.all_icon.image=self.red_arr_img
            else:
                self.all_icon.config(image="")
        elif range == ViewMode.WEEK:
            val = ct.calc_trend(start=lastweek, end=today)
            if (val < 0):  # weight loss
                # print("weekly weight loss")
                self.week_icon.config(image=self.green_arr_img)
                self.week_icon.image=self.green_arr_img
            elif (val > 0): # weight gain
                # print("weight gain")
                self.week_icon.config(image=self.red_arr_img)
                self.week_icon.image=self.red_arr_img
            else:
                self.week_icon.config(image="")

        return f'{val:+.1f}'

    def update_trend(self):
        self.all_trend.config(text=self.get_trend(ViewMode.ALL_TIME))
        self.week_trend.config(text=self.get_trend(ViewMode.WEEK))

    def view_handler(self, e):
        self.toggle_view(e)
        self.show_graph()

    """Toggles button view appearance but would benefit from actually changing the mode
    """

    def toggle_view(self, e):
        if e.widget.cget("text") == "All-Time":
            # sets the view mode
            self.mode = ViewMode.ALL_TIME
            # deactivate mouse over highlight
            # toggle button click
            self.all_view_btn.config(fg='gray', bg='darkgray',
                                     activebackground='darkgray',
                                     activeforeground='gray')
            self.wk_view_btn.config(fg='black', bg='lightgray',
                                    activebackground='lightgray',
                                    activeforeground='black')

        elif e.widget.cget("text") == "Week":

            self.mode = ViewMode.WEEK
            self.wk_view_btn.config(fg='gray', bg='darkgray',
                                    activebackground='darkgray',
                                    activeforeground='gray')
            self.all_view_btn.config(fg='black', bg='lightgray',
                                     activebackground='lightgray',
                                     activeforeground='black')

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
        self.e_w.config(fg='gray')
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

    def show_graph(self):
        self.set_up_graph()
        today = datetime.today()
        delta = timedelta(weeks=1)
        lastweek = today - delta
        if self.mode == ViewMode.WEEK:
            x, y = ct.get_records(start=lastweek, end=today)
        elif self.mode == ViewMode.ALL_TIME:
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
        self.update_trend()

    def send_report(self):
        ct.email_report()


if __name__ == '__main__':
    app = App()
    app.geometry("+200+800")
    app.title("WeightLogger")
    app.mainloop()
