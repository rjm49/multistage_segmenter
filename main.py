'''
Created on 30 Nov 2015

@author: Russell
'''
from multistage_segmenter.common import EVAL1_FILE_NORMED, read_file, DIR, PROBFILE, PILOT_FILE,\
    PILOT_FILE_NORMED, save_symbol_table, OUTSUBDIR, JOINT_CV_SLM_FILE_GLOBAL,\
    SLM_FST_FILE_GLOBAL, CONV_FST_FILE_GLOBAL, JOINT_LM_CV_SLM_FILE_GLOBAL
import os
import string
from multistage_segmenter.lm_gen import fstcompose, modfile, generate_lm,\
    fstarcsort
from multistage_segmenter.pm.pm_utils import compile_pm_files,\
    generate_pm_text_files
from multistage_segmenter.slm.slm_utils import generate_slm,\
    create_converter
import glob
import sys

if __name__ == '__main__':
    print "reading raw annotated token data from", EVAL1_FILE_NORMED
    training_rows = read_file(os.path.join(DIR, EVAL1_FILE_NORMED), ',', skip_header=True)
    test_rows = read_file(os.path.join(DIR, PILOT_FILE_NORMED), ',', skip_header=True)

    #print [r[5] for r in training_rows[0:100]]
#     print 'normalising tokens...'
#     for r in training_rows:
#         r[5] = r[5].translate(string.maketrans("",""), string.punctuation)
#     
#     for r in test_rows:
#         r[5] = r[5].translate(string.maketrans("",""), string.punctuation)
#     
    #print [r[5] for r in training_rows[0:100]]


    all_syms = set([r[5] for r in (training_rows + test_rows)])

    save_symbol_table(all_syms)
        
    generate_lm(training_rows)
    #raw_input("lm done - press key")
    
    generate_slm(training_rows, do_plot=False) # build the sentence length model, plot it so we can see it's sane
    #raw_input("slm done - press key")
    
    create_converter()
    
    fstarcsort(SLM_FST_FILE_GLOBAL, ilabel_sort=True)

    fstcompose(CONV_FST_FILE_GLOBAL, SLM_FST_FILE_GLOBAL, JOINT_CV_SLM_FILE_GLOBAL)
    fstcompose(modfile, JOINT_CV_SLM_FILE_GLOBAL, JOINT_LM_CV_SLM_FILE_GLOBAL) #TODO do this here?

    print "Wrote CVoSLM file:", JOINT_LM_CV_SLM_FILE_GLOBAL
    #sys.stdin.read()

    prob_rows = read_file(os.path.join(DIR, PROBFILE), ' ', skip_header=True)
    #generate pm
    generate_pm_text_files(test_rows, prob_rows) #this should produce the fxt files on disc that can feed into the FST composition
    compile_pm_files()
    

    #insert loop here for PMs
    #prep SVM for inference
    #for segments in datarows:
        #infer probabilities with SVM
        #build PM txt file
        #compile into PM FST
        #compose PM o copy(LM_SLM)
        #perform n-shortest path analysis
    
    
    fs = glob.glob(os.path.join(DIR,OUTSUBDIR,"*.fst"))
    outdir = os.path.join(DIR,"composed")
    for f in fs:
        print "composing",f,"o (LM o CV o SLM)"
        fstcompose(f, JOINT_LM_CV_SLM_FILE_GLOBAL, os.path.join(DIR,outdir,f))
    
    