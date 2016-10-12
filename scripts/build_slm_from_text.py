#!/usr/bin/env python
'''
Created on 30 Nov 2015

@author: Russell
'''
import os

from mseg.common import TRAIN_FILE_DEFAULT, DIR, read_file
from mseg.slm_utils import generate_slm, generate_slm_from_txt

gen_ntxt = False
tr_fname, slm_dir = "normed.txt", "eval1n"

if __name__ == '__main__':
    slm_dir = raw_input("Type in SLM dir or hit return to use default [%s]" % slm_dir) or slm_dir
    slm_dir = os.path.join(DIR,slm_dir)
    
    print "using ",slm_dir
    
    tr_fname = raw_input("enter training file name: [%s]" % tr_fname) or tr_fname
    tr_file = open(os.path.join(slm_dir,tr_fname))
    tr_rows = tr_file.readlines()
    print len(tr_rows)
            
    generate_slm_from_txt(tr_rows, slm_dir, do_plot=True) # build the sentence length model, plot it so we can see it's sane
    print "slm generated from", tr_fname, "in", slm_dir
