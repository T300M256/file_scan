#!/usr/bin/env python

"""
test suite for file_scan. Creates some directories and files to interogate.

Todd Moughamer
Copyright 2015

January 18, 2015        Created

February 1, 2015	Modified to work with Python 2.7.5 (mainly temp file stuff)

"""

import unittest
import tempfile
import os
import glob
import time
import datetime
from subprocess import call
import file_scan


EXP_REPORT_1 = """##### file_scan.py Report"""
### {{DATE AND TIME GO HERE}} ###
### /scanned/parent/dir/here ###
EXP_REPORT_2 = """
##############################
#### redundant content - identical md5sum
### 044c764d45303dc30f7ef356e2ecedf0
same_content1.txt
same_content2.txt
spam/same_content3.txt"""
EXP_REPORT_3 = """
##############################
#### potential compressed and uncompressed files
foobar
foobar.Z
foobar.bz2
foobar.gz
foobar.tar
foobar.tar.Z
foobar.tar.bz2
foobar.tar.gz
foobar.zip
spam/eggs
spam/eggs.Z
spam/eggs.bz2
spam/eggs.gz
spam/eggs.tar
spam/eggs.tar.Z
spam/eggs.tar.bz2
spam/eggs.tar.gz
spam/eggs.zip
##############################
#### files not accessed in 180 days
chalupa/batman.txt
christopher.foo
"""

EXP_CONFIG = """####################
### this is our example config file
access_time = 30 * 6 # about 6 months or 180 days
"""

#EXP_TIME_SPECS = {
#    "Jun  8 01:00:45 2013":"201306080100.45"
#}


class TestFileScan(unittest.TestCase):
    
    def setUp(self):
        """
        create some resrouces...
        ...a directory with some files
        ...files will cover various clutter scenarious
        ...a config file (proably)
        """
        
        self.maxDiff = None # so we can see long differences
        date_of_report = datetime.datetime.now().ctime()
        # construct the example report...adding dynamic date (e.g., date)
        self.exp_report_txt = EXP_REPORT_1 +"\n"+"##### "+ date_of_report +EXP_REPORT_2+EXP_REPORT_3        
        # create a temporary directory that should disappear when we are done
        #self.tdir = tempfile.TemporaryDirectory(prefix="test_file_scan")
        self.tdir = tempfile.mkdtemp(prefix='test_file_scan')
        #print(self.tdir)
	#sys.exit()
        # create some files for scenarious
        os.makedirs(self.tdir+"/"+"spam")
        for fn in ["same_content1.txt", "same_content2.txt", "spam/same_content3.txt"]:
            fh = open(self.tdir+"/"+fn,"w")
            fh.write("arbitrary content")
            fh.close()
        # prepare a files for a basename with typical compressed extension suffixs
        uniq_file_count = 0 # gives us a value for files we want to make unique content
        #self.uncomp_filename = "foobar"
        for base in ['foobar','spam/eggs']:
            fh = open(self.tdir+"/"+base,"w")
            fh.write(str(uniq_file_count))
            uniq_file_count += 1
            fh.close()
            for ext1 in ["","tar"]:
                suffixes = [base]
                if ext1:
                    suffixes.append(ext1)
                for ext2 in ["","Z","gz","bz2", "zip"]:
                    fn = ".".join(suffixes)
                    if ext2:
                        fn = fn + "." + ext2
                    if fn.__contains__(".tar.zip"):
                        continue # not expecting this combination
                    fh = open(self.tdir+"/"+fn,"w")
                    fh.write(str(uniq_file_count))
                    uniq_file_count += 1
                    fh.close()
        
        # try to make files for representing old files
        os.makedirs(self.tdir+"/"+"chalupa")
        for fn in ["chalupa/batman.txt", "christopher.foo"]:
            fh = open(self.tdir+"/"+fn,"w")
            fh.write(str(uniq_file_count))
            uniq_file_count += 1
            fh.close()
            # use the following command to make old access time stamps:
            # /usr/bin/touch -a -t 201312311200 foo.bar # date is noon on Dec 31 2013
            #retcall = call(["/usr/bin/touch","-a","-t","201312311200",self.tdir+"/"+fn])
            retcall = call(["/usr/bin/touch","-a","-t","201302021200",self.tdir+"/"+fn])
            if retcall != 0:
                print("failed to change access time for "+fn)
                sys.exit()
        #time.sleep(60)
        self.config_file = "config.py"
        #cf = open(self.config_file,"w")
        #cf.write(EXP_CONFIG)
        #cf.close()
        
        
    def test_report_text(self):
        """
        Verfiy the report text is what we expect.
        """
        obs_report = file_scan.get_report_string(self.tdir)
        #print(obs_report)
        
        self.assertEqual(obs_report, self.exp_report_txt)
        
    def testTimeSpec(self, ):
        """
        verifies that the time specification that is generated is what expected
        e.g., [[CC]YY]MMDDhhmm[.SS]]
        """
        #EXP_TIME_SPECS
        spec = file_scan.file_date_to_spec("Jun  8 01:00:45 2013")
        self.assertEqual("201306080100.45", spec)
        # Jan 25 22:07:30 2015 = 201501252207.30
        spec2 = file_scan.file_date_to_spec("Jan 25 22:07:30 2015")
        self.assertEqual("201501252207.30", spec2)
    
    
    def tearDown(self):
        #self.tdir.cleanup() # remove of temp directory
        #tfn = glob.glob(self.tdir+"/*")
        tfn = glob.glob(self.tdir+"/*/*")
        tfn += glob.glob(self.tdir+"/*")
        for fn in tfn:
            if os.path.isdir(fn):
                os.rmdir(fn)
            else:
                os.remove(fn)
        os.rmdir(self.tdir)
        #os.unlink(self.config_file)
    
if __name__ == "__main__":
    unittest.main()
