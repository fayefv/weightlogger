"""WeightLogger
@author fayefong
Date: 2-24-2021

This script simply tracks weight loss over time.
Progress visualized as a connected scatter plot.

The next step is to create a GitHub repository
"""
from datetime import date, datetime
import csv
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def log_weight():
    logdict = get_user_input()
    filename = "weightLog.csv"
    fields = ["date", "weight in lbs"]

    if os.path.exists(filename) is False:  # start a new log
        with open(filename, 'w') as csvfile:
            # creating a csv dict writer object
            writer = csv.DictWriter(csvfile, fieldnames=fields)

            # add dictionary as row in the csv
            writer.writerows(logdict)
    else:  # add to existing log
        with open(filename, 'a+', newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writerows(logdict)


def get_user_input():
    # populate list with existing entered dates
    list_of_dates = populate_date_list()

    logdict = []
    while True:
        date_recorded = input("Enter date ('Jan-01-2010') / hit 'ENTER' if today / 'x' to exit): ")

        # exit data entry
        if date_recorded.upper() == "X":
            break
        else:
            # easy log today's date
            if date_recorded == "":
                date_recorded = date.today().strftime("%b-%d-%Y")

            # check for duplicate date
            if date_recorded in list_of_dates:
                print("Error: duplicate date. Please try again.")
                continue

            # validate input format
            try:
                datetime.strptime(date_recorded, '%b-%d-%Y')
            except ValueError:
                print("Incorrect format, should be MMM-DD-YYYY")
                continue

        # finish taking data point
        weight = input("Enter weight: ")
        logdict.append({"date": date_recorded, "weight in lbs": weight})

    return logdict


def populate_date_list():
    list_of_dates = []
    with open("weightLog.csv", 'r') as csvfile:
        current_log = csv.reader(csvfile, delimiter=',')
        for entry in current_log:
            list_of_dates.append(entry[0])
    return list_of_dates


def show_log():
    d = {}
    with open('weightLog.csv', 'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            d[row[0]] = float(row[1])

    # sort the dates by real time
    # so that (date, weight) is plotted chronologically
    sorted_dates = sorted(d, key=lambda date_k: datetime.strptime(date_k, '%b-%d-%Y'))

    # plot data
    x = [datetime.strptime(s, '%b-%d-%Y') for s in sorted_dates]  # convert to datetime object
    y = [d[key] for key in sorted_dates]

    # format the plot to reflect real time progression
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b-%d-%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
    plt.gca().set_ylim([80.0, 125.0])
    plt.plot(x,y, color='lightgray', marker='o', markerfacecolor='black')
    plt.gcf().autofmt_xdate()
    plt.xlabel('Date')
    plt.ylabel('Weight (lbs)')
    plt.title("Weight Change over Time")
    plt.gcf().canvas.set_window_title('WeightLogger')
    plt.show()


if __name__ == '__main__':
    log_weight()
    show_log()
