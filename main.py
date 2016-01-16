'''
Created on 30 Nov 2015

@author: Russell
'''
from multistage_segmenter.common import EVAL1_FILE_NORMED, read_file, DATAFILE, DIR, PROBFILE,\
    loadSymbolTable, OUTSUBDIR
import os
import codecs
import string
from multistage_segmenter.lm_gen import farcompilestrings, ngramcount, ngrammake
from multistage_segmenter.pm.pm_utils import generate_pm
from multistage_segmenter.slm.slm_utils import generate_slm

def generate_lm(data):
    generate_normed_text_file(data)
    farcompilestrings() #create test.far from the normed text file
    ngramcount(3) #hopefully this combines all the segments into a single set of unified counts
    ngrammake() #this creates the ngram model file

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
                writer.write('<break>'+trailer) #finish off the segment
            else:
                first=False
            rec_id = r[0]
            seg_id = r[1]
        w = r[5].translate(string.maketrans("",""), string.punctuation) #remove punctuation  
        writer.write(w)
        writer.write(' ')
    writer.flush()
    writer.close() 

if __name__ == '__main__':
    lm_symbol_table = loadSymbolTable()
    print "reading raw annotated token data from", EVAL1_FILE_NORMED
    data_rows = read_file(os.path.join(DIR, EVAL1_FILE_NORMED), ',', skip_header=True)
    #print [r[5] for r in data_rows[0:100]]
    print 'normalising tokens...'
    for r in data_rows:
        r[5] = r[5].translate(string.maketrans("",""), string.punctuation)
    
    #print [r[5] for r in data_rows[0:100]]
    
    #generate lm
    generate_lm(data_rows)
    ###LANGUAGE MODEL FILES ARE READY AT THIS POINT
    generate_slm(data_rows, do_plot=True) # build the sentence length model, plot it so we can see it's sane   

    prob_rows = read_file(os.path.join(DIR, PROBFILE), ' ', skip_header=True)
    
    #generate pm
    generate_pm(data_rows, prob_rows) #this should produce the fxt files on disc that can feed into the FST composition
    #generate slm
    #generate_slm(data_rows) #produces the SLM fxt
    