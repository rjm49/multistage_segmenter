'''
Created on Feb 24, 2016

@author: rjm49
'''
import glob, os
from multistage_segmenter.common import DIR, PM_SUB_DIR,\
    JOINT_LM_CV_SLM_FILE_GLOBAL, COMP_SUB_DIR
from multistage_segmenter.lm_gen import fstcompose

def process_inputs(in_dir, lm_file, out_dir):
    fs = glob.glob(os.path.join(in_dir,"*.fst"))
    for f in fs:
        outf = os.path.join(out_dir ,os.path.basename(f))        
        fstcompose(f, lm_file, outf)
        print "output:",outf

if __name__ == '__main__':
    lmdir = "eval1n"
    print "This script will run all the prosodic model FSTs through the combined language/slen model"
    print "And also run the PM FSTs through just the LM without slen (for comparison)"
    lmdir = raw_input("Type in LM dir or hit return to use default [%s]" % lmdir) or lmdir
    print "using ",lmdir
    
    lmfile = os.path.join(DIR,lmdir,"lm.pru")
    pm_dir = os.path.join(DIR,PM_SUB_DIR)
    full_cmp_dir = os.path.join(DIR, COMP_SUB_DIR)
    pmlm_dir = os.path.join(DIR, "pm_lm_composed")
            
    for p in (pm_dir, full_cmp_dir, pmlm_dir):
        if not os.path.exists(p):
            os.makedirs(p)
    
    #use combined LM and slen modifier
    process_inputs(pm_dir, JOINT_LM_CV_SLM_FILE_GLOBAL, full_cmp_dir)

    #now just use the pruned LM file without slen modifier
    
    process_inputs(pm_dir, lmfile, pmlm_dir)
    