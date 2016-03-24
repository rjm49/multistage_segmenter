'''
Created on Feb 24, 2016

@author: rjm49
'''
import glob, os
from multistage_segmenter.common import DIR, PM_SUB_DIR,\
     PILOT_FILE_NORMED, GOLD_SUB_DIR, read_file, PROBFILE, load_symbol_table,\
    LM_SYM_FILE, PROSODIC_PREDICTION_FILE
from multistage_segmenter.lm_gen import fstcompose
import codecs
from multistage_segmenter.pm.pm_utils import generate_pm_text_files,\
    compile_pm_files


def open_wfile(odir,transcript_id):
    ofilename = os.path.join(odir,transcript_id+".gld")
    fhandle = codecs.open(ofilename, 'w')
    return fhandle

if __name__ == '__main__':
    lmdir = "eval1n"
    te_file = raw_input("enter test file name: [%s]" % PILOT_FILE_NORMED) or PILOT_FILE_NORMED
    te_rows = read_file(os.path.join(DIR, te_file), ',', skip_header=True)
    
    lmdir_global = os.path.join(DIR,lmdir)
    lm_syms = load_symbol_table(lmdir_global, LM_SYM_FILE)
    prob_rows = read_file(os.path.join(DIR, PROSODIC_PREDICTION_FILE), ' ', skip_header=True)

    generate_pm_text_files(lm_syms, te_rows, prob_rows)
    compile_pm_files(sym_dir=lmdir_global)