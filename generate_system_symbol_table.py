'''
Created on 3 Sep 2015

@author: Russell
This script just creates the symbol table used by other operations
'''
from common import LM_SYM_SRC, read_file, saveSymbolTable
from common import full_path

if __name__ == '__main__':
    syms = set()
    sym_rows = read_file(full_path(LM_SYM_SRC),',', True)
    for r in sym_rows:
        s = r[5][1:-1]
        syms.add(s)    
    saveSymbolTable(syms)