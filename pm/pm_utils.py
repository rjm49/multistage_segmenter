'''
Created on Jan 16, 2016

@author: rjm49
'''
from multistage_segmenter.common import loadSymbolTable, DIR, OUTSUBDIR, UNK
import os
import codecs

write_files = False
write_slm = True
do_plot = False
unkify = False

lm_symbol_table = loadSymbolTable()

def generate_pm(data_rows, prob_rows):
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