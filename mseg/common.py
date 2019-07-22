'''
Created on 3 Sep 2015

@author: Russell
'''
import codecs
import os

if(os.name=="nt"):
    DIR = "C:\\Users\\Russell\\mseg"
else:
    DIR = "/home/rjm49/mseg"

PM_SUB_DIR = "pm_fsts"
COMP_SUB_DIR = "all_composed"
SHP_SUB_DIR = "all_shortest"
OUTS_SUB_DIR = "all_output"
GOLD_SUB_DIR = "gold_standard"
#TEST_FILE_DEFAULT = "pilot-prosodicFeats_norm.csv"
TEST_FILE_DEFAULT = "eval1-prosodicFeats_norm_test.csv"
#PROBFILE = "predictions.dat"
#TRAIN_FILE_DEFAULT = "eval1-prosodicFeats_norm.csv"
TRAIN_FILE_DEFAULT = "eval1-prosodicFeats_norm_train.csv"
#TRAIN_FILE_DEFAULT = "switchboard-prosodicFeats_norm_train.csv"

#TEST_FILE="switchboard-prosodicFeats_norm_train.csv"
TRAIN_FILE="switchboard-prosodicFeats_norm_train.csv"

SYM_FILE="sym.dat"
LM_SYM_FILE="lm_sym.dat"
CONV_FST="conv.fst"
CONV_FXT="conv.fxt"

#SYM_FILE_GLOBAL = os.path.join(DIR,"vsys.sym")
SLM_FXT_FILE_GLOBAL = os.path.join(DIR,"slm.fxt")
SLM_FST_FILE_GLOBAL = os.path.join(DIR,"slm.fst")
#CONV_FXT_FILE_GLOBAL = os.path.join(DIR,"lm_slm_converter.fxt")
#CONV_FST_FILE_GLOBAL = os.path.join(DIR,"lm_slm_converter.fst")
JOINT_CV_SLM_FILE_GLOBAL = os.path.join(DIR,"cv_slm.fst")
JOINT_LM_CV_SLM_FILE_GLOBAL = os.path.join(DIR,"lm_cv_slm.fst")

LM_RAW = "lm.mod"
LM_PRUNED = "mod.pru"

UNK = "<unk>"
BREAK = "<break>"
ANYWORD = "<w>"
EPS = "<epsilon>"

PROSODIC_PREDICTION_FILE = "prosodic_predictions.dat"

def resolve_filenames():
    slm_dir = "eval1n"
    slm_dir = raw_input("Type in LM dir or hit return to use default [%s]" % slm_dir) or slm_dir
    print("using ",slm_dir)
    lmdir_global = os.path.join(DIR,slm_dir)
    all_syms = os.path.join(lmdir_global,SYM_FILE)
    lm_syms = os.path.join(lmdir_global,LM_SYM_FILE)
    tr_fname = os.path.join(lmdir_global,TRAIN_FILE_DEFAULT)
    te_file = os.path.join(lmdir_global,TEST_FILE_DEFAULT)
    


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
    print("number of tokens loaded:", len(listobj))
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

def load_symbol_table(fname):
    syms = []
    rows = read_file(fname, delim=None, skip_header=False)
    for r in rows:
        syms.append(r[0])
    return syms

def save_symbol_table(syms, fname):
    #now write the accompanying symbol table
    syms = list(syms)
    symf = codecs.open(fname, 'w')
    symf.truncate()
    syms.insert(0, EPS) # the epsilon symbol needs to be the zeroth item in the table
    syms.extend([BREAK,UNK,ANYWORD, "<nobreak>"]) # we add our custom utility symbols at the end, their actual position is unimportant
    for i,s in enumerate(syms):
        symf.write("%s\t%d\n" % (s,i))
        
    symf.flush()
    symf.close()
    print("wrote symbol table ", fname)
    
def create_remap_table(syms, fname):
    #now write the accompanying symbol table
    syms = list(syms)
    
    any_i = len(syms)+3
     
    symf = codecs.open(fname, 'w')
    symf.truncate()
    syms.insert(0, EPS) # the epsilon symbol needs to be the zeroth item in the table
    syms.extend([BREAK,UNK,ANYWORD]) # we add our custom utility symbols at the end, their actual position is unimportant
    for i,s in enumerate(syms):
        if i==0 or s==BREAK:
            symf.write("%d\t%d\n" % (i,i))       
        else:
            symf.write("%d\t%d\n" % (i,any_i))
        
    symf.flush()
    symf.close()
    print("wrote remap pairs table ", fname)
