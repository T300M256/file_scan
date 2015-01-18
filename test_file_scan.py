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

class TestFileScan(unittest.TestCase):
    
    def setUp(self):
        """
        create some resrouces...
        ...a directory with some files
        ...files will cover various clutter scenarious
        ...a config file (proably)
        """
        # create a temporary directory that should disappear when we are done
        self.tdir = tempfile.TemporaryDirectory(prefix="test_file_scan")
        # create some files for scenarious
        #same_content_files = ["same_content1.txt", "same_content2.txt"]
        for fn in ["same_content1.txt", "samecontent2.txt"]:
            fh = open(self.tdir.name+"/"+fn,"w")
            fh.write("arbitrary content")
            fh.close()
        #print("You have one minute to check if files exist in "+self.tdir.name)
        #time.sleep(60)
        
        #os.unlink(os.path(tdir.name))
        
        
    def testFoo(self):
        pass
    
    def tearDown(self):
        self.tdir.cleanup() # remove of temp directory
        
    
if __name__ == "__main__":
    unittest.main()
