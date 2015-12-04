'''
Created on 30 Nov 2015

@author: Russell
'''
from multistage_segmenter.common import EVAL1_FILE_NORMED, read_file, DATAFILE, DIR, PROBFILE,\
    loadSymbolTable, OUTSUBDIR
import os
from multistage_segmenter.wfsts.ProsodicFSTGen import generate_pm, generate_slm
import codecs
import string
import subprocess

lm_symbol_table = loadSymbolTable()
data_rows = read_file(os.path.join(DIR, EVAL1_FILE_NORMED), ',', skip_header=True)
prob_rows = read_file(os.path.join(DIR, PROBFILE), ' ', skip_header=True)

def generate_lm(data):
    pass

#This method generates normalised data files from the source CSV.  These need to be all-caps, punc-free, in order to feed into the OpenGRM language modelling libraries...
def generate_lm_files(data):
    rec_id = None
    writer = None
    first = True
    for r in data:
        if rec_id != r[0]:
            rec_id = r[0]
            if writer:
                writer.close()
            writer = codecs.open(os.path.join(DIR,OUTSUBDIR,rec_id+".txt"), 'w')
            first = True      
        w = r[5]
        #remove punctuation
        w = w.translate(string.maketrans("",""), string.punctuation)
        if first: #by default we add a space, but we skip it for the first word of each recording
            first=False
        else:
            pass
            writer.write(' ')
        writer.write(w)
        writer.write(' <break>')
    writer.close()

def generate_lm_file(data):
    rec_id = None
    first = True
    writer = codecs.open(os.path.join(DIR,OUTSUBDIR,"normed.txt"), 'w')
    for r in data:
        if rec_id != r[0]:
            if not first:
                writer.write('<break>\n') #finish off the segment
            else:
                first=False
            rec_id = r[0]
        w = r[5].translate(string.maketrans("",""), string.punctuation) #remove punctuation  
        writer.write(w)
        writer.write(' ')
    writer.flush()
    writer.close()

if __name__ == '__main__':
    #generate pm
    #generate_pm(data_rows) #this should produce the fxt files on disc that can feed into the FST composition
    #generate slm
    #generate_slm(data_rows) #produces the SLM fxt
    #generate lm
    #generate_lm(data_rows) #produces the LM fxts (one per transcript)
    generate_lm_file(data_rows)

    
    