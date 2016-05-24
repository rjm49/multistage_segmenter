'''
Created on 30 Nov 2015

@author: Russell
'''

import os

from common import read_file, DIR, \
    save_symbol_table, JOINT_CV_SLM_FILE_GLOBAL, \
    SLM_FST_FILE_GLOBAL, JOINT_LM_CV_SLM_FILE_GLOBAL, \
    CONV_FST, LM_SYM_FILE, PROSODIC_PREDICTION_FILE, SYM_FILE, \
    LM_PRUNED, TRAIN_FILE_DEFAULT, TEST_FILE_DEFAULT
from lm_gen import fstcompose, compile_lm, \
    fstarcsort, generate_normed_text_file, ngramshrink
from pm.pm_utils import compile_pm_files, \
    generate_pm_text_files
from slm.slm_utils import create_converter, generate_slm
import sys
import json
import shutil

if __name__ == '__main__':

    print "Number of arguments:", len(sys.argv), 'arguments.'
    print "Argument List:", str(sys.argv)
    args = sys.argv

#     config = None
#     with open('sample_config.cfg') as data_file:    
#         config = json.load(data_file)

if len(args)>1: 
    batch_name = args[1]
    base_dir = args[2]
    pm_dir = args[3]
    lm_dir = args[4]
    slm_dir = args[5]
    tr_file = args[6]
    te_file = args[7]
else:
    batch_name = "default"
    base_dir = DIR
#     pm_dir = "pm_default" currently not used
    lm_dir = "eval1n_tr" #lm_default"
    slm_dir = "eval1n_tr"  #"slm_default"
    tr_file = TRAIN_FILE_DEFAULT
    te_file = TEST_FILE_DEFAULT

    lm_dir= raw_input("enter LM name: [%s]" % lm_dir) or lm_dir
    tr_file = raw_input("enter LM training file name: [%s]" % tr_file) or tr_file
    te_file = raw_input("enter target test file name (for symbols): [%s]" % te_file) or te_file

    #SECTION ONE: dedicated to creating the Language Model files    
    lmdir_global = os.path.join(base_dir, lm_dir)
#     if(os.path.exists(lmdir_global)):
#         shutil.rmtree(lmdir_global)
#     os.makedirs(lmdir_global)

    tr_rows = read_file(os.path.join(base_dir, tr_file), ',', skip_header=True)
    te_rows = read_file(os.path.join(base_dir, te_file), ',', skip_header=True)
    lm_syms = set([r[5] for r in tr_rows])
    all_syms = set([r[5] for r in tr_rows+te_rows])
    
    save_symbol_table(lm_syms, os.path.join(lmdir_global, LM_SYM_FILE))
    save_symbol_table(all_syms, os.path.join(base_dir, SYM_FILE))
    
    rawtext_file = generate_normed_text_file(tr_rows, lmdir_global)

    buildmod = "y"
    modfile = os.path.join(lmdir_global,"lm.mod")
    modpru = os.path.join(lmdir_global,LM_PRUNED)
    
    print "checking for LM file",modfile
    if(os.path.exists(modfile)):
        buildmod = raw_input("model file in "+lmdir_global+" already exists.  Overwrite? [n]").lower() or "n"
    
    if(not buildmod=="n"):
        modfile = compile_lm(rawtext_file, lmdir_global)
        print "Created unpruned lang model file:", modfile
        print "Now pruning LM..."
        ngramshrink(modfile, modpru)
        #we don't use the unpruned modfile again, so switch over to the pruned version here
        modfile = modpru
        
    create_converter(lmdir_global)
    print "created converter."
    
    slm_dir = raw_input("Type in SLM dir or hit return to use default [%s]" % slm_dir) or slm_dir
    slm_dir = os.path.join(base_dir,slm_dir)
        
    print "using ",slm_dir

    generate_slm(tr_rows, slm_dir, do_plot=False) # build the sentence length model, plot it so we can see it's sane
    print "slm generated from", tr_file, "in", slm_dir
    
    print "all constituent system files now compiled"