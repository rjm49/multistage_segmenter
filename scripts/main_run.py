'''
Created on 30 Nov 2015

@author: Russell
'''
import json
import os
import sys

from common import read_file, load_symbol_table, LM_SYM_FILE, LM_PRUNED, \
    JOINT_LM_CV_SLM_FILE_GLOBAL, save_symbol_table, SYM_FILE
from pm.pm_utils import generate_pm_text_files, compile_pm_files
import process_inputs
import find_shortest_paths
import create_gold_files

if __name__ == '__main__':

    config = None
    with open('sample_config.cfg') as data_file:    
        config = json.load(data_file)
        
    base_dir = config['base_dir']
    batches = config['batches']

    for batch in batches:
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
    
        create_gold_files.generate_gold_files(os.path.join(batch_dir,"gold"), te_rows)
    
        #ONE: make speech_fsts from te_rows
        lmsym_fname = os.path.join(lm_dir,LM_SYM_FILE)
        lm_syms = load_symbol_table(lmsym_fname)
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
        
        lang_mod = os.path.join(lm_dir,LM_PRUNED)
        
        all_models_dir = os.path.join(batch_dir, "pm_lm_slm")
        all_models_in_dir = os.path.join(all_models_dir, "composed")
        all_models_shp_dir = os.path.join(all_models_dir, "shortest")
        all_models_out_dir = os.path.join(all_models_dir, "output")
        
        pm_only_dir = os.path.join(batch_dir, "pm_only")
        pm_shp_dir = os.path.join(pm_only_dir, "shortest")
        pm_outs_dir = os.path.join(pm_only_dir, "output")
        
        pm_lm_dir = os.path.join(batch_dir, "pm_lm")
        pm_lm_indir = os.path.join(pm_lm_dir, "composed")
        pm_lm_shp_dir = os.path.join(pm_lm_dir, "shortest")
        pm_lm_outs_dir = os.path.join(pm_lm_dir, "output")
    
        print "joined up cretinous dir names"
    
        find_shortest_paths.stringify_shortest_paths(batch_input_fst_dir, pm_shp_dir, pm_outs_dir)
        
        #now just use the pruned LM file without slen modifier
        process_inputs.process_inputs(batch_input_fst_dir, lang_mod, pm_lm_dir)
        find_shortest_paths.stringify_shortest_paths(pm_lm_dir, pm_lm_shp_dir, pm_lm_outs_dir)
        
        #use combined LM and slen modifier
        slm_file = os.path.join(slm_dir,"slm.fst")
        cv_file = os.path.join(lm_dir,"conv.fst")        
        
        converter_fname = process_inputs.compose_converters(batch_dir, lang_mod, cv_file, slm_file)
        process_inputs.process_inputs(batch_input_fst_dir, converter_fname, all_models_in_dir)
        find_shortest_paths.stringify_shortest_paths(all_models_in_dir, all_models_shp_dir, all_models_out_dir)
