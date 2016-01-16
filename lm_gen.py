'''
Created on Dec 8, 2015

@author: rjm49
'''
import subprocess as sp
from multistage_segmenter.common import DIR, OUTSUBDIR
import os

cmd_ngramsymbols = "ngramsymbols"
cmd_farcompilestrings = "farcompilestrings"
cmd_ngramcount = "ngramcount"
cmd_ngrammake = "ngrammake"
cmd_fstcompose = "fstcompose"
rawtext_file = os.path.join(DIR,OUTSUBDIR,"normed.txt")
farfile = os.path.join(DIR,OUTSUBDIR,"test.far")
symfile = os.path.join(DIR,OUTSUBDIR,"test.syms")
cntfile = os.path.join(DIR,OUTSUBDIR,"test.cnt")
modfile = os.path.join(DIR,OUTSUBDIR,"test.mod")
cmpfile = os.path.join(DIR,OUTSUBDIR,"test.cmp") #file for composed FSTs

print symfile

def ngramsymbols():
    sp.call([cmd_ngramsymbols], stdin=open(rawtext_file), stdout=open(symfile,"w"))

def farcompilestrings():
    sp.call([cmd_farcompilestrings,"-symbols="+symfile,"-keep_symbols=1",rawtext_file], stdout=open(farfile,"w"))
    
#ngramcount -order=5 earnest.far >earnest.cnts
def ngramcount(ordr):
    sp.call([cmd_ngramcount, "-order="+str(ordr), farfile], stdout=open(cntfile,'w'))
    print "created",cntfile

#ngrammake earnest.cnts >earnest.mod
def ngrammake():
    sp.call([cmd_ngrammake, cntfile], stdout=open(modfile,'w'))
    print "created",modfile

#fstcompose a.fst b.fst out.fst 
def fstcompose(a,b):
    sp.call([cmd_fstcompose, a, b, cmpfile])