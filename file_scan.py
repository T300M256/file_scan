#!/usr/bin/env python
"""
file_scan.py

Scans for file clutter such as redudant and old temp files

Todd Moughamer
Copyright 2015

January 18, 2015        Created

"""
import argparse
import datetime
import os
import subprocess
import re
import calendar
import sys

HEADER = "#"*30+"\n" # header line
DAYS_OLD = 6 * 30

iwd = os.getcwd()

def file_date_to_spec(fdate):
    """
    takes a string that is a date string from a stat command run on a file and
    returns a string that is a time specification that can be used by the touch
    command to change the time metadata for a file e.g.,:
    Jan 25 22:07:30 2015 = 201501252207.30
    """
    d = re.split("\s+",fdate)
    nd = ""
    nd += d[3]
    mnth = "{0:02d}".format(list(calendar.month_abbr).index(d[0]))
    nd = nd+mnth+"{0:02d}".format(int(d[1]))
    tim = re.sub(":","",d[2],1)
    tim = re.sub(":",".",tim,1)
    nd += tim
    return(nd)

def find_identical_files(directory):
    """
    return dict keyed by md5sum containing lists of files that share that
    md5sum value and almost certainly have identical content
    """
    # go to the directory
    os.chdir(directory)
    
    # the problem wiht the md5 in our scan is that it causes the access time to be
    # updated. This renders future scans of the directory when looking for old files
    # to see them no older than the last scan. An approach to get around this would
    # be to retrieve the access times for all the files using the stat command
    # then use touch reset the access time to the original. This may change other
    # time stats too need to look in that. Here is a command set example for
    # changing the access times using touch:

    # addressing access times
    
    # 1 - fetch all the previous accesstimes
    try:
        find_stat = subprocess.Popen("find * -exec stat '{}' \;",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    except:
        raise
    # get the standard output
    out, err = find_stat.communicate() # get the standard output
    fstats = out.decode().split("\n") # split the text into a list
    fdates = {}
    for s in fstats:
        # parse stat output lines appear as follows:
        #16777220 1001760 -rw-r--r-- 1 todd staff 0 7 "Jan 25 22:07:00 2015" "Jan 25 22:00:07 2015" "Jan 25 22:09:51 2015" "Jan 25 22:00:07 2015" 4096 8 0 bar.txt
        if s == "":
            continue
        at = re.search("\"[^\"]+\"",s).group(0)
        at = at.strip('"')
        dspec = file_date_to_spec(at)
        ss = s.split(" ")
        fn = " ".join(ss[27:])
        fdates[fn] = dspec
    

    # get the md5 sums for each file...the side effect is the access time changes...but we repair these    
    file_by_md5 = {}
    for fn in fdates.keys():
        
        # run md5 sum and get the value in a dict
        try:
            cmd_md5 = subprocess.Popen("md5 "+fn,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        except:
            raise
        out, err = cmd_md5.communicate() # get the standard output
        md5 = out.decode() # split the text into a list
        md5 = md5.rstrip()
        if md5 == '':
            continue
        p = re.split("\) = ",md5)
        if len(p) < 2:
            print("Failed to split "+f)
        fnn = re.sub("MD5 \(","",p[0])
        if fnn != fn:
            print("The file returned by md5 was not was not what was expected: "+fnn)
        if file_by_md5.__contains__(p[1]):
            file_by_md5[p[1]] += [ fn ]
        else:
            file_by_md5[p[1]] = [ fn ]
            
        # repair access time using touch command e.g.:
        # /usr/bin/touch -a -t 201501252207.30 bar.txt
        tch = "/usr/bin/touch -a -t "+fdates[fn]+" "+fn
        return_signal = subprocess.call(tch.split())
        if return_signal != 0:
            print("Could not run command "+tch)
            sys.exit()
  
    # create our dict of list of files keyed by md5 sums
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
    
    # get potential compressed and compressed files
    compressed = find_comp_uncomp(directory)
    
    # get files with identical content
    identical = find_identical_files(directory)

    # prepare identical file report text
    result += HEADER+"#### redundant content - identical md5sum\n"
    for md5 in identical.keys():
        mfiles = identical[md5]
        mfiles.sort()
        result += "### "+md5+"\n"
        result += "\n".join(mfiles)+"\n"
   
    # prepare compressed/uncompressed report text
    result += HEADER+"#### potential compressed and uncompressed files\n"
    result += "\n".join(compressed)+"\n"

    # get list of old unused files - we have to do this first due to a flaw
    # in that the find/md5 command used to find identical files appears to
    # result the access time of files which old files uses
    old = find_old_files(directory)
   
    # prepare old file report text
    result += HEADER+"#### files not accessed in "+str(DAYS_OLD)+" days\n"
    result += "\n".join(old)+"\n"
    return(result)

if __name__ == "__main__":
 
    parser = argparse.ArgumentParser(description='Traverses given directory and reports on clear and potential redundant files and files that are not being used')
    parser.add_argument("-d", "--directory", dest="dir", help="the directory to be scanned", required=True)
    args = parser.parse_args()
    
    print(get_report_string(args.dir))
