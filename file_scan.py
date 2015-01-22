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
import subprocess
import time


HEADER = "#"*30+"\n" # header line
DAYS_OLD = 6 * 30
# note: we can use "find {{dir}}* -atime +30" to get files not accessed for 30 days

iwd = os.curdir

def find_old_files(directory):
    """
    return a list of files in the given directory that have not been accessed
    in the time specified by DAYS_OLD
    """
    
    # go to the directory
    os.chdir(directory)
    
    # construct the find command to interogate the directory
    find_cmd = ["find"]
    find_cmd.append("*")
    find_cmd.append("-atime")
    find_cmd.append("+"+str(DAYS_OLD))
    # print("find command: "+" ".join(find_cmd)+"\n")
    
    # run the find command
    try:
        find = subprocess.Popen(" ".join(find_cmd),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    except:
        raise
    # get the standard output
    out, err = find.communicate() # get the standard output
    found = out.decode().split() # split the text into a list
    
    # go back to our starting directory 
    os.chdir(iwd)
        
    return(found)

def get_report_string(directory):
    """
    returns a report string for the directory passed to it
    """
    result = "##### file_scan.py Report\n"
    result += "##### "+datetime.datetime.now().ctime()+"\n"
    
    # get list of old unused files
    old = find_old_files(directory)

    result += HEADER+"#### files not accessed in "+str(DAYS_OLD)+" days\n"
    result += "\n".join(old)+"\n"
    return(result)

if __name__ == "__main__":
    print(get_report_string())
