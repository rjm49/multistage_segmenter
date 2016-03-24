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
            outstr += '\n'
    return outstr.strip()
    
def process_outputs(input_dir, shortpath_dir, strings_dir):    
    fs = glob.glob(os.path.join(input_dir,"*.fst"))
    for inf in fs:
        shpf = os.path.join(shortpath_dir,os.path.basename(inf))
        outf = os.path.join(strings_dir, os.path.basename(inf))
        fstshortestpath(inf, shpf)
        outstr = fstprint(shpf)
        of = open(outf,"w")
        of.write(outstr)
        of.flush()
        of.close()
        print "shortest path ->",outf

if __name__ == '__main__':
#     lmdir = "eval1n"
    print "This script will find the shortest paths through the combined-model sentence FSTs"
#     lmdir = raw_input("Type in LM dir or hit return to use default [%s]" % lmdir) or lmdir
#     print "using ",lmdir
#     lmdir_global = os.path.join(DIR,lmdir)
    cmp_dir = os.path.join(DIR,COMP_SUB_DIR)
    shp_dir = os.path.join(DIR,SHP_SUB_DIR)
    outs_dir = os.path.join(DIR, OUTS_SUB_DIR)
    pm_dir = os.path.join(DIR, PM_SUB_DIR)

    pmshp_dir = os.path.join(DIR, "pm_shortest")
    pmouts_dir = os.path.join(DIR, "pm_output")
    
    pmlm_indir = os.path.join(DIR, "pm_lm_composed")
    pmlmshp_dir = os.path.join(DIR, "pm_lm_shortest")
    pmlmouts_dir = os.path.join(DIR, "pm_lm_output")
    
    print "reading from", cmp_dir
    print "shortest path FSTs to", shp_dir
    print "segmented strings to", outs_dir

    dirs = (cmp_dir, shp_dir, outs_dir, pm_dir, pmshp_dir, pmouts_dir, pmlm_indir, pmlmshp_dir, pmlmouts_dir)
    try:
        for d in dirs:
            if not os.path.exists(d):
                os.makedirs(d)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise 
        
    #process the multi-stage composed models first 
    process_outputs(cmp_dir, shp_dir, outs_dir)
    
    #next, do the prosodic-only models
    process_outputs(pm_dir, pmshp_dir, pmouts_dir)
    
    #next, do the PMLM models
    process_outputs(pmlm_indir, pmlmshp_dir, pmlmouts_dir)
    
    print "done"
    
    