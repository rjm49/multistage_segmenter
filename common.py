'''
Created on 3 Sep 2015

@author: Russell
'''
import codecs
import os

WDIR = "C:\\Users\\Russell\\Documents\\Dropbox\\nlp_alta\\recreate_LG\\datafiles"
LDIR = "/home/rjm49/mseg"
DIR = LDIR #TODO crap hack - you can switch between windows and linux paths here
OUTSUBDIR = "seg_fsts"
PILOT_FILE = "pilot-prosodicFeats.csv"
PILOT_FILE_NORMED = "pilot-prosodicFeats_norm.csv"
PROBFILE = "predictions.dat"
EVAL1_FILE = "eval1-prosodicFeats.csv"
EVAL1_FILE_NORMED = "eval1-prosodicFeats_norm.csv"

SYM_FILE_GLOBAL = os.path.join(DIR,"vsys.sym")
SLM_FXT_FILE_GLOBAL = os.path.join(DIR,"slm.fxt")
SLM_FST_FILE_GLOBAL = os.path.join(DIR,"slm.fst")
CONV_FXT_FILE_GLOBAL = os.path.join(DIR,"lm_slm_converter.fxt")
CONV_FST_FILE_GLOBAL = os.path.join(DIR,"lm_slm_converter.fst")
JOINT_CV_SLM_FILE_GLOBAL = os.path.join(DIR,"cv_slm.fst")
JOINT_LM_CV_SLM_FILE_GLOBAL = os.path.join(DIR,"lm_cv_slm.fst")

UNK = "<unk>"
BREAK = "<break>"
ANYWORD = "<w>"
EPS = "<epsilon>"

# SLM_FXT_FILE = "slm.fxt"
# SLM_FST_FILE = "slm.fst"
# CONV_FXT_FILE = "lm_slm_converter.fxt"
# CONV_FST_FILE = "lm_slm_converter.fst"

# JOINT_CV_SLM_FILE = "cv_slm.fst"
#JOINT_LM_SLM_FILE = "lm_slm.fst"
# JOINT_LM_CV_SLM_FILE = "lm_cv_slm.fst" 

PROSODIC_PREDICTION_FILE = "prosodic_predictions.dat"

def full_path(fname):
    return os.path.join(DIR,fname)

## method to load data
def read_file(filename, delim=',', skip_header=False):
    listobj = []  # empty list
    reader = codecs.open(filename, 'r')  # open file
    if(skip_header):
        next(reader)  # skip header line
    ## for each line in file
    for line in reader:
        line = line.rstrip()  # remove trailing characters
        rowin = line.split(delim)  # split on commas
        listobj.append((rowin))  # append to eval1 list (list of lists)
    print "number of tokens loaded:", len(listobj)
    return listobj

def filter_data_rows(in_list, keep_headers=False, sel=range(7,30)):
    samples = []
    classes = []
    headers = [] # list for the new header row
    
    ci = 6 #class at six
    
    if(keep_headers):
        hrow = in_list[0]
        in_list = in_list[1:] #slice off the rest of the list
        for j in range(len(hrow)):
            #if j>=si and j<=xi:
            if j in sel:
                headers.append(hrow[j])

    for row in in_list:
        sample = []
        for i in range(len(row)):
            if i==ci:
                classes.append(float(row[i]))
            #elif i>=si and i<=xi: #0..29 rows
            elif i in sel:
                sample.append(float(row[i]))
        samples.append(sample)
        
    if(keep_headers):
        return (samples, classes, headers)
    else:
        return (samples, classes)

def load_symbol_table():
    if(not(SYM_FILE_GLOBAL)):
        return []
    
    syms = []
    rows = read_file(SYM_FILE_GLOBAL, " ", skip_header=False)
    for r in rows:
        syms.append(r[0])
    return syms

def save_symbol_table(syms):
    #now write the accompanying symbol table
    syms = list(syms)
    symf = codecs.open(SYM_FILE_GLOBAL, 'w')
    symf.truncate()
    syms.insert(0, EPS) # the epsilon symbol needs to be the zeroth item in the table
    syms.extend([BREAK,UNK,ANYWORD]) # we add our custom utility symbols at the end, their actual position is unimportant
    for i,s in enumerate(syms):
        symf.write("%s %d\n" % (s,i))
        
    symf.flush()
    symf.close()
    print("wrote symbol table ", SYM_FILE_GLOBAL)
    

