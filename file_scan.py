#!/usr/bin/env python
"""
file_scan.py

Scans for file clutter such as redudant and old temp files

Todd Moughamer
Copyright 2015

January 18, 2015        Created

"""
import datetime
import os
import glob

HEADER = "#"*30+"\n" # header line
DAYS_OLD = 6 * 30
# note: we can use "find {{dir}}* -atime +30" to get files not accessed for 30 days

def find_old_files(directory):
    old_files = []
    return(old_files)

def get_report_string(directory):
    """
    returns a report string for the directory passed to it
    """
    result = "##### file_scan.py Report\n"
    result += "##### "+datetime.datetime.now().ctime()+" \n"
    
    # get list of old unused files
    old = find_old_files(directory)

    result += HEADER+"\n"+"#### files not accessed in "+str(DAYS_OLD)+" days"+"\n".join(old)+"\n"
    return(result)

if __name__ == "__main__":
    print(get_report_string())
