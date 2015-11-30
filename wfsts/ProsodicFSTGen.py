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
from common import read_file, UNK, DIR, DATAFILE,\
    PROBFILE, OUTSUBDIR, loadSymbolTable
from multistage_segmenter.common import ANYWORD, BREAK, EPS

write_files = False
write_slm = True
do_plot = False
unkify = False

lm_symbol_table = []

def writeLink(ofile,s,w,p):
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
        
    ofile.write("%d %d %s %s 0\n" % (s,s+1,w,wo))
    ofile.write("%d %d <epsilon> <epsilon> %f\n" % (s+1,s+2, not_weight))
    ofile.write("%d %d <epsilon> <break> %f\n" % (s+1,s+2, weight))

    
def writeFinalStateAndClose(ofile,s):
    if not write_files:
        return
    ofile.write("%d 0" % s)
    ofile.flush()
    ofile.close()
    print "wrote",ofilename


def plot_graph(x_vals, gam_gen):
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

if __name__ == '__main__':
    
    lm_symbol_table = loadSymbolTable()
    data_rows = read_file(os.path.join(DIR, DATAFILE), ',', skip_header=True)
    prob_rows = read_file(os.path.join(DIR, PROBFILE), ' ', skip_header=True)
    
    slength_counts = Counter()

    if len(data_rows)!=len(prob_rows):
        print len(data_rows), "in data not equal to prob rows:", len(prob_rows)
        exit(1)

    s=0
    ofile = None
    ofilename = None
    slen=0
    
    currseg = None

    if(len(data_rows)>0):
        spkid = data_rows[0][0][1:-1]
        currseg = spkid + "." + data_rows[0][1]
        ofilename = os.path.join(DIR,OUTSUBDIR,spkid+".fxt")
        
        if(write_files):
            ofile = codecs.open(ofilename, 'w')
    
        for r in data_rows:
            newspkid = r[0][1:-1]
            newseg = newspkid + "." + r[1]
            print newseg
            w = r[5][1:-1]
            #if(w not in lm_symbol_table):
            #    lm_symbol_table.append(w)
            
            if (newseg != currseg):
                slength_counts[slen]+=1
                currseg = newseg
                slen=0
                
                if(newspkid != spkid):
                    spkid = newspkid
                    writeFinalStateAndClose(ofile, s)
                    ofilename = os.path.join(DIR,OUTSUBDIR,spkid+".fxt")
                    s=0
                    if(write_files):
                        ofile = codecs.open(ofilename, 'w')
                    
            p = float( prob_rows.pop(0)[2] ) # pop the next probability value from our remaining prob_rows
            writeLink(ofile, s, w, p)
            slen += 1
            s += 2
                
        print "ended on rec.seg="+str(currseg)
        writeFinalStateAndClose(ofile, s)
        #saveSymbolTable(lm_symbol_table)
        print "wrote",ofilename        
    
    els = list( slength_counts.elements() )
    print els
    
    x_vals = range(0, max(els)+1)
    (shape, loc, scale) = gamma.fit(els, floc=0)
    gam_gen = gamma(shape, loc, scale) #use these model params to build a new gamma distrib/n generator
    
    write_slm(x_vals, gam_gen)
    ########################
    # OH YEAH, NOW PLOT IT #
    ########################
    if do_plot:
        plot_graph(x_vals, gam_gen)
        

    
    