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

def find_old_files(directory):
    
    
    #subprocess.Popen("find /Users/Todd/Downloads/ -atime +1", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #>>> (out2, err2) = find2.communicate()
    #>>> files2 = out2.decode().split()
    #>>> files2      
    
    find_cmd = ["find"]
    find_cmd.append(directory+"/*")
    find_cmd.append("-atime")
    find_cmd.append("+"+str(DAYS_OLD))
    
    print("find command: "+" ".join(find_cmd)+"\n") # what gets printed executes on the command line as expected
    
    #time.sleep(60)
    
    try:
        find = subprocess.Popen(" ".join(find_cmd),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        # might not need...universal_newlines=True
    except:
        raise
    
    out, err = find.communicate()
    
    found = out.decode().split()
    
    print("found:\n"+str(found))
    print("err:\n"+err.decode())
        
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
