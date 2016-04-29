'''
Created on 30 Nov 2015

@author: Russell
'''
import os

from common import LM_SYM_FILE, SYM_FILE, EVAL1_FILE_NORMED, \
    DIR, PILOT_FILE_NORMED, read_file, save_symbol_table
from lm_gen import generate_normed_text_file


gen_ntxt = False
tr_file, lmdir = EVAL1_FILE_NORMED, "eval1n"
#tr_file, lmdir = "test1.csv", "test1"

if __name__ == '__main__':
        
    #EVAL1_FILE_NORMED = "smalltest_norm.csv"     
    lmdir = raw_input("Type in LM dir or hit return to use default [%s]" % lmdir) or lmdir
    print "using ",lmdir
    lmdir_global = os.path.join(DIR,lmdir)
    
    tr_file = raw_input("enter training file name: [%s]" % tr_file) or tr_file
    te_file = raw_input("enter test file name: [%s]" % PILOT_FILE_NORMED) or PILOT_FILE_NORMED
    
    tr_rows = read_file(os.path.join(DIR, tr_file), ',', skip_header=True)
    te_rows = read_file(os.path.join(DIR, te_file), ',', skip_header=True)
    rawtext_file = generate_normed_text_file(tr_rows, lmdir_global)
    
    all_syms = set([r[5] for r in (tr_rows + te_rows)])
    lm_syms = set([r[5] for r in tr_rows])
    
    save_symbol_table(all_syms, lmdir_global, SYM_FILE)
    save_symbol_table(lm_syms, lmdir_global, LM_SYM_FILE)