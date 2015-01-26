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

def find_comp_uncomp(directory):
    """
    Return a list or dict of files that contains lists of file that maybe
    co-existing compressed and uncompressed files based on shared base name
    and common compressed file extensions (.Z, .gz, .zip, .bz2) as well as
    the tar extension.
    """
    # go to the directory
    os.chdir(directory)
    
    # run a ls command to get a complete list of files under the directory (could walk but OS portablitly is not a goal)
    try:
        find = subprocess.Popen("find *",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    except:
        raise
    # get the standard output
    out, err = find.communicate() # get the standard output
    files = out.decode().split() # split the text into a list
    
    # all extensions to check will be held here
    exts = []
    
    # list of compressed extentions
    primary_exts = ['bz2','gz','zip','Z']
    
    # list of intermediary extenstions (e.g. tar)
    exts += primary_exts
    for e in primary_exts:
        exts.append("tar."+e)
    
    # add the singular tar compressed exstention
    exts.append("tgz")
    
    # create a pattern to search for files with extensions
    #pat = "$|(.+).".join(exts)
    pat = "$|".join(exts)
    pat += "$)"
    pat = "(.+)\.("+pat
    
    # 1 - go through the file list and pull out all files that end with one
    #     of the extensions in the list
    cmp_files = {}
    for fn in files:
        # search or fullmatch
        m = re.search(pat,fn)
        if m:
            # 2 - store the name of those files with the extension removed in a dict
            # look slike a compressed file
            prefix = m.groups()[0]
            
            if cmp_files.get(prefix):
                # append to list value
                cmp_files[prefix].append(fn)
            else:
                # create new list for value
                cmp_files[prefix] = [fn]
    
    # 3 - go through all the files and those that are present in the dict need
    #     to be captured as potentially redundant to the compressed version
    pos_red = []
    for fn in files:
        if cmp_files.get(fn):
            pos_red.append(fn)
            pos_red += cmp_files[fn]
    
    pos_red.sort()
    
    # Have to decide how to return them in a dict or just a list
    
    
    # go back to our starting directory 
    os.chdir(iwd)
    
    return(pos_red)

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
    
    # get potential compressed and compressed files
    compressed = find_comp_uncomp(directory)
    
    # get files with identical content
    identical = find_identical_files(directory)

    # prepare identical file report text
    result += HEADER+"#### redundant content - identical md5sum\n"
    for md5 in identical.keys():
        mfiles = identical[md5]
        result += "### "+md5+"\n"
        result += "\n".join(mfiles)+"\n"
   
    # prepare compressed/uncompressed report text
    result += HEADER+"#### potential compressed and uncompressed files\n"
    result += "\n".join(compressed)+"\n"
   
    # prepare old file report text
    result += HEADER+"#### files not accessed in "+str(DAYS_OLD)+" days\n"
    result += "\n".join(old)+"\n"
    return(result)

if __name__ == "__main__":
    print(get_report_string())
