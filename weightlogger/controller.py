"""Defines the controller functions for weightlogger app
@author fayefong
"""
import yagmail
import tkinter as tk
import csv
import os
from datetime import datetime
import constant as const
from enum import Enum
from datetime import datetime, timedelta

class ViewMode(Enum):
    ALL_TIME = 1
    WEEK = 2


def calc_trend(**kwargs):
    """Calculates useful statistics. May be expanded for more sophisticated stats.

    Args:
        **kwargs: select optional date range to calculate stats over

    Returns: difference between start weight and latest recorded weight

    """
    x, y = get_records(**kwargs)
    return y[len(y) - 1] - y[0]

def get_records(**kwargs):
    d = {}
    with open(const.LOGFILENAME, 'r') as csvfile:
        records = csv.reader(csvfile, delimiter=',')
        for row in records:  # grabs data from CSV and puts into k,v in dict
            d[datetime.strptime(row[0], '%b-%d-%Y')] = float(row[1])  # strs to datetime and float weights

    sorted_dates = sorted(d)  # returns sorted list of keys
    if len(kwargs) > 0:  # select dates within specified timerange
        time_st = kwargs['start']
        time_end = kwargs['end']
        sorted_dates = [d for d in sorted_dates if d >= time_st and d <= time_end]
    sorted_weights = [d[k] for k in sorted_dates]

    return sorted_dates, sorted_weights


"""Handles submit button clicks by appropriately modifying CSV file
"""


def submit_handler(d, w):
    date_recorded = d
    weight = w

    # deletes an existing record
    # makes more sense when you bind keypress event
    if weight == "":
        delete_record(date_recorded)
        return "grey"  # user will not see change but View code needs return color str

    try:  # validates weight input
        float(weight)

        if lookup_record(date_recorded) != "":  # modifies an existing record
            replace_value(date_recorded, weight)
        else:  # appends a new record to the csv
            # print("appended")
            write_new_data(date_recorded, weight)

        return "grey"  # greys out the text when new value is submitted
    except ValueError:
        tk.messagebox.showerror("Error", "Not a valid weight value.")  # do nothing so user can try again


"""Deletes a record from the csv
"""


def delete_record(del_this_date):
    log = []
    with open(const.LOGFILENAME, 'r') as csvfile:
        records = csv.reader(csvfile, delimiter=',')
        for row in records:
            if row[0] != del_this_date:  # collect every row except the deletion date
                log.append({"date": row[0], "weight in lbs": row[1]})

    with open(const.LOGFILENAME, 'w', newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=const.FIELDS)
        writer.writerows(log)


"""Looks up the weight for a specific date.
Used to populate entry box
And also to handle new submissions
"""


def lookup_record(date_str):
    # handles file not found case
    try:
        csv_file = csv.reader(open(const.LOGFILENAME, 'r'), delimiter=',')
    except FileNotFoundError:
        with open(const.LOGFILENAME, 'w') as csv_file:
            return ""

    # handles empty file case
    if os.stat(const.LOGFILENAME).st_size == 0:
        return ""

    for row in csv_file:
        if row[0] == date_str and row[1] != "":
            return row[1]  # returns current weight record for that date

    return ""  # returns empty str if date not found or missing weight

def replace_value(date, new_weight):
    """Replaces the previously recorded weight with a new measurement.

    Args:
        date: date selected
        new_weight: new weight

    Returns:

    """
    log = []
    with open(const.LOGFILENAME, 'r') as csvfile:
        records = csv.reader(csvfile, delimiter=',')
        for row in records:
            d, w = row[0], row[1]  # unchanged values are collected in a new log
            if d == date:
                w = new_weight  # and the new value is also added
            log.append({"date": d, "weight in lbs": w})

    # overwrites the csv with updated log
    with open(const.LOGFILENAME, 'w', newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=const.FIELDS)
        writer.writerows(log)

def write_new_data(d, w):
    """Appends a new record (date, weight) to the csv.

    Args:
        d: date selected
        w: weight recorded

    Returns:

    """
    with open(const.LOGFILENAME, 'a+', newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=const.FIELDS)
        writer.writerow({"date": d, "weight in lbs": w})

def email_report():
    """Emails png of latest plot to recipients

    Returns:

    """
    receiver = "fong.faye@gmail.com"
    body = "This message was generated automatically to" \
           " send you an updated report on Faye's weight loss journey. " \
           "Please see attached."
    filename = const.OUTPUTFILENAME

    # send email attachment of png figure
    yag = yagmail.SMTP("faye.vainsencher@gmail.com")
    yag.send(
        to=receiver,
        subject="AUTOGENERATED hotness report",
        contents=body,
        attachments=filename
    )
