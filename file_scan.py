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
import re

HEADER = "#"*30+"\n" # header line
DAYS_OLD = 6 * 30
# note: we can use "find {{dir}}* -atime +30" to get files not accessed for 30 days

iwd = os.getcwd()

def find_identical_files(directory):
    """
    return dict keyed by md5sum containing lists of files that share that
    md5sum value and almost certainly have identical content
    """
    # go to the directory
    os.chdir(directory)
    
    # Walk through directory
    #for dName, sdName, fList in os.walk(inDIR):
    #    for fileName in fList:
    #        if fnmatch.fnmatch(fileName, pattern): # Match search string
    #            fileList.append(os.path.join(dName, fileName))
    
    #find * -exec md5 '{}' \; # is the command that will essentially run md5 recursively
    
    # run the find command
    try:
        find = subprocess.Popen("find * -exec md5 '{}' \;",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    except:
        raise
    # get the standard output
    out, err = find.communicate() # get the standard output
    md5_results = out.decode().split("\n") # split the text into a list
    
    file_by_md5 = {}
    for f in md5_results:
        if f == '':
            continue
        p = re.split("\) = ",f)
        #print("Split returned "+str(p))
        if len(p) < 2:
            print("Failed to split "+f)
        fn = re.sub("MD5 \(","",p[0])
        if file_by_md5.__contains__(p[1]):
            file_by_md5[p[1]] += [ fn ]
        else:
            file_by_md5[p[1]] = [ fn ]
            
    identical = {}
    for md5 in file_by_md5.keys():
        if len(file_by_md5[md5]) == 1:
            continue
        identical[md5] = file_by_md5[md5]
    
    # go back to our starting directory 
    os.chdir(iwd)
    
    return(identical)

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
    
    # get list of old unused files - we have to do this first due to a flaw
    # in that the find/md5 command used to find identical files appears to
    # result the access time of files which old files uses
    old = find_old_files(directory)
    
    
    # get files with identical content
    result += HEADER+"#### redundant content - identical md5sum\n"
    identical = find_identical_files(directory)
    for md5 in identical.keys():
        mfiles = identical[md5]
        result += "### "+md5+"\n"
        result += "\n".join(mfiles)+"\n"

    result += HEADER+"#### files not accessed in "+str(DAYS_OLD)+" days\n"
    result += "\n".join(old)+"\n"
    return(result)

if __name__ == "__main__":
    print(get_report_string())
