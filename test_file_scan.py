#!/usr/local/bin/python3

"""
test suite for file_scan. Creates some directories and files to interogate.

Todd Moughamer
Copyright 2015

January 18, 2015        Created

"""

import unittest
import tempfile
import os
import glob
import time
import datetime
import file_scan


EXP_REPORT_1 = """##### file_scan.py Report"""
### {{DATE AND TIME GO HERE}} ###
EXP_REPORT_2 = """
##############################
#### redundant content - identical md5sum
### 044c764d45303dc30f7ef356e2ecedf0
../same_content1.txt
../same_content2.txt
"""
EXP_REPORT_3 = """
##############################
#### potential compressed and uncompressed files
### foobar
### foobar.Z
### foobar.gz
### foobar.bz2
### foobar.tar
### foobar.tar.Z
### foobar.tar.gz
### foobar.tar.bz2

"""



class TestFileScan(unittest.TestCase):
    
    def setUp(self):
        """
        create some resrouces...
        ...a directory with some files
        ...files will cover various clutter scenarious
        ...a config file (proably)
        """
        
        date_of_report = datetime.datetime.now().ctime()
        # construct the example report...adding dynamic date (e.g., date)
        self.exp_report_txt = EXP_REPORT_1 +"\n"+"##### "+ date_of_report +EXP_REPORT_2
        
        # create a temporary directory that should disappear when we are done
        self.tdir = tempfile.TemporaryDirectory(prefix="test_file_scan")
        # create some files for scenarious
        #same_content_files = ["same_content1.txt", "same_content2.txt"]
        for fn in ["same_content1.txt", "samecontent2.txt"]:
            fh = open(self.tdir.name+"/"+fn,"w")
            fh.write("arbitrary content")
            fh.close()
        # prepare a files for a basename with typical compressed extension suffixs   
        self.uncomp_filename = "foobar"
        fh = open(self.tdir.name+"/"+"foobar","w")
        fh.close()
        for ext1 in ["","tar"]:
            suffixes = ['foobar']
            if ext1:
                suffixes.append(ext1)
            for ext2 in ["","Z","gz","bz2", "zip"]:
                if ext2:
                    if len(suffixes) == 3:
                        suffixes[2] == ext2
                    else:
                        suffixes.append(ext2)
                #print(str(full))
                print(".".join(suffixes))
                
        #print("You have one minute to check if files exist in "+self.tdir.name)
        #time.sleep(60)
        
        
    def test_report_text(self):
        """
        Verfiy the report text is what we expect.
        """
        obs_report = file_scan.get_report_string()
        self.assertEqual(obs_report, self.exp_report_txt)
    
    def tearDown(self):
        self.tdir.cleanup() # remove of temp directory
        
    
if __name__ == "__main__":
    unittest.main()
