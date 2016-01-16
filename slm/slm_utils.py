'''
Created on Jan 16, 2016

@author: rjm49
'''
import codecs
from multistage_segmenter.common import DIR, ANYWORD, EPS, BREAK
import os
from collections import Counter
from scipy.stats import gamma, norm
import matplotlib.pyplot as plt

def generate_slm(data_rows, do_plot):
    slength_counts = Counter()
    slen=0

    for r in data_rows:
        #print r
        is_boundary = int(r[6])
        if(not is_boundary):
            slen += 1
        else:
            print "adding slen=",(slen+1)
            slength_counts[slen+1]+=1
            slen = 0
        
    els = list( slength_counts.elements() ) #Counter.elements() returns iterator that iterates across n instances of each element e where slength_counts[e]=n .. we make this into a list for plotting

    print els
    
    x_vals = range(0, max(els)+1)
    (shape, loc, scale) = gamma.fit(els, floc=0)
    gam_gen = gamma(shape, loc, scale) #use these model params to build a new gamma distrib/n generator
    write_slm(x_vals, gam_gen)
    
    if do_plot:
        plot_graph(x_vals, gam_gen, els)

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