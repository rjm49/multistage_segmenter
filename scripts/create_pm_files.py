'''
Created on Feb 24, 2016

@author: rjm49
'''
import codecs
import glob, os

from common import DIR, PM_SUB_DIR, GOLD_SUB_DIR, read_file, load_symbol_table, \
    LM_SYM_FILE, PROSODIC_PREDICTION_FILE, TEST_FILE_DEFAULT
from lm_gen import fstcompose
from pm.pm_utils import generate_pm_text_files, \
    compile_pm_files


def open_wfile(odir,transcript_id):
    ofilename = os.path.join(odir,transcript_id+".gld")
    fhandle = codecs.open(ofilename, 'w')
    return fhandle

if __name__ == '__main__':
    lmdir = raw_input("enter language model name: [%s]" % "lm_default") or "lm_default"
    pmdir = raw_input("enter prosodic model name: [%s]" % "pm_default") or "pm_default"
    te_file = raw_input("enter test file name: [%s]" % TEST_FILE_DEFAULT) or TEST_FILE_DEFAULT
    te_rows = read_file(os.path.join(DIR, te_file), ',', skip_header=True)
    
    lmdir_global = os.path.join(DIR,lmdir)
    lm_syms = load_symbol_table(lmdir_global, LM_SYM_FILE)
    prob_rows = read_file(os.path.join(DIR, pmdir, PROSODIC_PREDICTION_FILE), ' ', skip_header=True)

    generate_pm_text_files(lm_syms, te_rows, prob_rows, max_count=-1)
    compile_pm_files(sym_dir=lmdir_global)