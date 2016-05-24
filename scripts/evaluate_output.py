'''
Created on Feb 24, 2016

@author: rjm49
'''
import codecs
import glob, os

from common import DIR, PM_SUB_DIR, \
     TEST_FILE_DEFAULT, GOLD_SUB_DIR, read_file, load_symbol_table, \
    LM_SYM_FILE, OUTS_SUB_DIR, BREAK
from lm_gen import fstcompose
from pm.pm_utils import generate_pm_text_files, \
    compile_pm_files


#this lets us compare the contents of two files
def compare_rows(_recid, gold_rows, algo_rows):
    fps=tps=fns=tns = 0.0 #reset our counters for each record, as floats
    nobrks_out=nobrks_gold = 0

    for (gold_row, algo_row) in zip(gold_rows, algo_rows):
        gold_row = gold_row.split("\t")
        algo_row = algo_row.split("\t")
        
        gold_is_brk = int(gold_row[1])
        algo_is_brk = int(algo_row[1])
        
        #print gold_row,"vs",algo_row
        #print gold_is_brk, algo_is_brk
        
        if(gold_is_brk):
            nobrks_gold += 1
            if(algo_is_brk):
                tps+=1
                nobrks_out += 1
            else:
                fns+=1
        else:
            if(algo_is_brk):
                fps+=1
                nobrks_out += 1
            else:
                tns+=1
                
    #print tps, tns
    #print fps, fns
    p = 1.0 if (tps+fps==0) else (tps / (tps + fps)) #cases found / (cases found + wrongly assumed cases)
    r = 1.0 if (tps+fns==0) else (tps / (tps + fns)) #cases found / (cases found + cases not found)
     
    #print p, r
    F = 0 if (p+r==0) else (2*p*r / (p+r))

    return (_recid, nobrks_gold, nobrks_out, tps, fps, fns, tns, p,r,F)


if __name__ == '__main__':

    base_dir = "/home/rjm49/mseg/"
    batch_dir= os.path.join(base_dir,"Pb_Lb_Sb(heldout)")
    
    lmdir = "eval1n"   
    gold_dir = os.path.join(batch_dir,"gold")    
    output_dirs = ("pm_lm_slm", "pm_only", "pm_lm")
    
    prF = "p,r,F"
    out_rows = []

    report_fname = os.path.join(batch_dir,"segmenter_report.csv")
    rfile = codecs.open(report_fname,"w")
    headers = "RECID,G#B,O#B,TPOS,FPOS,FNEG,(TNEG)"

    report = {}
    for d in output_dirs:
        d = os.path.join(batch_dir,d,"output")
            
        print "dir is:", d
        gfps=gtps=gfns=gtns = 0.0
        totF=avF = 0.0
        n=0.0
            
        outs = glob.glob(os.path.join(d,"*.fst"))
        print "found",len(outs),"output files in",d
        for outf in outs:
#            print "algo_rows from:",outf
            recid = os.path.basename(outf)[:-4]
            goldf = recid+".gld"
            algo_rows = codecs.open(os.path.join(d,outf), "r").read().splitlines()        
            gold_rows = codecs.open(os.path.join(gold_dir,goldf), "r").read().splitlines()
            
            tup = compare_rows(recid, gold_rows, algo_rows)
                        
 #           print tup
                        
            gtps+=tup[3] #add the t/f p/n scores to the global totals
            gfps+=tup[4]
            gfns+=tup[5]
            gtns+=tup[6]
            totF += tup[9] #add the F score from this row to the overall F total
            n += 1.0 # for averaging later
            
            if(recid in report.keys()):
                report[recid]= report[recid] + tup[-3:]
            else:
                report[recid]= tup
                
            #print report[recid]
    
        headers = headers + ", "+ d + ": " + prF
    
        avF = totF/n
        print "for",d,"average F=",avF
               
        #calculate global versions of p,r,F i.e. if we assume there is just a single unified string of tokens
        gp = 1.0 if (gtps+gfps==0) else (gtps / (gtps + gfps)) #cases found / (cases found + wrongly assumed cases)
        gr = 1.0 if (gtps+gfns==0) else (gtps / (gtps + gfns)) #cases found / (cases found + cases not found)    
        gF = 0 if (gp+gr==0) else (2*gp*gr / (gp+gr))
        print "Total: - gp/gr/gF:",gp,gr,gF
    
        # check also the average (mean) F across files    

    rfile.write(headers+"\n")
    
    keys = report.keys()
    keys.sort()
    
    for k in keys:
        outstr = ",".join(map(str,report[k]))
        rfile.write(outstr + "\n")
    rfile.flush()
    rfile.close()