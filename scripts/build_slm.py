#!/usr/bin/env python
'''
Created on 30 Nov 2015

@author: Russell
'''
import os

from mseg.common import TRAIN_FILE_DEFAULT, DIR, read_file
from mseg.slm_utils import generate_slm

gen_ntxt = False
tr_file, slm_dir = TRAIN_FILE_DEFAULT, "eval1n"

if __name__ == '__main__':
    slm_dir = raw_input("Type in SLM dir or hit return to use default [%s]" % slm_dir) or slm_dir
    slm_dir = os.path.join(DIR,slm_dir)
    
    print "using ",slm_dir
    
    tr_file = raw_input("enter training file name: [%s]" % tr_file) or tr_file
    tr_rows = read_file(os.path.join(DIR, tr_file), ',', skip_header=True)
    generate_slm(tr_rows, slm_dir, do_plot=True) # build the sentence length model, plot it so we can see it's sane
    print "slm generated from", tr_file, "in", slm_dir
