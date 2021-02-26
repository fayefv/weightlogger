import tkinter as tk
from functools import partial
import tkinter.font as font
import logger as lg
import csv

# a global variable to collect new data until ready to commit to CSV
logdict = []
master = tk.Tk()


# Collects new data in list of dicts
def submit_handler(e1, e2):
    date_recorded = e1.get()
    weight = e2.get()

    # handles empty entry case
    if date_recorded != "" and weight != "":

        # add input validation here

        logdict.append({"date": date_recorded, "weight in lbs": weight})
        # clears the entry text
        e1.delete(0, "end")
        e2.delete(0, "end")


def write_new_data():
    # add input validation

    # setup a CSV writer
    filename = "GUI_weightLog.csv"
    fields = ["date", "weight in lbs"]
    with open(filename, 'a+', newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writerows(logdict)


# there should be a view graph button that fires new data and generates graph
def show_graph():
    write_new_data()
    lg.show_log("GUI_weightLog.csv")

def custom_quit():

    master.quit()
    # how to close matplotlib window simultaneously
    # there are two loops happening
    # so presently requires two button clicks on quit to close all


def create_entry_window():

    master.geometry("+200+1000")
    master.title("WeightLogger GUI")

    # creates entry fields for user data
    tk.Label(master, text="Date", font=("Arial", 25)).grid(row=0)
    tk.Label(master, text="Weight (lbs)", font=("Arial", 25)).grid(row=1)
    e1 = tk.Entry(master, font=("Arial", 20))
    e2 = tk.Entry(master, font=("Arial", 20))
    e1.grid(row=0, column=1, padx=30, pady=10, ipady=10)
    e2.grid(row=1, column=1, padx=30, pady=10, ipady=10)

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
              command=partial(submit_handler, e1, e2)).grid(row=3,
                                                            column=1,
                                                            sticky=tk.W,
                                                            pady=10,
                                                            padx=100)
    # show button to plot updated graph
    tk.Button(master,
              text='Show',
              font=button_style,
              command=show_graph).grid(row=4,
                                       column=1,
                                       sticky=tk.W,
                                       pady=10,
                                       padx=100)

    master.mainloop()


if __name__ == '__main__':
    create_entry_window()
