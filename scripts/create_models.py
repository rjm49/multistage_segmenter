#!/usr/bin/env python
'''
Created on 30 Nov 2015

@author: Russell
'''
import argparse
import os
import sys

from mseg.common import TRAIN_FILE_DEFAULT, read_file, BREAK, UNK, \
    LM_PRUNED, create_remap_table, get_basedir
from mseg.lm_utils import generate_normed_text_file, compile_lm, remap_lm, ngramshrink
from mseg.slm_utils import generate_slm_from_txt, create_slm_sym_file
import json


def main(args):
#     default_bdir = get_basedir()
    default_cfg = os.path.join(os.getcwd(),"mseg_config.cfg")
    
    parser = argparse.ArgumentParser()
    #parser.add_argument("base_dir", nargs='?', default= default_bdir, help="this is the working directory, all files and subdirs live under it; default is the current folder, i.e. "+default_bdir)
    parser.add_argument("config_file", nargs='?', default=default_cfg, help="configuration file for the multistage segmenter")
    parser.add_argument("lm_dir", nargs='?', default="lm_default", help="this is the directory in which to store the Language Model (LM) files")
    parser.add_argument("training_file", nargs='?', default=TRAIN_FILE_DEFAULT, help="name of CSV file that contains correctly annotated training examples")
    parser.add_argument("-o", "--order", type=int, default=4, help="sets the n-gramme order of the LM (default=4)")
    args = parser.parse_args()
    
    config_fname = args.config_file
    with open(config_fname) as data_file:
        config = json.load(data_file)
    base_dir = config['base_dir']
    
#     pm_dir = "pm_default" currently not used
    lm_dir = args.lm_dir
    tr_file = args.training_file
    ngo = args.order
    
    #SECTION ONE: dedicated to creating the Language Model files    
    lmdir_global = os.path.join(base_dir, lm_dir)
#     if(os.path.exists(lmdir_global)):
#         shutil.rmtree(lmdir_global)
#     os.makedirs(lmdir_global)

    tr_rows = read_file(os.path.join(base_dir, tr_file), ',', skip_header=True)

    rawtext_file = generate_normed_text_file(tr_rows, lmdir_global)
    
    #lm_syms = set([r[5] for r in tr_rows])
    
    lm_txt = open(rawtext_file, "r").readlines()
    lm_syms= set( open(rawtext_file, "r").read().split() )
    if BREAK in lm_syms: lm_syms.remove(BREAK)
    if UNK in lm_syms: lm_syms.remove(UNK)
    
    buildmod = "y"
    modfile = os.path.join(lmdir_global,"lm.mod")
    modpru = os.path.join(lmdir_global,LM_PRUNED)
    
    print "checking for LM file",modfile
    if(os.path.exists(modfile)):
        buildmod = raw_input("model file in "+lmdir_global+" already exists.  Overwrite? [n]").lower() or "n"
    
    if(not buildmod=="n"):
        modfile = compile_lm(rawtext_file, lmdir_global, lm_syms, ngo)
        
        print "Created unpruned lang model file:", modfile
        print "Now pruning LM..."
        ngramshrink(modfile, modpru)
        #print "Now minimising LM..."
        #lm_utils.fstmin(modpru,modpru)
        
        #we don't use the unpruned modfile again, so switch over to the pruned version here
        modfile = modpru
        
        remap_fname = os.path.join(lmdir_global,"lm_remap.dat")
        create_remap_table(lm_syms, remap_fname)
        
        
        osymfile = os.path.join(base_dir,"slm_sym.dat")
        create_slm_sym_file(osymfile)
        remap_lm(modfile, remap_fname, osymfile)
        print "remapped modfile output symbols"
                
    #create_converter(lmdir_global)
    #print "created converter."
    
#     slm_dir = raw_input("Type in SLM dir or hit return to match LM [%s]" % lm_dir) or lm_dir
#     slm_dir = os.path.join(base_dir,slm_dir)
#         
#     print "using ",slm_dir

    #put the SLM model into the same directory as its corresponding LM
    slm_dir = os.path.join(base_dir, lm_dir)

    generate_slm_from_txt(lm_txt, slm_dir, do_plot=True)
    #generate_slm(tr_rows, slm_dir, do_plot=False) # build the sentence length model, plot it so we can see it's sane
    print "slm generated from", tr_file, "in", slm_dir
    
    print "all constituent system files now compiled"

if __name__ == '__main__':
    main(sys.argv[1:])