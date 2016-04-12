'''
Created on Feb 24, 2016

@author: rjm49
'''
import glob, os
from multistage_segmenter.common import DIR, PM_SUB_DIR,\
     PILOT_FILE_NORMED, GOLD_SUB_DIR, read_file
from multistage_segmenter.lm_gen import fstcompose
import codecs

def generate_gold_files(rows):

    if(len(rows)==0):
        print "No data rows"
        exit(1)
        
    odir = os.path.join(DIR,GOLD_SUB_DIR)
    if(not os.path.exists(odir)):
        os.makedirs(odir)
               
    transcript_id = rows[0][0]#[1:-1]
    ofile = open_wfile(odir, transcript_id)
    
    for r in rows:
        next_transcript_id = r[0]
        w = r[5]#[1:-1]
        b = r[6]
        if(next_transcript_id != transcript_id):
            transcript_id = next_transcript_id
            ofile.flush()
            ofile.close()
            print "wrote",ofile
            ofile = open_wfile(odir, transcript_id)
        ofile.write(w+"\t"+b+"\n")
#         if(b):
#             ofile.write("<break>\n")
    ofile.flush()
    ofile.close()
    print "wrote",ofile

def open_wfile(odir,transcript_id):
    ofilename = os.path.join(odir,transcript_id+".gld")
    fhandle = codecs.open(ofilename, 'w')
    return fhandle

if __name__ == '__main__':
    lmdir = "eval1n"
    te_file = raw_input("enter test file name: [%s]" % PILOT_FILE_NORMED) or PILOT_FILE_NORMED
    te_rows = read_file(os.path.join(DIR, te_file), ',', skip_header=True)
    generate_gold_files(te_rows)