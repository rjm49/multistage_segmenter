'''
Created on Feb 24, 2016

@author: rjm49
'''
import glob, os
import shutil

from common import DIR, PM_SUB_DIR, \
    JOINT_LM_CV_SLM_FILE_GLOBAL, COMP_SUB_DIR, LM_PRUNED, OUTS_SUB_DIR, \
    SHP_SUB_DIR, LM_RAW
from find_shortest_paths import stringify_shortest_paths
import find_shortest_paths
from lm_gen import fstcompose


def process_inputs(input_dir, lm_file, out_dir):
    if(not os.path.exists(input_dir)):
        print "FST source directory",input_dir,"does not exist - can't continue analysis without it!"
        exit(1)
       
    #create/refresh the working directory
    shutil.rmtree(out_dir, ignore_errors=True)
    os.mkdir(out_dir)
    
    fs = glob.glob(os.path.join(input_dir,"*.fst"))
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
    
#     modpru = os.path.join(DIR,lmdir,LM_PRUNED)
    lang_mod = os.path.join(DIR,lmdir,LM_RAW)
    pm_dir = os.path.join(DIR,PM_SUB_DIR)
    pmlm_dir = os.path.join(DIR, "pm_lm_composed")
    full_cmp_dir = os.path.join(DIR, COMP_SUB_DIR)
    
    pmshp_dir = os.path.join(DIR, "pm_shortest")
    pmouts_dir = os.path.join(DIR, "pm_output")
    
    pmlm_indir = os.path.join(DIR, "pm_lm_composed")
    pmlmshp_dir = os.path.join(DIR, "pm_lm_shortest")
    pmlmouts_dir = os.path.join(DIR, "pm_lm_output")
                    
    stringify_shortest_paths(pm_dir, pmshp_dir, pmouts_dir)
    
    #now just use the pruned LM file without slen modifier
    process_inputs(pm_dir, lang_mod, pmlm_dir)
    stringify_shortest_paths(pmlm_dir, pmlmshp_dir, pmlmouts_dir)
    
    #use combined LM and slen modifier
    process_inputs(pm_dir, JOINT_LM_CV_SLM_FILE_GLOBAL, full_cmp_dir)
    stringify_shortest_paths(full_cmp_dir, os.path.join(DIR,SHP_SUB_DIR), os.path.join(DIR, OUTS_SUB_DIR))