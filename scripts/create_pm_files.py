'''
Created on Feb 24, 2016

@author: rjm49
'''
import codecs
import glob, os

from common import DIR, PM_SUB_DIR, \
     PILOT_FILE_NORMED, GOLD_SUB_DIR, read_file, load_symbol_table, \
    LM_SYM_FILE, PROSODIC_PREDICTION_FILE
from lm_gen import fstcompose
from pm.pm_utils import generate_pm_text_files, \
    compile_pm_files


def open_wfile(odir,transcript_id):
    ofilename = os.path.join(odir,transcript_id+".gld")
    fhandle = codecs.open(ofilename, 'w')
    return fhandle

if __name__ == '__main__':
    lmdir = raw_input("enter language model name: [%s]" % "eval1n") or "eval1n"
    te_file = raw_input("enter test file name: [%s]" % PILOT_FILE_NORMED) or PILOT_FILE_NORMED
    te_rows = read_file(os.path.join(DIR, te_file), ',', skip_header=True)
    
    lmdir_global = os.path.join(DIR,lmdir)
    lm_syms = load_symbol_table(lmdir_global, LM_SYM_FILE)
    prob_rows = read_file(os.path.join(DIR, PROSODIC_PREDICTION_FILE), ' ', skip_header=True)

    generate_pm_text_files(lm_syms, te_rows, prob_rows, max_count=-1)
    compile_pm_files(sym_dir=lmdir_global)