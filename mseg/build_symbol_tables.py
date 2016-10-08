'''
Created on 30 Nov 2015

@author: Russell
'''
import os

from mseg.common import LM_SYM_FILE, SYM_FILE, TRAIN_FILE_DEFAULT, \
    DIR, TEST_FILE_DEFAULT, read_file, save_symbol_table
from mseg.lm_utils import generate_normed_text_file


gen_ntxt = False
tr_fname, slm_dir = TRAIN_FILE_DEFAULT, "eval1n"
#tr_fname, slm_dir = "test1.csv", "test1"

if __name__ == '__main__':
        
    #TRAIN_FILE_DEFAULT = "smalltest_norm.csv"     
    slm_dir = raw_input("Type in LM dir or hit return to use default [%s]" % slm_dir) or slm_dir
    print "using ",slm_dir
    lmdir_global = os.path.join(DIR,slm_dir)
    
    tr_fname = raw_input("enter training file name: [%s]" % tr_fname) or tr_fname
    te_file = raw_input("enter test file name: [%s]" % TEST_FILE_DEFAULT) or TEST_FILE_DEFAULT
    
    tr_data = read_file(os.path.join(DIR, tr_fname), ',', skip_header=True)
    te_rows = read_file(os.path.join(DIR, te_file), ',', skip_header=True)
    rawtext_file = generate_normed_text_file(tr_data, lmdir_global)
    
    all_syms = set([r[5] for r in (tr_data + te_rows)])
    lm_syms = set([r[5] for r in tr_data])
    
    save_symbol_table(all_syms, lmdir_global, SYM_FILE)
    save_symbol_table(lm_syms, lmdir_global, LM_SYM_FILE)