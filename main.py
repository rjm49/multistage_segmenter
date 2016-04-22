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
    te_file = raw_input("enter test file name: [%s]" % PILOT_FILE_NORMED) or PILOT_FILE_NORMED
    
    tr_rows = read_file(os.path.join(DIR, tr_file), ',', skip_header=True)
    te_rows = read_file(os.path.join(DIR, te_file), ',', skip_header=True)
    rawtext_file = generate_normed_text_file(tr_rows, lmdir_global)
    
    all_syms = set([r[5] for r in (tr_rows + te_rows)])
    lm_syms = set([r[5] for r in tr_rows])
    
    save_symbol_table(all_syms, lmdir_global, SYM_FILE)
    save_symbol_table(lm_syms, lmdir_global, LM_SYM_FILE)
        
    buildmod = "y"
    modfile = os.path.join(lmdir_global,"lm.mod")
    modpru = os.path.join(lmdir_global,LM_PRUNED)
    if(os.path.exists(modfile)):
        buildmod = raw_input("model file in "+lmdir_global+" already exists.  Overwrite? [n]").lower() or "n"
    
    if(not buildmod=="n"):
        modfile = compile_lm(rawtext_file, lmdir_global)
        print "Created unpruned lang model file:", modfile
        print "Now pruning LM..."
        ngramshrink(modfile, modpru)
        #we don't use the unpruned modfile again, so switch over to the pruned version here
        modfile = modpru
    
    #generate_slm(tr_rows, lmdir_global, do_plot=True) # build the sentence length model, plot it so we can see it's sane
    #raw_input("slm done - press key")
    
    create_converter(lmdir_global)
    print "created converter."
    
    raw_input("hit return to start compositions...")
    
    fstarcsort(SLM_FST_FILE_GLOBAL, ilabel_sort=True)
    print "composing CV o SLM..."
    convfst = os.path.join(lmdir_global,CONV_FST)
    fstcompose(convfst, SLM_FST_FILE_GLOBAL, JOINT_CV_SLM_FILE_GLOBAL)
    #fstcompose(modfile,convfst,os.path.join(DIR,"lm_cv"))
        
    print "Done. Now composing LM o CVoSLM..."
    fstcompose(modfile, JOINT_CV_SLM_FILE_GLOBAL, JOINT_LM_CV_SLM_FILE_GLOBAL) #TODO do this here?
    #fstcompose(os.path.join(DIR,"lm_cv"), SLM_FST_FILE_GLOBAL, JOINT_LM_CV_SLM_FILE_GLOBAL)
    print "Wrote LMoCVoSLM file:", JOINT_LM_CV_SLM_FILE_GLOBAL
    #sys.stdin.read()

    prob_rows = read_file(os.path.join(DIR, PROSODIC_PREDICTION_FILE), ' ', skip_header=True)
    
    raw_input("about to generate pm text files- press key to continue...")
    #generate pm
    generate_pm_text_files(lm_syms, te_rows, prob_rows) #this produces the fxt files on disc that can feed into the FST composition
        
    compile_pm_files(sym_dir=lmdir_global)
    print "compiled PM files."
    
    print "all constituent system files now compiled"