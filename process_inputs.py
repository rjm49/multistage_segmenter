'''
Created on Feb 24, 2016

@author: rjm49
'''
import glob, os
from multistage_segmenter.common import DIR, PM_SUB_DIR,\
    JOINT_LM_CV_SLM_FILE_GLOBAL
from multistage_segmenter.lm_gen import fstcompose

def process_inputs(lm_dir,pm_dir):
    fs = glob.glob(os.path.join(DIR,PM_SUB_DIR,"*.fst"))
    for f in fs:
        outf = os.path.join(DIR,"composed",os.path.basename(f))        
        fstcompose(f, JOINT_LM_CV_SLM_FILE_GLOBAL, outf)

if __name__ == '__main__':
    lmdir = "eval1n"
    print "This script will run all the prosodic model FSTs through the combined language/slen model"
    lmdir = raw_input("Type in LM dir or hit return to use default [%s]" % lmdir) or lmdir
    print "using ",lmdir
    lmdir_global = os.path.join(DIR,lmdir)
    pm_dir = os.path.join(DIR,PM_SUB_DIR)
    process_inputs(DIR, pm_dir)