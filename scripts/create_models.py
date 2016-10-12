'''
Created on 30 Nov 2015

@author: Russell
'''

import json
import os
import shutil
import sys

from mseg import lm_utils
from mseg.common import read_file, DIR, \
    save_symbol_table, JOINT_CV_SLM_FILE_GLOBAL, \
    SLM_FST_FILE_GLOBAL, JOINT_LM_CV_SLM_FILE_GLOBAL, \
    CONV_FST, LM_SYM_FILE, PROSODIC_PREDICTION_FILE, SYM_FILE, \
    LM_PRUNED, TRAIN_FILE_DEFAULT, TEST_FILE_DEFAULT, create_remap_table, BREAK, \
    UNK
from mseg.lm_utils import fstcompose, compile_lm, \
    fstarcsort, generate_normed_text_file, ngramshrink, remap_lm
from mseg.pm_utils import compile_pm_files, \
    generate_pm_text_files
from mseg.slm_utils import create_converter, generate_slm, generate_slm_from_txt

def main(argv):
    print "Number of arguments:", len(sys.argv), 'arguments.'
    print "Argument List:", str(sys.argv)

#     config = None
#     with open('sample_config.cfg') as data_file:    
#         config = json.load(data_file)


    base_dir = DIR
#     pm_dir = "pm_default" currently not used
    lm_dir = "eval1n_tr" #lm_default"
    tr_file = TRAIN_FILE_DEFAULT

    lm_dir= raw_input("enter LM name: [%s]" % lm_dir) or lm_dir
    tr_file = raw_input("enter LM training file name: [%s]" % tr_file) or tr_file
    ngo = int(raw_input("enter ngram order: [%s]" % 4) or 4)
    #te_file = raw_input("enter target test file name (for symbols): [%s]" % te_file) or te_file

    #SECTION ONE: dedicated to creating the Language Model files    
    lmdir_global = os.path.join(base_dir, lm_dir)
#     if(os.path.exists(lmdir_global)):
#         shutil.rmtree(lmdir_global)
#     os.makedirs(lmdir_global)

    tr_rows = read_file(os.path.join(base_dir, tr_file), ',', skip_header=True)

    rawtext_file = generate_normed_text_file(tr_rows, lmdir_global)
    
    #lm_syms = set([r[5] for r in tr_rows])
    
    lm_txt = open(rawtext_file, "r").readlines()
    lm_syms= set( open(rawtext_file, "r").read().split() )
    if BREAK in lm_syms: lm_syms.remove(BREAK)
    if UNK in lm_syms: lm_syms.remove(UNK)
    
    buildmod = "y"
    modfile = os.path.join(lmdir_global,"lm.mod")
    modpru = os.path.join(lmdir_global,LM_PRUNED)
    
    print "checking for LM file",modfile
    if(os.path.exists(modfile)):
        buildmod = raw_input("model file in "+lmdir_global+" already exists.  Overwrite? [n]").lower() or "n"
    
    if(not buildmod=="n"):
        modfile = compile_lm(rawtext_file, lmdir_global, lm_syms, ngo)
        
        print "Created unpruned lang model file:", modfile
        print "Now pruning LM..."
        ngramshrink(modfile, modpru)
        #print "Now minimising LM..."
        #lm_utils.fstmin(modpru,modpru)
        
        #we don't use the unpruned modfile again, so switch over to the pruned version here
        modfile = modpru
        
        remap_fname = os.path.join(lmdir_global,"lm_remap.dat")
        create_remap_table(lm_syms, remap_fname)
        
        osymfile = os.path.join(base_dir,"slm_sym.dat")
        remap_lm(modfile, remap_fname, osymfile)
        print "remapped modfile output symbols"
                
    #create_converter(lmdir_global)
    #print "created converter."
    
    slm_dir = raw_input("Type in SLM dir or hit return to match LM [%s]" % lm_dir) or lm_dir
    slm_dir = os.path.join(base_dir,slm_dir)
        
    print "using ",slm_dir

    generate_slm_from_txt(lm_txt, slm_dir, do_plot=True)
    #generate_slm(tr_rows, slm_dir, do_plot=False) # build the sentence length model, plot it so we can see it's sane
    print "slm generated from", tr_file, "in", slm_dir
    
    print "all constituent system files now compiled"

if __name__ == '__main__':
    main(sys.argv[1:])