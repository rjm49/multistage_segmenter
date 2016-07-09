'''
Created on Jan 16, 2016

@author: rjm49
'''
import codecs
from collections import Counter
import math
import os

from scipy.stats import gamma, norm

import matplotlib.pyplot as plt
from common import DIR, ANYWORD, EPS, BREAK, SLM_FST_FILE_GLOBAL, \
    SLM_FXT_FILE_GLOBAL, load_symbol_table, PM_SUB_DIR, UNK, \
    SYM_FILE, CONV_FXT, CONV_FST, LM_SYM_FILE
import subprocess as sp


def create_converter(lm_dir):
    #print "creating converter...."
    
    symfile = os.path.join(lm_dir,LM_SYM_FILE)
    syms = load_symbol_table(symfile)
    dummy_symfile = os.path.join(lm_dir,"..","slm_sym.dat")
    convfxt = os.path.join(lm_dir,CONV_FXT)
    convfst = os.path.join(lm_dir,CONV_FST)
    
    ofile = codecs.open(convfxt, 'w')
    
    for sym in syms:
        if(sym not in [ANYWORD, EPS, BREAK, UNK]):
            ofile.write("0 0 %s %s\n" % (sym,ANYWORD))

    ofile.write("0 0 %s %s\n" % (UNK,ANYWORD))
    ofile.write("0 0 %s %s\n" % (EPS,EPS))
    ofile.write("0 0 %s %s\n" % (BREAK,BREAK))
    ofile.write("0\n")
    #final state needed?
    ofile.flush()
    ofile.close()
    print "compiling converter",convfst,"with isyms=",symfile,"and osyms=",dummy_symfile
    sp.call(["fstcompile","--isymbols="+symfile,"--osymbols="+dummy_symfile, "--keep_isymbols", "--keep_osymbols", convfxt, convfst])
    #print "done...."    
    

def generate_slm(training_rows, slm_dir, do_plot=True):
    slm_fxt = os.path.join(slm_dir, "slm.fxt")
    slength_counts = Counter()
    slen=1
    for r in training_rows:
        #print r
        is_boundary = int(r[6])
        if(not is_boundary):
            slen += 1
        else:
#             print "adding slen=",(slen+1)
            slength_counts[slen]+=1
            slen = 1   
    els = list( slength_counts.elements() ) #Counter.elements() returns iterator that iterates across n instances of each element e where slength_counts[e]=n .. we make this into a list for plotting
    #print els
    x_vals = range(0, max(els)+1)
    
    (shape, loc, scale) = gamma.fit(els, floc=0)
    gam_gen = gamma(shape, loc, scale) #use these model params to build a new gamma distrib/n generator
    write_slm(slm_fxt, x_vals, gam_gen)
    if do_plot:
        plot_graph(x_vals, gam_gen, els)
    compile_slm(slm_dir) #this last step compiles the slm to binary .fst format


def generate_slm_from_txt(training_rows, slm_dir, do_plot=True):
    slm_fxt = os.path.join(slm_dir, "slm.fxt")
    slength_counts = Counter()
    slen=1
    maxl=0
    #print training_rows
    for r in training_rows:
        r = r.strip()
               
        segs = r.split(BREAK) # chop the line up into segments
        for s in segs:
            slen = len(s.split())

            if slen > maxl:
                print "new max length = ", slen
                maxl = slen
                print "from seg: ", s
                print "from row: ", r

            if slen:
                slength_counts[slen]+=1

    #_ = raw_input("hit key")
                           
    els = list( slength_counts.elements() ) #Counter.elements() returns iterator that iterates across n instances of each element e where slength_counts[e]=n .. we make this into a list for plotting
    print els
    x_vals = range(0, max(els)+1)
    
    (shape, loc, scale) = gamma.fit(els, floc=0)
    gam_gen = gamma(shape, loc, scale) #use these model params to build a new gamma distrib/n generator
    write_slm(slm_fxt, x_vals, gam_gen)
    if do_plot:
        plot_graph(x_vals, gam_gen, els)
    compile_slm(slm_dir) #this last step compiles the slm to binary .fst format

def write_slm(slm_file, x_vals, gam_gen):
    if not write_slm:
        return
    lfile = codecs.open(slm_file,"w")
    lfile.truncate()
    
    maxp = 0

    p_acc= 0    
    for i in x_vals:
        #prob of being length i = p(i)
        
        #first state (0) has arc OUT and EPS arc
        #states 1-(L-1) have arcs OUT, EPS, and BREAK
        #state (L-1) has arc EPS and BREAK

        p_i = gam_gen.pdf(i) if i>0 else 0.0
        print "p("+str(i)+")=", p_i
        p_acc += p_i
        
        lfile.write("%d %d %s %s\n" % (i,i,EPS,EPS))
        if(i < max(x_vals)): #unless we're in the final state...
            #score_gt_i = -math.log( 1-gam_gen.cdf(i) )
            score_gt_i = -math.log( 1-p_i )
            lfile.write("%d %d %s %s %s\n" % (i,i+1,ANYWORD,ANYWORD,str(score_gt_i)))
        if(i>0):
            if(p_i>maxp):
                maxp = p_i
                print "new max p=",str(maxp)," at slen ",str(i)

            #score_i = -math.log(gam_gen.pdf(i))
            score_i = -math.log( p_i ) 
            lfile.write("%d 0 %s %s %s\n" % (i,BREAK,BREAK,str(score_i))) #arc back    

    lfile.write("0 0") #final state=0 with penalty=zero
    lfile.flush() 
    lfile.close()
    
    print "p_acc total=", p_acc
    #_ = raw_input("hit key")
    
def compile_slm(slm_dir):
    slm_fxt = os.path.join(slm_dir,"slm.fxt")
    slm_fst = os.path.join(slm_dir,"slm.fst")
    symfile = os.path.join(slm_dir,"..","slm_sym.dat")
    #fstcompile --isymbols=isyms.txt --osymbols=osyms.txt text.fst binary.fst
    sp.call(["fstcompile","--isymbols="+symfile,"--osymbols="+symfile, "--keep_isymbols", "--keep_osymbols", slm_fxt, slm_fst])
    
def plot_graph(x_vals, gam_gen, els):
    fig, ax = plt.subplots(1, 1)
    
    #build a list of expected values
    exp_vals = []
    for i in x_vals:
        #xv = (rv.cdf(i+1)-rv.cdf(i)) * len(els)
        xv = gam_gen.pdf(i) * len(els)
        print gam_gen.pdf(i), sum(els)
        exp_vals.append(xv)
   
    ax.plot(x_vals, exp_vals, 'r-', lw=2, label='gamma dist')
    ax.hist(els, bins=max(els), normed=False, histtype='stepfilled', alpha=0.2, label='samples')
    
    #code here lets you generate some random data for comparison
    #fake_els = rv.rvs(size=len(els))   
    #ax.hist(fake_els, bins=max(els), normed=False, histtype='stepfilled', alpha=0.2, label='gen/d') 
    ax.legend(loc='best', frameon=False)
    plt.show()