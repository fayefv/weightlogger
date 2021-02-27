"""A GUI version of WeightLogger application.

@author fayefong

Next step is to autofill entry with previously recorded value
Then, add ability find and replace text in csv
----
Please advise on button handler where you pass references to the button, the window, etc
Seems brittle
And it seems like there's a more robust way to handle events with def def and event binding

"""
import tkinter as tk
from functools import partial
import tkinter.font as font
import logger as lg
import csv
from tkcalendar import Calendar, DateEntry
from datetime import date, datetime
import matplotlib
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.ticker as ticker

# a global variable to collect new data until ready to commit to CSV
logdict = []
master = tk.Tk()


# duplicate record handled by allowing revision of existing record
# regex search for the keys in the csv file


# Collects new data in list of dicts
def submit_handler(cal, e_w):
    # converts calendar entry to datetime object
    # for easy conversion to formatted string
    date_recorded = cal.get_date().strftime('%b-%d-%Y')
    weight = e_w.get()

    try:  # validates weight input
        float(weight)
        logdict.append({"date": date_recorded, "weight in lbs": weight})

        # could add a checkmark when submitted

        # greys out the text when submitted
        e_w.config(fg='grey')
    except ValueError:
        # print("Not a valid weight value.")
        tk.messagebox.showerror("Error", "Not a valid weight value.")
        # does nothing, so user can try again

def write_new_data():
    # add input validation

    # setup a CSV writer
    filename = "GUI_weightLog.csv"
    fields = ["date", "weight in lbs"]
    with open(filename, 'a+', newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writerows(logdict)


# there should be a view graph button that fires new data and generates graph
# def show_graph():
#     write_new_data()
#     logdict.clear()  # clears current logdict for new data entry
#     lg.show_log("GUI_weightLog.csv")


def custom_quit():
    master.quit()
    # how to close matplotlib window simultaneously
    # there are two loops happening
    # so presently requires two button clicks on quit to close all


# def create_entry_window():
#     master.geometry("+200+1000")
#     master.title("WeightLogger GUI")
#
#     # creates entry fields for user data
#     tk.Label(master, text="Date", font=("Arial", 25)).grid(row=0)
#     tk.Label(master, text="Weight (lbs)", font=("Arial", 25)).grid(row=1)
#     cal = DateEntry(master, year=2021, font=("Arial", 20), )  # gets a str (M/D/YY)
#     e_w = tk.Entry(master, font=("Arial", 20))
#
#     cal.grid(row=0, column=1, padx=30, pady=10, ipady=10)
#     e_w.grid(row=1, column=1, padx=30, pady=10, ipady=10)
#
#     # set default value to today's weight
#     today = cal.get_date().strftime('%b-%d-%Y')
#     setTextInput(e_w, lookup_record(today))
#
#     # creates action buttons
#     button_style = font.Font(family='Arial', size=25, weight='bold')
#     # quit button to end session
#     tk.Button(master,
#               text='Quit',
#               font=button_style,
#               command=custom_quit).grid(row=3,
#                                         column=0,
#                                         sticky=tk.W,
#                                         pady=10,
#                                         padx=100
#                                         )
#
#     # submit button to commit changes to weight log
#     tk.Button(master,
#               text='Submit',
#               font=button_style,
#               command=partial(submit_handler, cal, e_w)).grid(row=3,
#                                                               column=1,
#                                                               sticky=tk.W,
#                                                               pady=10,
#                                                               padx=100)
#
#
#
#     # show button to plot updated graph
#     tk.Button(master,
#               text='Plot',
#               font=button_style,
#               command=update_graph).grid(row=4,
#                                          column=1,
#                                          sticky=tk.W,
#                                          pady=10,
#                                          padx=100)
#
#     # embed a blank plot
#     figure = Figure(figsize=(9, 8), dpi=100)
#     plt = figure.add_subplot(1, 1, 1)
#     canvas = FigureCanvasTkAgg(figure, master)
#     canvas.get_tk_widget().grid(row=0, column=2, rowspan=15, padx=5, pady=5)
#     plt.xaxis.set_major_locator(ticker.NullLocator())
#     plt.yaxis.set_major_locator(ticker.NullLocator())
#     # plt.set_xlabel('Date')
#     # plt.set_ylabel('Weight (lbs)')
#     plt.set_title("Weight Change over Time")
#
#     master.mainloop()

def lookup_record(date_str):
    csv_file = csv.reader(open('GUI_weightLog.csv', 'r'), delimiter=',')

    for row in csv_file:
        if row[0] == date_str:
            return row[1]

def update_graph():

    write_new_data()
    logdict.clear()  # clears current logdict for new data entry

    # redraw the embedded graph
    figure = Figure(figsize=(9, 8), dpi=100)
    plt = figure.add_subplot(1, 1, 1)
    canvas = FigureCanvasTkAgg(figure, master)
    canvas.get_tk_widget().grid(row=0, column=2, rowspan=15, padx=5, pady=5)

    d = {}
    with open("GUI_weightLog.csv", 'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            d[row[0]] = float(row[1])

    # sort the dates by real time
    # so that (date, weight) is plotted chronologically
    sorted_dates = sorted(d, key=lambda date_k: datetime.strptime(date_k, '%b-%d-%Y'))


    # x = sorted(d, key=lambda date_k: datetime.strptime(date_k, '%b-%d-%Y'))
    # print(type(x))
    x = [datetime.strptime(s, '%b-%d-%Y') for s in sorted_dates]  # convert to datetime object
    y = [d[key] for key in sorted_dates]

    plt.plot(x, y, color='lightgray', marker='o', markerfacecolor='black')
    plt.set_xlabel('Date')
    plt.set_ylabel('Weight (lbs)')
    plt.set_title("Weight Change over Time")
    plt.set_autoscaley_on(False)
    plt.set_ylim([80.0, 125.0])
    plt.xaxis.set_major_locator(ticker.MaxNLocator(12))
    plt.xaxis.set_major_formatter(DateFormatter('%b-%d-%Y'))
    plt.tick_params(axis='x', labelrotation=25)

def setTextInput(e_w, text):
    e_w.delete(0, "end")
    e_w.insert(0, text)


if __name__ == '__main__':
    # create_entry_window()

    def print_sel(e): # define a function inside a function
        e_w.config(fg='black') # return weight entry text to black for new submission
        lookup_date = cal.get_date().strftime('%b-%d-%Y')
        text = lookup_record(lookup_date)
        e_w.delete(0, "end")
        if text != None:
            e_w.insert(0, text)



    master.geometry("+200+1000")
    master.title("WeightLogger GUI")

    # creates entry fields for user data
    tk.Label(master, text="Date", font=("Arial", 25)).grid(row=0)
    tk.Label(master, text="Weight (lbs)", font=("Arial", 25)).grid(row=1)
    cal = DateEntry(master, year=2021, font=("Arial", 20), )  # gets a str (M/D/YY)
    cal.bind("<<DateEntrySelected>>", print_sel)  # bind fill function to the <<CalenderSelected>> event
    e_w = tk.Entry(master, font=("Arial", 20))

    cal.grid(row=0, column=1, padx=30, pady=10, ipady=10)
    e_w.grid(row=1, column=1, padx=30, pady=10, ipady=10)

    # set default value to today's weight
    today = cal.get_date().strftime('%b-%d-%Y')
    setTextInput(e_w, lookup_record(today))

    # creates action buttons
    button_style = font.Font(family='Arial', size=25, weight='bold')
    # quit button to end session
    tk.Button(master,
              text='Quit',
              font=button_style,
              command=custom_quit).grid(row=3,
                                        column=0,
                                        sticky=tk.W,
                                        pady=10,
                                        padx=100
                                        )

    # submit button to commit changes to weight log
    tk.Button(master,
              text='Submit',
              font=button_style,
              command=partial(submit_handler, cal, e_w)).grid(row=3,
                                                              column=1,
                                                              sticky=tk.W,
                                                              pady=10,
                                                              padx=100)



    # show button to plot updated graph
    tk.Button(master,
              text='Plot',
              font=button_style,
              command=update_graph).grid(row=4,
                                         column=1,
                                         sticky=tk.W,
                                         pady=10,
                                         padx=100)

    # embed a blank plot
    figure = Figure(figsize=(9, 8), dpi=100)
    plt = figure.add_subplot(1, 1, 1)
    canvas = FigureCanvasTkAgg(figure, master)
    canvas.get_tk_widget().grid(row=0, column=2, rowspan=15, padx=5, pady=5)
    plt.xaxis.set_major_locator(ticker.NullLocator())
    plt.yaxis.set_major_locator(ticker.NullLocator())
    # plt.set_xlabel('Date')
    # plt.set_ylabel('Weight (lbs)')
    plt.set_title("Weight Change over Time")

    master.mainloop()
