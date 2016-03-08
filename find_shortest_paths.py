'''
Created on Feb 24, 2016

@author: rjm49
'''
import glob, os
import subprocess as sp
from multistage_segmenter.common import DIR, PM_SUB_DIR,\
    JOINT_LM_CV_SLM_FILE_GLOBAL, COMP_SUB_DIR, SHP_SUB_DIR, OUTS_SUB_DIR
from multistage_segmenter.lm_gen import fstcompose
import errno


def fstshortestpath(inf, outf):
    sp.call(["fstshortestpath",inf,outf])

def fstprint(inf):
    op = sp.check_output(["fstprint",inf]) #call the print command and get the output as a byte string
    #print op
    op = op.decode() #convert byte string into unicode
    lines = op.split('\n')

    lines.pop() # remove empty line from end of list
    lines.append(lines.pop(0)) #for some reason the last state appears first so we must fix this...
    lines.reverse() # and then, the list is back to front, so we must also do this!

    outstr = ""
    for line in lines:
        #print (line)
        toks= line.split('\t')
        if len(toks)>3 and toks[3] != '<epsilon>':
            if toks[3] == '<break>':
                outstr += toks[3]
            else:
                outstr += toks[2]
            outstr += ' '
    return outstr.strip()
    
def process_outputs(cmp_dir, shp_dir, outs_dir):
    fs = glob.glob(os.path.join(cmp_dir,"*.fst"))
    for cmpf in fs:
        shpf = os.path.join(shp_dir,os.path.basename(cmpf))
        outf = os.path.join(outs_dir, os.path.basename(cmpf))
        fstshortestpath(cmpf, shpf)
        outstr = fstprint(shpf)
        of = open(outf,"w")
        of.write(outstr)
        of.flush()
        of.close()

if __name__ == '__main__':
#     lmdir = "eval1n"
    print "This script will find the shortest paths through the combined-model sentence FSTs"
#     lmdir = raw_input("Type in LM dir or hit return to use default [%s]" % lmdir) or lmdir
#     print "using ",lmdir
#     lmdir_global = os.path.join(DIR,lmdir)
    cmp_dir = os.path.join(DIR,COMP_SUB_DIR)
    shp_dir = os.path.join(DIR,SHP_SUB_DIR)
    outs_dir = os.path.join(DIR, OUTS_SUB_DIR)
    
    print "reading from", cmp_dir
    print "shortest path FSTs to", shp_dir
    print "segmented strings to", outs_dir
    
    try:
        os.makedirs(shp_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise 
    
    process_outputs(cmp_dir, shp_dir, outs_dir)
    print "done"
    
    