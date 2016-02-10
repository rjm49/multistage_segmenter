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

def compile_lm(ifile, lmdir_global):
    #generate_normed_text_file(data)
    #raw_input("about to far compile - press key")
    farfile = farcompilestrings(ifile, lmdir_global) #create test.far from the normed text file
    print "farcompiled strings"
    #raw_input("about to ngramcount - press key")
    cntfile = ngramcount(farfile, lmdir_global, 3) #hopefully this combines all the segments into a single set of unified counts
    print "counted ngrammes"
    #raw_input("about to ngrammake - press key")
    modfile = ngrammake(cntfile, lmdir_global) #this creates the ngram model file
    print "made ngrammes"
    return modfile

def generate_normed_text_file(data, lmdir_global):   
    rec_id = None
    seg_id = None
    first = True
    filenm = os.path.join(lmdir_global,"normed.txt")
    
    #if this file already exists, just return the full filename
    if(os.path.exists(filenm) and os.path.isfile(filenm)):
        return filenm
    else:
        os.makedirs(os.path.dirname(filenm))
    
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
    return filenm

def ngramsymbols(infile):
    sp.call([cmd_ngramsymbols], stdin=open(infile), stdout=open(SYM_FILE_GLOBAL,"w"))

def farcompilestrings(ifile, lmdir_global):
    ofile = os.path.join(lmdir_global, "lm.far")
    sp.call([cmd_farcompilestrings,"-symbols="+SYM_FILE_GLOBAL,"-keep_symbols=1",ifile], stdout=open(ofile,"w"))
    return ofile
    
#ngramcount -order=5 earnest.far >earnest.cnts
def ngramcount(ifile, lmdir_global, ordr):
    cntfile = os.path.join(lmdir_global,"lm.cnt")
    sp.call([cmd_ngramcount, "--require_symbols=false", "-order="+str(ordr), ifile], stdout=open(cntfile,'w'))
    print "created",cntfile
    return cntfile

#ngrammake earnest.cnts >earnest.mod
def ngrammake(ifile, lmdir_global):
    print "calling ngrammake on", ifile
    modfile = os.path.join(lmdir_global,"lm.mod")
    sp.call([cmd_ngrammake, ifile], stdout=open(modfile,'w'))
    print "created",modfile
    return modfile

#fstcompose a.fst b.fst out.fst 
def fstcompose(a,b, out):
    cmpfile = os.path.join(DIR,OUTSUBDIR, out)
    print cmpfile
    sp.call([cmd_fstcompose, a, b, cmpfile])
    
#fstcompile --isymbols=isyms.txt --osymbols=osyms.txt text.fst binary.fst
def fstcompile(txtf,binf):
    sp.call(["fstcompile","--isymbols="+SYM_FILE_GLOBAL,"--osymbols="+SYM_FILE_GLOBAL, "--keep_isymbols", "--keep_osymbols",txtf,binf])
    
def fstarcsort(txtf,ilabel_sort=True):
    sp.call(["fstarcsort","--sort_type="+("ilabel" if ilabel_sort else "olabel"),txtf,txtf])
    
def add_symbols(fstf):
    sp.call(["fstsymbols","--isymbols="+SYM_FILE_GLOBAL,"--osymbols="+SYM_FILE_GLOBAL,fstf])
    
def nshortest_path(fstf,outf,ordr):
    sp.call(["fstshortestpath","--nshortest="+str(ordr),fstf,outf])