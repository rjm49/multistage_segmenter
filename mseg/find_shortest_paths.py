'''
Created on Feb 24, 2016

@author: rjm49
'''
import errno
import glob, os
import shutil

from mseg.common import PM_SUB_DIR, \
    COMP_SUB_DIR, SHP_SUB_DIR, OUTS_SUB_DIR, EPS, \
    BREAK, get_basedir
from mseg.lm_utils import nshortest_path
import subprocess as sp

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
    
    
def fstprint2(full_fname):
    print "reading", full_fname
    
    op = sp.check_output(["fstprint",full_fname]) #call the print command and get the output as a byte string
    #print op
    op = op.decode() #convert byte string into unicode
    lines = op.split('\n')

    lines.pop() # remove empty line from end of list
    lines.append(lines.pop(0)) #for some reason the last state appears first so we must fix this...
    lines.reverse() # and then, the list is back to front, so we must also do this!

    outstr = ""
    was_break = False
    last_tok=""
    first = True

    for line in lines:
        #print (line)
        toks= line.split('\t')
        if (len(toks)>3):
            if(toks[2]!=EPS):
                if first:
                    first=False
                else:
                    outstr+= (last_tok + "\t" + ("1" if was_break else "0") + "\n")
                was_break = False
                last_tok=toks[2]
            elif(toks[3]==BREAK):
                was_break = True

    outstr+= (last_tok + "\t" + ("1" if was_break else "0") + "\n")
    return outstr.strip()
    
def stringify_shortest_paths(input_dir, shortpath_dir, strings_dir):    
    if(not os.path.exists(input_dir)):
        print "FST source directory",input_dir,"does not exist - can't continue analysis without it!"
        exit(1)
       
    #create/refresh the working directories 
    for d in (shortpath_dir, strings_dir):
        print "re-making",d
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    
    descriptor = os.path.join(input_dir,"*.fst")
    print "processing files matching:", descriptor
    fs = glob.glob(descriptor)
    for inf in fs:
        fname = os.path.basename(inf)
        shpf = os.path.join(shortpath_dir, fname)
        outf = os.path.join(strings_dir, fname)
        print "Finding shortest path:",inf,"->",outf
        print "First, create temp file:", shpf
        nshortest_path(inf, shpf, 1)
        outstr = fstprint2(shpf)
        of = open(outf,"w")
        of.write(outstr)
        of.flush()
        of.close()    


def convert_to_single_file(match_str, input_dir):
    descriptor = os.path.join(input_dir,match_str)
    print "processing files matching:", descriptor
    fs = glob.glob(descriptor)
    txfile = open(os.path.join(input_dir,"all.txt"), "w")
    outlines = []
    for inf in sorted(fs):
        #fname = os.path.basename(inf)
        f= open(inf)  
        outstr = ""
        for ln in f:
            tup = ln.split()
            #txfile.write(tup[0]+" ")
            outstr += tup[0]+" "
            #print tup[1]
            if tup[1]=='1':
                outstr += "<break> "
                #txfile.write("<break> ")
        outlines.append(outstr)
    txfile.writelines(outlines)
    txfile.close()
    print "wrote",txfile
    return " ".join(outlines)

if __name__ == '__main__':
#     lmdir = "eval1n"
    print "This script will find the shortest paths through the combined-model sentence FSTs"
#     lmdir = raw_input("Type in LM dir or hit return to use default [%s]" % lmdir) or lmdir
#     print "using ",lmdir
#     lmdir_global = os.path.join(base_dir,lmdir)

    base_dir = get_basedir()

    cmp_dir = os.path.join(base_dir,COMP_SUB_DIR)
    shp_dir = os.path.join(base_dir,SHP_SUB_DIR)
    outs_dir = os.path.join(base_dir, OUTS_SUB_DIR)
    pm_dir = os.path.join(base_dir, PM_SUB_DIR)

    pmshp_dir = os.path.join(base_dir, "pm_shortest")
    pmouts_dir = os.path.join(base_dir, "pm_output")
    
    pmlm_indir = os.path.join(base_dir, "pm_lm_composed")
    pmlmshp_dir = os.path.join(base_dir, "pm_lm_shortest")
    pmlmouts_dir = os.path.join(base_dir, "pm_lm_output")
    
    print "reading from", cmp_dir
    print "shortest path FSTs to", shp_dir
    print "segmented strings to", outs_dir

    dirs = ((cmp_dir, shp_dir, outs_dir), (pm_dir, pmshp_dir, pmouts_dir), (pmlm_indir, pmlmshp_dir, pmlmouts_dir))
    try:
        for tupl in dirs:
            for d in tupl:
#                 if os.path.exists(d):
#                     #print "removing",d 
#                     shutil.rmtree(d)
                os.makedirs(d)
                print "made",d
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
        
    #process the multi-stage composed models first 
    for tupl in dirs:
        (compostion_dir, shortest_path_dir, output_dir) = tupl
        print "analysing shortest paths:", compostion_dir, shortest_path_dir, "->", output_dir
        stringify_shortest_paths(compostion_dir, shortest_path_dir, output_dir)
    
    print "done"
    
    