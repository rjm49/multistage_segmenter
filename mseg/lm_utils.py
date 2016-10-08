'''
Created on Dec 8, 2015

@author: rjm49
'''
import codecs
import os

from mseg.common import DIR, PM_SUB_DIR, BREAK, SYM_FILE, LM_SYM_FILE,\
    save_symbol_table, create_remap_table
import subprocess as sp


cmd_ngramsymbols = "ngramsymbols"
cmd_farcompilestrings = "farcompilestrings"
cmd_ngramcount = "ngramcount"
cmd_ngrammake = "ngrammake"
cmd_fstcompose = "fstcompose"

def compile_lm(raw_text_file, lmdir_global, lm_syms, ngo):
    
    #ngramsymbols(raw_text_file, lmdir_global)
    symfile = os.path.join(lmdir_global, LM_SYM_FILE)

    save_symbol_table(lm_syms, symfile)
           
    #generate_normed_text_file(data)
    #raw_input("about to far compile - press key")
    farfile = farcompilestrings(raw_text_file, lmdir_global) #create test.far from the normed text file
    print "farcompiled strings"
    #raw_input("about to ngramcount - press key")
    cntfile = ngramcount(farfile, lmdir_global, ngo) #hopefully this combines all the segments into a single set of unified counts
    print "counted ngrammes"
    #raw_input("about to ngrammake - press key")
    modfile = ngrammake(cntfile, lmdir_global) #this creates the ngram model file
    
    print "made ngrammes"
    return modfile

def remap_lm(lm_file, remap_file, osymfile):
    sp.call(["fstrelabel","--relabel_opairs="+remap_file, lm_file, lm_file])
    sp.call(["fstrelabel","--relabel_osymbols="+osymfile, lm_file, lm_file])
    
def generate_normed_text_file(data, lmdir_global):   
    filenm = os.path.join(lmdir_global,"normed.txt")
    
    #if this file already exists, just return the full filename
    if(os.path.exists(filenm)):
        print filenm, "already exists.  Using existing file..."
        return filenm

    try:
        os.makedirs(os.path.dirname(filenm))
    except OSError:
        print "could not make dirs"
        
    writer = codecs.open(filenm, 'w')
    
    rec_ids = []
    for r in data:
        if r[0] not in rec_ids:
            rec_ids.append(r[0])

    for rec_id in rec_ids:
        rec = [r for r in data if r[0]==rec_id ]
        outs = ""
        print rec_id, "recording length=",len(rec)
        for s in rec:
            outs += s[5]+" "
            if int(s[6])==1:
                outs += "<break> "
        outs = outs.strip() + "\n"
        writer.write(outs)
    writer.write('<unk>\n')
 
    #_ = raw_input("hit key...")
   
#     print 'writing file',filenm
#     for r in data:
#         if rec_id!=r[0] or seg_id!=r[1]:
#             if not first:
#                 trailer = '\n' if (rec_id!=r[0]) else ' ' #a trailing space for new seg, a newline for new recprding
#                 writer.write(BREAK+trailer) #finish off the segment
#             else:
#                 first=False
#             rec_id = r[0]
#             seg_id = r[1]
#         w = r[5]
#         writer.write(w+' ')
#     writer.write(BREAK)
#     writer.write('\n<unk>\n')
#     writer.flush()
    writer.close()
    return filenm

def ngramsymbols(infile, lmdir_global):
    symfile = os.path.join(lmdir_global, LM_SYM_FILE)
    sp.call([cmd_ngramsymbols], stdin=open(infile), stdout=open(symfile,"w"))

def farcompilestrings(ifile, lmdir_global):
    symfile = os.path.join(lmdir_global, LM_SYM_FILE)
    ofile = os.path.join(lmdir_global, "lm.far")
    sp.call([cmd_farcompilestrings, "-symbols="+symfile,"-keep_symbols=1",ifile], stdout=open(ofile,"w"))
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
    cmpfile = os.path.join(DIR,PM_SUB_DIR, out)
    print "composing",a,b,"->",cmpfile
    sp.call([cmd_fstcompose, a, b, cmpfile])
    
def ngramshrink(a,out):
#ngramshrink -method=relative_entropy -theta=0.00015 eval1n/lm.mod  >eval1n/lm.pru
    sp.call(["ngramshrink","-method=relative_entropy","-theta=1.0e-5",a],stdout=open(out,'w'))
    
def fstmin(a,out):
#ngramshrink -method=relative_entropy -theta=0.00015 eval1n/lm.mod  >eval1n/lm.pru
    sp.call(["fstminimize",a,out])
    
def fstimmut(a,out):
#ngramshrink -method=relative_entropy -theta=0.00015 eval1n/lm.mod  >eval1n/lm.pru
    sp.call(["fstconvert","-fst_type=const",a,out])

#fstcompile --isymbols=isyms.txt --osymbols=osyms.txt text.fst binary.fst
def fstcompile(txtf,binf, isyms, osyms):
    sp.call(["fstcompile","--isymbols="+isyms,"--osymbols="+osyms, "--keep_isymbols", "--keep_osymbols",txtf,binf])
    
def fstarcsort(f,ilabel_sort=True):
    sp.call(["fstarcsort","--sort_type="+("ilabel" if ilabel_sort else "olabel"),f,f])
    
def add_symbols(fstf, lmdir_global):
    symfile = os.path.join(lmdir_global, SYM_FILE)
    sp.call(["fstsymbols","--isymbols="+symfile,"--osymbols="+symfile,fstf])
    
def nshortest_path(fstf,outf,ordr):
    sp.call(["fstshortestpath","--nshortest="+str(ordr),fstf,outf])