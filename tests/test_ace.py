#!/usr/bin/env python
# File created on 27 Feb 2012
from __future__ import division

__author__ = "Morgan Langille"
__copyright__ = "Copyright 2011, The PICRUST project"
__credits__ = ["Morgan Langille"]
__license__ = "GPL"
__version__ = "1.4.0-dev"
__maintainer__ = "Morgan Langille"
__email__ = "morgan.g.i.langille@gmail.com"
__status__ = "Development"
 

from cogent.util.unit_test import TestCase, main
from picrust.ace import ace_for_picrust
from cogent.app.util import get_tmp_filename
from cogent.util.misc import remove_files
from cogent import LoadTable
from cogent.util.table import Table

class AceTests(TestCase):
    """ """
    
    def setUp(self):
        """ """
        #create a tmp tree file
        self.in_tree1_fp = get_tmp_filename(prefix='AceTests',suffix='.nwk')
        self.in_tree1_file = open(self.in_tree1_fp,'w')
        self.in_tree1_file.write(in_tree1)
        self.in_tree1_file.close()

        #create a tmp trait file
        self.in_trait1_fp = get_tmp_filename(prefix='AceTests',suffix='.tsv')
        self.in_trait1_file=open(self.in_trait1_fp,'w')
        self.in_trait1_file.write(in_trait1)
        self.in_trait1_file.close()

        self.files_to_remove = [self.in_tree1_fp,self.in_trait1_fp]

    def tearDown(self):
        remove_files(self.files_to_remove)
                       

    def test_ace_for_picrust_ml(self):
        """ test_ace_for_picrust with method 'ML' functions as expected with valid input
        """
        actual= ace_for_picrust(self.in_tree1_fp, self.in_trait1_fp, method="ML")
        expected=Table(['nodes','trait1','trait2'],[['14','2.9737','2.5436'],['12','2.3701','2.7056'],['11','0.8370','2.9706'],['10','4.4826','2.1388']])
        self.assertEqual(actual.tostring(),expected.tostring())
   

    def test_ace_for_picrust_pic(self):
        """ test_ace_for_picrust with method 'pic' functions as expected with valid input
        """
        actual= ace_for_picrust(self.in_tree1_fp,self.in_trait1_fp, method="pic")
        expected=Table(['nodes','trait1','trait2'],[['14','2.9737','2.5436'],['12','1.2727','3'],['11','0.6667','3'],['10','5','2']])
        self.assertEqual(actual.tostring(),expected.tostring())

in_tree1="""(((1:0.1,2:0.2)11:0.6,3:0.8)12:0.2,(4:0.3,D:0.4)10:0.5)14;"""

in_trait1="""tips	trait1	trait2
1	1	3
2	0	3
3	2	3
4	5	2
D	5	2"""

if __name__ == "__main__":
    main()