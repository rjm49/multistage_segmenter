'''
Created on Feb 24, 2016

@author: rjm49
'''
import glob, os
import shutil

from common import CONV_FST, JOINT_CV_SLM_FILE_GLOBAL, \
    JOINT_LM_CV_SLM_FILE_GLOBAL, DIR, PM_SUB_DIR, LM_RAW, COMP_SUB_DIR, \
    SHP_SUB_DIR, OUTS_SUB_DIR
import lm_gen
from scripts import find_shortest_paths

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
        lm_gen.fstcompose(f, lm_file, outf)
        print "output:",outf

def compose_converters(pm_dir, lm_dir, slm_dir):
    slm_file = os.path.join(slm_dir,"slm.fst")
    lm_gen.fstarcsort(slm_file, ilabel_sort=True)
    print "composing CV o SLM..."
    convfst = os.path.join(lm_dir,CONV_FST)
    lm_gen.fstcompose(convfst, slm_file, JOINT_CV_SLM_FILE_GLOBAL)
    #fstcompose(modfile,convfst,os.path.join(DIR,"lm_cv"))
        
    print "Done. Now composing LM o CVoSLM..."
    modfile = os.path.join(lm_dir,"mod.pru")
    lm_gen.fstcompose(modfile, JOINT_CV_SLM_FILE_GLOBAL, JOINT_LM_CV_SLM_FILE_GLOBAL) #TODO do this here?
    #fstcompose(os.path.join(DIR,"lm_cv"), SLM_FST_FILE_GLOBAL, JOINT_LM_CV_SLM_FILE_GLOBAL)
    print "Wrote LMoCVoSLM file:", JOINT_LM_CV_SLM_FILE_GLOBAL

if __name__ == '__main__':
    batch_dir = "default_batch"
    lm_dir = "lm_default"
    slm_dir = "slm_default"
    print "This script will run all the prosodic model FSTs through the combined language/slen model"
    print "And also run the PM FSTs through just the LM without slen (for comparison)"
    lm_dir = raw_input("Type in LM subdir or hit return to use default [%s]" % lm_dir) or lm_dir
    lm_dir = os.path.join(DIR,lm_dir)
    print "using ",lm_dir
    
    slm_dir = raw_input("Type in SLM subdir or hit return to use default [%s]" % slm_dir) or slm_dir
    slm_dir = os.path.join(DIR,slm_dir)
    print "using ",slm_dir

    pm_dir = "pm_default"
    pm_dir = raw_input("Type in PM dir or hit return to use default [%s]" % pm_dir) or pm_dir
    pm_dir = os.path.join(DIR,"pm_default",PM_SUB_DIR)
    print "using ",pm_dir
    
#     modpru = os.path.join(DIR,lm_dir,LM_PRUNED)
    lang_mod = os.path.join(lm_dir,LM_RAW)
    
    pmlm_dir = os.path.join(DIR, batch_dir, "pm_lm_composed")
    full_cmp_dir = os.path.join(DIR, batch_dir, COMP_SUB_DIR)
    
    pmshp_dir = os.path.join(DIR, batch_dir, "pm_shortest")
    pmouts_dir = os.path.join(DIR, batch_dir, "pm_output")
    
    pmlm_indir = os.path.join(DIR, batch_dir, "pm_lm_composed")
    pmlmshp_dir = os.path.join(DIR, batch_dir, "pm_lm_shortest")
    pmlmouts_dir = os.path.join(DIR, batch_dir, "pm_lm_output")

    find_shortest_paths.stringify_shortest_paths(pm_dir, pmshp_dir, pmouts_dir)
    
    #now just use the pruned LM file without slen modifier
    process_inputs(pm_dir, lang_mod, pmlm_dir)
    find_shortest_paths.stringify_shortest_paths(pmlm_dir, pmlmshp_dir, pmlmouts_dir)
    
    #use combined LM and slen modifier
    compose_converters(pm_dir, lm_dir, slm_dir)
    process_inputs(pm_dir, JOINT_LM_CV_SLM_FILE_GLOBAL, full_cmp_dir)
    find_shortest_paths.stringify_shortest_paths(full_cmp_dir, os.path.join(DIR,SHP_SUB_DIR), os.path.join(DIR, OUTS_SUB_DIR))