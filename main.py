'''
Created on 30 Nov 2015

@author: Russell
'''
from multistage_segmenter.common import EVAL1_FILE_NORMED, read_file, DIR, PROBFILE, \
    PILOT_FILE_NORMED, save_symbol_table, OUTSUBDIR, JOINT_CV_SLM_FILE_GLOBAL,\
    SLM_FST_FILE_GLOBAL, CONV_FST_FILE_GLOBAL, JOINT_LM_CV_SLM_FILE_GLOBAL,\
    EVAL1_FILE
import os
import string
from multistage_segmenter.lm_gen import fstcompose, compile_lm,\
    fstarcsort, generate_normed_text_file
from multistage_segmenter.pm.pm_utils import compile_pm_files,\
    generate_pm_text_files
from multistage_segmenter.slm.slm_utils import generate_slm,\
    create_converter
import glob
import sys
from string import lowercase
from __builtin__ import True

gen_ntxt = False
#source_data, lmdir = EVAL1_FILE_NORMED, "eval1n"
tr_file, lmdir = "test1.csv", "test1"

if __name__ == '__main__':
        
    #EVAL1_FILE_NORMED = "smalltest_norm.csv"     
    lmdir = raw_input("Type in LM dir or hit return to use default [%s]" % lmdir) or lmdir
    print "using ",lmdir
    lmdir_global = os.path.join(DIR,lmdir)
    
    tr_file = raw_input("enter training file name: [%s]" % tr_file) or tr_file
    te_file = raw_input("enter test file name: [%s]" % PILOT_FILE_NORMED) or PILOT_FILE_NORMED
    
    tr_rows = read_file(os.path.join(DIR, tr_file), ',', skip_header=True)
    te_rows = read_file(os.path.join(DIR, te_file), ',', skip_header=True)
    rawtext_file = generate_normed_text_file(tr_rows, lmdir_global)
    
    all_syms = set([r[5] for r in tr_rows + te_rows])
    
    lm_syms = set([r[5] for r in tr_rows])
    
    save_symbol_table(all_syms)
    
    buildmod = "y"
    modfile = os.path.join(lmdir_global,"lm.mod")
    if(os.path.exists(modfile)):
        buildmod = raw_input("model file in "+lmdir+" already exists.  Overwrite? [n]").lower() or "n"
    
    if(not buildmod=="n"):
        modfile = compile_lm(rawtext_file, lmdir_global)
        print "Created language model file:", modfile
    
    generate_slm(tr_rows, do_plot=False) # build the sentence length model, plot it so we can see it's sane
    #raw_input("slm done - press key")
    
    create_converter()
    print "created converter."
    
    fstarcsort(SLM_FST_FILE_GLOBAL, ilabel_sort=True)
    print "composing CV o SLM..."
    fstcompose(CONV_FST_FILE_GLOBAL, SLM_FST_FILE_GLOBAL, JOINT_CV_SLM_FILE_GLOBAL)
    print "Done. Now composing LM o CVoSLM..."
    
    fstcompose(modfile, JOINT_CV_SLM_FILE_GLOBAL, JOINT_LM_CV_SLM_FILE_GLOBAL) #TODO do this here?
    print "Wrote LMoCVoSLM file:", JOINT_LM_CV_SLM_FILE_GLOBAL
    #sys.stdin.read()

    prob_rows = read_file(os.path.join(DIR, PROBFILE), ' ', skip_header=True)
    
    raw_input("about to generate pm text files- press key to continue...")
    #generate pm
    generate_pm_text_files(lm_syms, te_rows, prob_rows) #this should produce the fxt files on disc that can feed into the FST composition
        
    compile_pm_files()
    print "compiled PM files."
    
    fs = glob.glob(os.path.join(DIR,OUTSUBDIR,"*.fst"))
    for f in fs:
        outf = os.path.join(DIR,"composed",os.path.basename(f))
        #print "composing",f,"o (LM o CV o SLM)"
        #fstcompose(f, JOINT_LM_CV_SLM_FILE_GLOBAL, outf)
        fstcompose(f, modfile, outf)