'''
Created on Dec 8, 2015

@author: rjm49
'''
import subprocess as sp
from multistage_segmenter.common import DIR, OUTSUBDIR, SYM_FILE_GLOBAL, BREAK
import os
import string
import codecs

cmd_ngramsymbols = "ngramsymbols"
cmd_farcompilestrings = "farcompilestrings"
cmd_ngramcount = "ngramcount"
cmd_ngrammake = "ngrammake"
cmd_fstcompose = "fstcompose"

lm_dir = "lm"

rawtext_file = os.path.join(DIR,lm_dir,"normed.txt")
farfile = os.path.join(DIR,lm_dir,"lm.far")
#symfile = os.path.join(DIR,"vsys.sym")
cntfile = os.path.join(DIR,lm_dir,"lm.cnt")
modfile = os.path.join(DIR,lm_dir,"lm.mod")

def generate_lm(data):
    generate_normed_text_file(data)
    print "gen'd normed text file"
    farcompilestrings() #create test.far from the normed text file
    print "farcompiled strings"
    ngramcount(3) #hopefully this combines all the segments into a single set of unified counts
    print "counted ngrammes"
    ngrammake() #this creates the ngram model file
    print "made ngrammes"

def generate_normed_text_file(data):
    rec_id = None
    seg_id = None
    first = True
    filenm = os.path.join(DIR,OUTSUBDIR,"normed.txt")
    writer = codecs.open(filenm, 'w')
    print 'writing file',filenm
    for r in data:
        if rec_id != r[0] or seg_id != r[1]:
            if not first:
                trailer = '\n' if (rec_id!=r[0]) else ' ' # trailing space for a segment break, newline for the end of a whole recording
                writer.write(BREAK+trailer) #finish off the segment
            else:
                first=False
            rec_id = r[0]
            seg_id = r[1]
        #w = r[5].translate(string.maketrans("",""), string.punctuation) #remove punctuation  
        w = r[5]
        writer.write(w)
        writer.write(' ')
    writer.flush()
    writer.close() 

def ngramsymbols():
    sp.call([cmd_ngramsymbols], stdin=open(rawtext_file), stdout=open(SYM_FILE_GLOBAL,"w"))

def farcompilestrings():
    sp.call([cmd_farcompilestrings,"-symbols="+SYM_FILE_GLOBAL,"-keep_symbols=1",rawtext_file], stdout=open(farfile,"w"))
    
#ngramcount -order=5 earnest.far >earnest.cnts
def ngramcount(ordr):
    sp.call([cmd_ngramcount, "--require_symbols=false", "-order="+str(ordr), farfile], stdout=open(cntfile,'w'))
    print "created",cntfile

#ngrammake earnest.cnts >earnest.mod
def ngrammake():
    sp.call([cmd_ngrammake, cntfile], stdout=open(modfile,'w'))
    print "created",modfile

#fstcompose a.fst b.fst out.fst 
def fstcompose(a,b, out):
    cmpfile = os.path.join(DIR,OUTSUBDIR, out)
    sp.call([cmd_fstcompose, a, b, cmpfile])
    
#fstcompile --isymbols=isyms.txt --osymbols=osyms.txt text.fst binary.fst
def fstcompile(txtf,binf):
    sp.call(["fstcompile","--isymbols="+SYM_FILE_GLOBAL,"--osymbols="+SYM_FILE_GLOBAL, "--keep_isymbols", "--keep_osymbols",txtf,binf])
    
def fstarcsort(txtf,ilabel_sort=True):
    sp.call(["fstarcsort","--sort_type="+("ilabel" if ilabel_sort else "olabel"),txtf,txtf])
    
def add_symbols(fstf):
    sp.call(["fstsymbols","--isymbols="+SYM_FILE_GLOBAL,"--osymbols="+SYM_FILE_GLOBAL,fstf])