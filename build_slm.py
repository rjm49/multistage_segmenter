'''
Created on 30 Nov 2015

@author: Russell
'''
from multistage_segmenter.common import EVAL1_FILE_NORMED, read_file, DIR, \
    PILOT_FILE_NORMED, save_symbol_table, PM_SUB_DIR, JOINT_CV_SLM_FILE_GLOBAL,\
    SLM_FST_FILE_GLOBAL, JOINT_LM_CV_SLM_FILE_GLOBAL,\
    CONV_FST, LM_SYM_FILE, PROSODIC_PREDICTION_FILE, SYM_FILE,\
    LM_PRUNED
import os
import string
from multistage_segmenter.lm_gen import fstcompose, compile_lm,\
    fstarcsort, generate_normed_text_file, ngramshrink
from multistage_segmenter.pm.pm_utils import compile_pm_files,\
    generate_pm_text_files, generate_pm_text_files
from multistage_segmenter.slm.slm_utils import generate_slm,\
    create_converter
import glob
import sys


gen_ntxt = False
tr_file, lmdir = EVAL1_FILE_NORMED, "eval1n"

if __name__ == '__main__':
        
    lmdir = raw_input("Type in LM dir or hit return to use default [%s]" % lmdir) or lmdir
    print "using ",lmdir
    lmdir_global = os.path.join(DIR,lmdir)
    
    tr_file = raw_input("enter training file name: [%s]" % tr_file) or tr_file
    
    tr_rows = read_file(os.path.join(DIR, tr_file), ',', skip_header=True)

    generate_slm(tr_rows, lmdir_global, do_plot=True) # build the sentence length model, plot it so we can see it's sane
    print "slm generated from", tr_file, "in", lmdir_global
