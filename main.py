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

lm_dir = "lm"

rawtext_file = os.path.join(DIR,lm_dir,"normed.txt")
farfile = os.path.join(DIR,lm_dir,"lm.far")
#symfile = os.path.join(DIR,"vsys.sym")
cntfile = os.path.join(DIR,lm_dir,"lm.cnt")
modfile = os.path.join(DIR,lm_dir,"lm.mod")


gen_ntxt = False
source_data, lmdir = EVAL1_FILE_NORMED, "eval1n"


if __name__ == '__main__':
        
    #EVAL1_FILE_NORMED = "smalltest_norm.csv"
    print "reading raw annotated token data from", EVAL1_FILE_NORMED
    training_rows = read_file(os.path.join(DIR, EVAL1_FILE_NORMED), ',', skip_header=True)
    test_rows = read_file(os.path.join(DIR, PILOT_FILE_NORMED), ',', skip_header=True)

    #check to see if the language model dir exists and if not create it
    lmdir_global = os.path.join(DIR,lmdir)
    if(not os.path.exists(lmdir_global)):
        try:
            os.mkdir(lmdir_global)
        except OSError:
            print lmdir_global, "already seems to exist!"
            exit
    
    all_syms = set([r[5] for r in (training_rows + test_rows)])

    save_symbol_table(all_syms)

    rawtext_file = generate_normed_text_file(training_rows, lmdir_global)
    
    modfile = os.path.join(lmdir_global,"lm.mod")
    if(os.path.exists(modfile)):
        ans = raw_input("model in "+lmdir+" already exists.  Overwrite? [n]")
        if(ans.lower()=="y"):
            modfile = compile_lm(rawtext_file, lmdir_global)
            print "Created language model file:", modfile
    
    generate_slm(training_rows, do_plot=False) # build the sentence length model, plot it so we can see it's sane
    #raw_input("slm done - press key")
    
    create_converter()
    print "created converter."
    
    fstarcsort(SLM_FST_FILE_GLOBAL, ilabel_sort=True)
    print "composing CV o SLM..."
    fstcompose(CONV_FST_FILE_GLOBAL, SLM_FST_FILE_GLOBAL, JOINT_CV_SLM_FILE_GLOBAL)
    print "Done. Now composing LM o CVoSLM..."
    
    #fstcompose(modfile, JOINT_CV_SLM_FILE_GLOBAL, JOINT_LM_CV_SLM_FILE_GLOBAL) #TODO do this here?
    #print "Wrote LMoCVoSLM file:", JOINT_LM_CV_SLM_FILE_GLOBAL
    #sys.stdin.read()

    prob_rows = read_file(os.path.join(DIR, PROBFILE), ' ', skip_header=True)
    
    raw_input("about to generate pm text files- press key to continue...")
    #generate pm
    generate_pm_text_files(test_rows, prob_rows) #this should produce the fxt files on disc that can feed into the FST composition
        
    compile_pm_files()
    print "compiled PM files."
    
    fs = glob.glob(os.path.join(DIR,OUTSUBDIR,"*.fst"))
    outdir = os.path.join(DIR,"composed")
    for f in fs:
        print "composing",f,"o (LM o CV o SLM)"
        fstcompose(f, JOINT_LM_CV_SLM_FILE_GLOBAL, os.path.join(DIR,outdir,f))
    
    