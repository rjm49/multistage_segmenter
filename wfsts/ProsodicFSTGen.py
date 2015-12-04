'''
Created on 29 Jul 2015

@author: Russell
'''
import codecs
import os
import math
from collections import Counter
from scipy.stats import gamma, norm
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
from __builtin__ import True
from multistage_segmenter.common import read_file, UNK, DIR, DATAFILE,\
    PROBFILE, OUTSUBDIR, loadSymbolTable
from multistage_segmenter.common import ANYWORD, BREAK, EPS
from numpy.f2py.auxfuncs import throw_error

write_files = False
write_slm = True
do_plot = False
unkify = False

lm_symbol_table = []

def writeLink(ofile,state,w,p):
    if not write_files:
        return
#     ln_not_p = -math.log(1-p)
#     ln_p = -math.log(p)

    weight = p
    not_weight = 1-p
    
    if unkify and w not in lm_symbol_table:
        wo = UNK
    else:
        wo = w
        
    ofile.write("%d %d %state %state 0\n" % (state,state+1,w,wo))
    ofile.write("%d %d <epsilon> <epsilon> %f\n" % (state+1,state+2, not_weight))
    ofile.write("%d %d <epsilon> <break> %f\n" % (state+1,state+2, weight))

    
def write_final_state_and_close(ofile,state):
    if not write_files:
        return
    ofile.write("%d 0" % state)
    ofile.flush()
    ofile.close()
    print "wrote",ofile


def plot_graph(x_vals, gam_gen, els):
    # First of all, fit the samples to a gamma distribution to get the relevant shape params
    
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

def write_slm(x_vals, gam_gen):
    if not write_slm:
        return
    lfile = codecs.open(os.path.join(DIR,"slen.fxt"),"w")
    lfile.truncate()
    for i in x_vals:
        #prob of being length i = p(i)
        #except for last state for the max-length sentence, each state has an arc back and an arc out...
        #ln_prob_i = -math.log(gam_gen.pdf(i))
        score_i = gam_gen.pdf(i)
        print score_i
        
        if(i < max(x_vals)): #unless we're in the final state...
            #ln_prob_gt_i = -math.log(1-gam_gen.cdf(i))
            score_gt_i = 1-gam_gen.cdf(i)
            #lfile.write("%d %d <rho> <rho> %f\n" % (i,i+1, score_gt_i)) #...arc out
            lfile.write("%d %d %s %s\n" % (i,i+1,ANYWORD,ANYWORD))
            lfile.write("%d %d %s %s\n" % (i,i,EPS,EPS))
            
        if(i>0):
            #lfile.write("%d 0 <break> <break> %f\n" % (i, score_i)) #arc back
            lfile.write("%d 0 %s %s\n" % (i,BREAK,BREAK)) #arc back    
            
    #lfile.write("0 0") #final state=0 with penalty=zero
    lfile.write("0")
    lfile.flush() 
    lfile.close()

def generate_pm(data_rows, prob_rows):
    lm_symbol_table = loadSymbolTable()

    if len(data_rows)!=len(prob_rows):
        print len(data_rows), "in data not equal to prob rows:", len(prob_rows)
        exit(1)

    if(len(data_rows)==0):
        print "No data rows"
        exit(1)

    state=0
    transcript_id = data_rows[0][0][1:-1]
    ofilename = os.path.join(DIR,OUTSUBDIR,transcript_id+".fxt")
    ofile = codecs.open(ofilename, 'w') if write_files else None
    
    for r in data_rows:
        next_transcript_id = r[0][1:-1]
        w = r[5][1:-1]
        if(next_transcript_id != transcript_id):
            transcript_id = next_transcript_id
            write_final_state_and_close(ofile, state)
            state=0
            if(write_files):
                ofilename = os.path.join(DIR,OUTSUBDIR,transcript_id+".fxt")
                ofile = codecs.open(ofilename, 'w')
        p = float( prob_rows.pop(0)[1] ) # pop the next probability value from our remaining prob_rows
        writeLink(ofile, state, w, p)
        state += 2 # we advance the state counter two steps because each "link" writes two arcs
    write_final_state_and_close(ofile, state)
    #saveSymbolTable(lm_symbol_table)
    print "wrote",ofilename        
    

def generate_slm(data_rows):
    slength_counts = Counter()
    slen=0

    segment_id = data_rows[0][1]
    for r in data_rows:
        next_segment_id = r[1]
        if(next_segment_id <= segment_id): #this implies a reset of the segment number ... the only equal case should be 1==1 (for a single word sentence)
            slength_counts[slen]+=1
            slen = 0
        else:
            slen += 1
        
    els = list( slength_counts.elements() ) #Counter.elements() returns iterator that iterates across n instances of each element e where slength_counts[e]=n .. we make this into a list for plotting
    
    x_vals = range(0, max(els)+1)
    (shape, loc, scale) = gamma.fit(els, floc=0)
    gam_gen = gamma(shape, loc, scale) #use these model params to build a new gamma distrib/n generator
    
    write_slm(x_vals, gam_gen)

    if do_plot:
        plot_graph(x_vals, gam_gen, els)