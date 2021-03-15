"""This module defines the controller functions for weightlogger app.

@author fayefong
"""
import tkfilebrowser
import tkinter as tk
import csv
import os
import pathlib
import platform
import subprocess
import shutil
from enum import Enum
from datetime import datetime
import weightlogger.constant as const


class ViewMode(Enum):
    """Enumerates allowed view modes for data.

    Presently, data may be viewed over all-time or over the previous week.

    """
    ALL_TIME = 1
    WEEK = 2


def calc_trend(**kwargs):
    """Calculates useful statistics. May be expanded for more sophisticated stats.

    Args:
        **kwargs: optional date range to calculate stats over, may specify start and end dates

    Returns: difference between weight over specified date range

    """
    x, y = get_records(**kwargs)
    return y[len(y) - 1] - y[0] if len(y) > 1 else const.NOTRENDFLAG  # Not enough data to calculate trend


def get_records(**kwargs):
    """Gets the chronologically sorted records for a selected date range.

    Args:
        **kwargs: optional date range to get records, may specify start and end dates

    Returns: a list of dates and a list of corresponding weights that are sorted chronologically

    """
    d = {}
    try:  # handles log file not found case
        with open(const.LOGFILENAME, 'r') as csvfile:
            records = csv.reader(csvfile, delimiter=',')
            for row in records:  # grabs data from CSV and puts into k,v in dict
                d[datetime.strptime(row[0], '%b-%d-%Y')] = float(row[1])  # convert str to datetime objects
    except FileNotFoundError:
        with open(const.LOGFILENAME, 'w') as csv_file:
            return [], []

    selected_dates = d.keys()
    if len(kwargs) > 0:
        time_st = kwargs['start']
        time_end = kwargs['end']
        # filter for records within specified timerange
        selected_dates = [d for d in selected_dates if time_st <= d <= time_end]

    sorted_dates = sorted(selected_dates)  # returns sorted list of datetime keys
    sorted_weights = [d[k] for k in sorted_dates]

    return sorted_dates, sorted_weights


def submit_handler(date_recorded, weight):
    """Adds or modifies the weight recorded for a selected date.

    Args:
        date_recorded: selected date
        weight: weight recorded

    Returns: color str to grey out the weight entry box to indicate that the weight has been updated

    """
    if weight == "":  # entering an empty str deletes an existing record
        delete_record(date_recorded)
        return "grey"  # no visible effect but weightlogger module requires return color str

    try:  # validates weight input
        float(weight)

        if lookup_record(date_recorded) != "":  # modifies an existing record
            replace_value(date_recorded, weight)
        else:  # appends a new record
            write_new_data(date_recorded, weight)

        return "grey"  # greys out the text when new value is submitted
    except ValueError:
        tk.messagebox.showerror("Error", "Not a valid weight value.")  # warns user so they can try again


def delete_record(del_this_date):
    """Deletes the record for the selected date.

    Args:
        del_this_date: date selected for deletion

    """
    log = []
    with open(const.LOGFILENAME, 'r') as csvfile:
        records = csv.reader(csvfile, delimiter=',')
        for row in records:
            if row[0] != del_this_date:  # collects every row except the deletion date
                log.append({"date": row[0], "weight in lbs": row[1]})

    with open(const.LOGFILENAME, 'w', newline="") as csvfile:  # overwrites the log file
        writer = csv.DictWriter(csvfile, fieldnames=const.FIELDS)
        writer.writerows(log)


def lookup_record(date_str):
    """Gets the previously recorded weight for a selected date.

    Args:
        date_str: date of interest

    Returns: the previously recorded weight or the empty str if no record exists

    """
    # handles log file not found case
    try:
        csv_file = csv.reader(open(const.LOGFILENAME, 'r'), delimiter=',')
    except FileNotFoundError:
        with open(const.LOGFILENAME, 'w') as csv_file:
            return ""

    # handles empty log file case
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

    """
    log = []
    with open(const.LOGFILENAME, 'r') as csvfile:
        records = csv.reader(csvfile, delimiter=',')
        for row in records:
            d, w = row[0], row[1]  # unchanged values are collected in a new log
            if d == date:
                w = new_weight  # and the new value is also added, preserving order
            log.append({"date": d, "weight in lbs": w})

    # overwrites the csv with updated log
    with open(const.LOGFILENAME, 'w', newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=const.FIELDS)
        writer.writerows(log)


def write_new_data(date, weight):
    """Appends a new record (date, weight) to the csv.

    Args:
        date: date selected
        weight: weight recorded

    """
    with open(const.LOGFILENAME, 'a+', newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=const.FIELDS)
        writer.writerow({"date": date, "weight in lbs": weight})


def open_folder_dialog(path):
    """Opens file explorer.

    Args:
        path: specified directory

    """
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:  # Linux
        subprocess.Popen(["xdg-open", path])


def save_report():
    """Saves a copy of the fitness report to selected directory."""
    src_dir = pathlib.Path(__file__).parent / "data"
    src_files_raw = os.listdir(src_dir)  # gets the report files from data folder

    # opens dialog to choose a destination folder
    dest_dir = tkfilebrowser.askopendirname(initialdir=pathlib.Path.home(),
                                            title="Choose Directory to Save to...")
    if dest_dir == "":  # do nothing if user cancels
        return

    # make new report folder in chosen directory
    suffix = datetime.now().strftime("%Y%m%d_%H-%M-%S")
    dir_name = "Report_" + suffix  # ensures unique report name to prevent overwrite
    report_dir = os.path.join(dest_dir, dir_name)
    os.mkdir(path=report_dir)

    # copies files to new folder
    for f in src_files_raw:
        src_file = pathlib.Path(src_dir).joinpath(f)
        shutil.copy2(src_file, report_dir)

    # open new report folder
    open_folder_dialog(report_dir)
