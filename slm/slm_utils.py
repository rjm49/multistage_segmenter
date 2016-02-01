'''
Created on Jan 16, 2016

@author: rjm49
'''
import codecs
from multistage_segmenter.common import DIR, ANYWORD, EPS, BREAK, SLM_FST_FILE_GLOBAL,\
    SLM_FXT_FILE_GLOBAL, SYM_FILE_GLOBAL, load_symbol_table, OUTSUBDIR, UNK,\
    CONV_FST_FILE_GLOBAL, CONV_FXT_FILE_GLOBAL
import os
from collections import Counter
from scipy.stats import gamma, norm
import matplotlib.pyplot as plt
import subprocess as sp

def create_converter():
    #print "creating converter...."
    syms = load_symbol_table()
    #ofilename = os.path.join(DIR,CONV_FXT_FILE)
    
    ofile = codecs.open(CONV_FXT_FILE_GLOBAL, 'w')
    
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
    #print "compiling...."
    sp.call(["fstcompile","--isymbols="+SYM_FILE_GLOBAL,"--osymbols="+SYM_FILE_GLOBAL, "--keep_isymbols", "--keep_osymbols", CONV_FXT_FILE_GLOBAL, CONV_FST_FILE_GLOBAL])
    #print "done...."    
    

def generate_slm(training_rows, do_plot):
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
    write_slm(x_vals, gam_gen)
    if do_plot:
        plot_graph(x_vals, gam_gen, els)
    compile_slm() #this last step compiles the slm to binary .fst format

def write_slm(x_vals, gam_gen):
    if not write_slm:
        return
    lfile = codecs.open(SLM_FXT_FILE_GLOBAL,"w")
    lfile.truncate()
    for i in x_vals:
        #prob of being length i = p(i)
        #except for last state for the max-length sentence, each state has an arc back and an arc out...
        #ln_prob_i = -math.log(gam_gen.pdf(i))
        score_i = gam_gen.pdf(i)
        #print score_i
        if(i < max(x_vals)): #unless we're in the final state...
            #ln_prob_gt_i = -math.log(1-gam_gen.cdf(i))
            score_gt_i = 1-gam_gen.cdf(i)
            #lfile.write("%d %d <rho> <rho> %f\n" % (i,i+1, score_gt_i)) #...arc out
            lfile.write("%d %d %s %s\n" % (i,i+1,ANYWORD,ANYWORD))
            lfile.write("%d %d %s %s %d\n" % (i,i,EPS,EPS,score_gt_i))
        if(i>0):
            #lfile.write("%d 0 <break> <break> %f\n" % (i, score_i)) #arc back
            lfile.write("%d 0 %s %s %d\n" % (i,BREAK,BREAK,score_i)) #arc back    
    #lfile.write("0 0") #final state=0 with penalty=zero
    lfile.write("0")
    lfile.flush() 
    lfile.close()
    
def compile_slm():
    #fstcompile --isymbols=isyms.txt --osymbols=osyms.txt text.fst binary.fst
    sp.call(["fstcompile","--isymbols="+SYM_FILE_GLOBAL,"--osymbols="+SYM_FILE_GLOBAL, "--keep_isymbols", "--keep_osymbols", SLM_FXT_FILE_GLOBAL, SLM_FST_FILE_GLOBAL])
    
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