'''
Created on 30 Nov 2015

@author: Russell
'''
import json
import os
import create_gold_files
import find_shortest_paths
import evaluate_output
import lm_gen
import shutil
import glob

from common import read_file, LM_SYM_FILE, load_symbol_table, SYM_FILE, \
    save_symbol_table, LM_PRUNED
from pm.pm_utils import generate_pm_text_files, compile_pm_files


def process_inputs(input_dir, lm_file, out_dir):
    if(not os.path.exists(input_dir)):
        print "FST source directory",input_dir,"does not exist - can't continue analysis without it!"
        exit(1)
       
    #create/refresh the working directory
    print "remaking ", out_dir
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir)
    
    fs = glob.glob(os.path.join(input_dir,"*.fst"))
    for f in fs:
        outf = os.path.join(out_dir ,os.path.basename(f))
        lm_gen.fstcompose(f, lm_file, outf)
        print "output:",outf

if __name__ == '__main__':

    config = None
    with open('sample_config.cfg') as data_file:    
        config = json.load(data_file)
        
    base_dir = config['base_dir']
    batches = config['batches']

    for batch in batches:
        if(not batch['run_batch']):
            continue
        
        print "RUNNING BATCH", batch
        
        batch_dir = os.path.join(base_dir, batch['batch_dir'])
        lm_dir = os.path.join(base_dir, batch['language_model'])
        pm_dir = os.path.join(base_dir, batch['prosodic_model'])
        slm_dir = os.path.join(base_dir,batch['length_model'])
        te_file = batch['test_file']

        #lmdir_global = os.path.join(base_dir,lm_dir)
        batch_input_fst_dir = os.path.join(batch_dir, "speech_fsts")
        if not os.path.exists(batch_input_fst_dir):
            os.makedirs(batch_input_fst_dir)
    
        te_rows = read_file(os.path.join(base_dir, te_file), ',', skip_header=True)
    
        gold_dir = os.path.join(batch_dir, "gold")
        create_gold_files.generate_gold_files(gold_dir, te_rows)
    
        #ONE: make speech_fsts from te_rows
        lmsym_fname = os.path.join(lm_dir,LM_SYM_FILE)
        lm_syms = load_symbol_table(lmsym_fname)
        
#         for s in lm_syms:
#             print s
#             
#         raw_input("press owt")
#             
        te_syms = [r[5] for r in te_rows]

        all_syms = set(lm_syms + te_syms)
        pmsym_fname = os.path.join(batch_dir, SYM_FILE)
        save_symbol_table(all_syms, pmsym_fname)
        
        probability_file = os.path.join(pm_dir, (te_file+"-probabilities.dat"))
        if not os.path.exists(probability_file):
            print "NO PROBABILITY FILE FOUND AT ", probability_file, " - you need to create this first with train_pm_svm.py"
            continue #go onto the next batch TODO should create prob file here!
        
        prob_rows = read_file(probability_file, ' ', skip_header=True)
    
        generate_pm_text_files(batch_input_fst_dir, lm_syms, te_rows, prob_rows, max_count=-1)
        compile_pm_files(batch_input_fst_dir, pmsym_fname, lmsym_fname)
        
        #TWO: Assuming all the other model files are complete, we should be good to go
        
        #lang_mod = os.path.join(lm_dir,LM_PRUNED)
        lang_mod = os.path.join(lm_dir,"mod.pru")
        
        all_models_dir = os.path.join(batch_dir, "pm_lm_slm")
        all_models_in_dir = os.path.join(all_models_dir, "composed")
        all_models_shp_dir = os.path.join(all_models_dir, "shortest")
        all_models_out_dir = os.path.join(all_models_dir, "output")
        
        pm_only_dir = os.path.join(batch_dir, "pm_only")
        pm_shp_dir = os.path.join(pm_only_dir, "shortest")
        pm_outs_dir = os.path.join(pm_only_dir, "output")
        
        pm_lm_dir = os.path.join(batch_dir, "pm_lm")
        pm_lm_in_dir = os.path.join(pm_lm_dir, "composed")
        pm_lm_shp_dir = os.path.join(pm_lm_dir, "shortest")
        pm_lm_outs_dir = os.path.join(pm_lm_dir, "output")
    
        print "joined up cretinous dir names"
    
        find_shortest_paths.stringify_shortest_paths(batch_input_fst_dir, pm_shp_dir, pm_outs_dir)
        
        #now just use the pruned LM file without slen modifier
        process_inputs(batch_input_fst_dir, lang_mod, pm_lm_in_dir)
        find_shortest_paths.stringify_shortest_paths(pm_lm_in_dir, pm_lm_shp_dir, pm_lm_outs_dir) #(input_dir, shortpath_dir, strings_dir
        
        #use combined LM and slen modifier
        slm_file = os.path.join(slm_dir,"slm.fst")
        lm_slm = os.path.join(batch_dir,"lm_slm.fst") 
        
        
        lm_gen.fstarcsort(slm_file, ilabel_sort=True)
        lm_gen.fstcompose(lang_mod, slm_file, lm_slm)
                
        process_inputs(batch_input_fst_dir, lm_slm, all_models_in_dir)
        find_shortest_paths.stringify_shortest_paths(all_models_in_dir, all_models_shp_dir, all_models_out_dir)
        
        evaluate_output.eval_segmenter_output(batch_dir)
