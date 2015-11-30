'''
Created on 4 Sep 2015

@author: Russell
'''
from multistage_segmenter.common import loadSymbolTable, DIR, OUTSUBDIR, UNK, BREAK,\
    ANYWORD, EPS
import os
import codecs

if __name__ == '__main__':
    syms = loadSymbolTable()
    ofilename = os.path.join(DIR,OUTSUBDIR,"lm_slm_converter.fxt")
    
    ofile = codecs.open(ofilename, 'w')
    
    for sym in syms:
        if(sym not in [BREAK, UNK]):
            ofile.write("0 0 %s %s\n" % (sym,ANYWORD))

    ofile.write("0 0 %s %s\n" % (UNK,ANYWORD))
    ofile.write("0 0 %s %s\n" % (EPS,EPS))
    ofile.write("0 0 %s %s\n" % (BREAK,BREAK))
    ofile.write("0\n")
    #final state needed?
    ofile.flush()
    ofile.close()