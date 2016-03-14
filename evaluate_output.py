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


def open_wfile(odir,transcript_id):
    ofilename = os.path.join(odir,transcript_id+".gld")
    fhandle = codecs.open(ofilename, 'w')
    return fhandle

if __name__ == '__main__':
    lmdir = "eval1n"
    
    gold_dir = os.path.join(DIR,GOLD_SUB_DIR)
    output_dir = os.path.join(DIR,OUTS_SUB_DIR)
    
    report_fname = os.path.join(DIR,"segmenter_report.csv")
    rfile = codecs.open(report_fname,"w")
    rfile.write("RECID,G#B,O#B,TPOS,FPOS,FNEG,(TNEG),P,R,F\n")

    gfps=gtps=gfns=gtns = 0.0
    totF=avF = 0.0
    n=0.0
        
    outs = glob.glob(os.path.join(output_dir,"*.fst"))
    for outf in outs:
        goldf = os.path.basename(outf)[:-4]+".gld"
        output_rows = codecs.open(os.path.join(output_dir,outf), "r").read().splitlines()        
        gold_rows = codecs.open(os.path.join(gold_dir,goldf), "r").read().splitlines()
        
        #print output_rows
        #print gold_rows
        
        #raw_input()
        
        fps=tps=fns=tns = 0.0 #reset our counters for each record, as floats
        nobrks_out=nobrks_gold = 0

        while gold_rows != []:
            gold_row = gold_rows.pop(0)
            out_row = output_rows.pop(0)
            #print gold_row,"vs",out_row
            
            if(gold_row == out_row):
                if gold_row == BREAK:
                    nobrks_gold += 1
                    nobrks_out += 1
                    tps += 1
                    gtps += 1
                else:
                    tns += 1
                    gtns += 1
            else: #either outrow has missed a break, or added one too many
                if gold_row == BREAK: #out missed a break
                    nobrks_gold+=1
                    fns += 1
                    gfns += 1
                    gold_row = gold_rows.pop(0)
                else:
                    nobrks_out+=1
                    fps += 1
                    gfps += 1
                    out_row = output_rows.pop(0)
        
        #print tps, tns
        #print fps, fns
        p = 1.0 if (tps+fps==0) else (tps / (tps + fps)) #cases found / (cases found + wrongly assumed cases)
        r = 1.0 if (tps+fns==0) else (tps / (tps + fns)) #cases found / (cases found + cases not found)
         
        #print p, r
        F = 0 if (p+r==0) else (p*r / (p+r))
        print outf,"- p/r/F:",p,r,F
        outstr = os.path.basename(outf)[:-4]
        outstr+= ","+str(nobrks_gold)
        outstr+= ","+str(nobrks_out)
        for i in (tps,fps,fns,tns):
            outstr += (","+ str(int(i)))
        for j in (p,r,F):
            outstr += (","+ str(j))
        rfile.write(outstr + "\n")

        totF += F
        n += 1.0

    rfile.flush()
    rfile.close()
    
    #calculate global versions of p,r,F i.e. if we assume there is just a single unified string of tokens
    gp = 1.0 if (gtps+gfps==0) else (gtps / (gtps + gfps)) #cases found / (cases found + wrongly assumed cases)
    gr = 1.0 if (gtps+gfns==0) else (gtps / (gtps + gfns)) #cases found / (cases found + cases not found)    
    gF = 0 if (gp+gr==0) else (gp*gr / (gp+gr))
    print outf,"- - - - gp/gr/gF:",gp,gr,gF

    # check also the average (mean) F across files    
    avF = totF/n
    print "average F=",avF