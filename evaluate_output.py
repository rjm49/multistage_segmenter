'''
Created on Feb 24, 2016

@author: rjm49
'''
import glob, os
from multistage_segmenter.common import DIR, PM_SUB_DIR,\
     PILOT_FILE_NORMED, GOLD_SUB_DIR, read_file, PROBFILE, load_symbol_table,\
    LM_SYM_FILE, OUTS_SUB_DIR, BREAK
from multistage_segmenter.lm_gen import fstcompose
import codecs
from multistage_segmenter.pm.pm_utils import generate_pm_text_files,\
    compile_pm_files

#this lets us compare the contents of two files
def compare_rows(gold_rows, algo_rows):
    fps=tps=fns=tns = 0.0 #reset our counters for each record, as floats
    nobrks_out=nobrks_gold = 0

    while gold_rows != []:
        gold_row = gold_rows.pop(0)
        out_row = algo_rows.pop(0)
        #print gold_row,"vs",out_row
        
        if(gold_row == out_row):
            if gold_row == BREAK:
                nobrks_gold += 1
                nobrks_out += 1
                tps += 1
            else:
                tns += 1
        else: #either outrow has missed a break, or added one too many
            if gold_row == BREAK: #out missed a break
                nobrks_gold+=1
                fns += 1
                gold_row = gold_rows.pop(0)
            else:
                nobrks_out+=1
                fps += 1
                out_row = algo_rows.pop(0)
    
    remaining = len(algo_rows)
    if(remaining)>0:
        print "Dangling output row remaining=", remaining
        print algo_rows
        fps+=1
    
    #print tps, tns
    #print fps, fns
    p = 1.0 if (tps+fps==0) else (tps / (tps + fps)) #cases found / (cases found + wrongly assumed cases)
    r = 1.0 if (tps+fns==0) else (tps / (tps + fns)) #cases found / (cases found + cases not found)
     
    #print p, r
    F = 0 if (p+r==0) else (2*p*r / (p+r))
    print outf,"- p/r/F:",p,r,F

    recid = os.path.basename(outf)[:-4]

    return (recid, nobrks_gold, nobrks_out, tps, fps, fns, tns, p,r,F)


if __name__ == '__main__':
    lmdir = "eval1n"
    
    gold_dir = os.path.join(DIR,GOLD_SUB_DIR)
    #output_dir = os.path.join(DIR,OUTS_SUB_DIR)
    
    output_dirs = ("pm_output", "pm_lm_output", OUTS_SUB_DIR)

    prF = "p,r,F"
    out_rows = []

    report_fname = os.path.join(DIR,"segmenter_report.csv")
    rfile = codecs.open(report_fname,"w")
    headers = "RECID,G#B,O#B,TPOS,FPOS,FNEG,(TNEG)"

    report = {}
    for d in output_dirs:
                
        gfps=gtps=gfns=gtns = 0.0
        totF=avF = 0.0
        n=0.0
            
        outs = glob.glob(os.path.join(DIR, d,"*.fst"))
        for outf in outs:
            goldf = os.path.basename(outf)[:-4]+".gld"
            algo_rows = codecs.open(os.path.join(DIR, d,outf), "r").read().splitlines()        
            gold_rows = codecs.open(os.path.join(gold_dir,goldf), "r").read().splitlines()
            
            tup = compare_rows(gold_rows, algo_rows)
            
            recid=tup[0]
            
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