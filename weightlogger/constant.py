"""Global constants for the app
"""
import pathlib

LOGFILENAME = pathlib.Path(__file__).parent / "data/weightlog.csv"
FIELDS = ["date", "weight in lbs"]
GRAPH_FILENAME = pathlib.Path(__file__).parent / "data/weightlog.png"
NOTRENDFLAG = 10000
