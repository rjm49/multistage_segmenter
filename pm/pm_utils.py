'''
Created on Jan 16, 2016

@author: rjm49
'''
import codecs
import glob, shutil
import os

from common import DIR, PM_SUB_DIR, UNK, \
    EPS, BREAK
from lm_gen import fstcompile


write_files = True
write_slm = True
do_plot = False
unkify = True

def compile_pm_files(sym_dir):
    pmt_glob = os.path.join(DIR,PM_SUB_DIR,"*.fxt")
    pm_text_file_list = glob.glob(pmt_glob)
    for f in pm_text_file_list:
        bin_name = f[:-3]+"fst"
#         print "compiling", bin_name
        fstcompile(f, bin_name, sym_dir)
        print "compiled",bin_name

def generate_pm_text_files(known_syms, test_rows, prob_rows, max_count=-1):   
    if len(test_rows)!=len(prob_rows):
        print len(test_rows), "in data not equal to prob rows:", len(prob_rows)
        exit(1)

    if(len(test_rows)==0):
        print "No data rows"
        exit(1)
        
    pm_dir = os.path.join(DIR, PM_SUB_DIR)
    shutil.rmtree(pm_dir, ignore_errors=True)
    os.mkdir(pm_dir)
    
    state=0
    transcript_id = test_rows[0][0]#[1:-1]
    ofilename = os.path.join(pm_dir,transcript_id+".fxt")
    ofile = codecs.open(ofilename, 'w') if write_files else None

    rec_cnt=0
    for r,log_probs in zip(test_rows, prob_rows):
        next_transcript_id = r[0]
        w = r[5]#[1:-1]
        if(next_transcript_id != transcript_id):
            transcript_id = next_transcript_id
            rec_cnt+=1
            if(max_count>0 and rec_cnt >= max_count):
                break
            
            write_final_state_and_close(ofile, state)
            state=0
            if(write_files):
                ofilename = os.path.join(DIR,PM_SUB_DIR,transcript_id+".fxt")
                ofile = codecs.open(ofilename, 'w')

        np = float( log_probs[1] ) # pop the next probability value from our remaining prob_rows                
        p = float( log_probs[2] ) # pop the next probability value from our remaining prob_rows
        
        print "prob",p
        
        writeLink(ofile, known_syms, state, w, p, np)
        state += 2 # we advance the state counter two steps because each "link" writes two arcs
    write_final_state_and_close(ofile, state)
    #saveSymbolTable(lm_symbol_table)
    
def writeLink(ofile, symbols,state,w,p,np):
    #symbols = load_symbol_table()
    
    if not write_files:
        return

    # natural logs if base is not specified
#     weight = -math.log(p)
#     not_weight = -math.log(1-p)
    
    weight = p
    not_weight = np
    
    if unkify and w not in symbols:
        wo = UNK
    else:
        wo = w
    
    ofile.write("%d %d %s %s 0\n" % (state,state+1,w,wo))
    ofile.write("%d %d %s %s %f\n" % (state+1,state+2, EPS, EPS, not_weight))
    ofile.write("%d %d %s %s %f\n" % (state+1,state+2, EPS, BREAK, weight))
    
def write_final_state_and_close(ofile,state):
    if not write_files:
        return
    ofile.write("%d 0" % state)
    ofile.flush()
    ofile.close()
    print "wrote",ofile