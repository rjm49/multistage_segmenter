'''
Created on 30 Nov 2015

@author: Russell
'''
import json
import os
import sys

from common import read_file, load_symbol_table, LM_SYM_FILE, LM_PRUNED, \
    JOINT_LM_CV_SLM_FILE_GLOBAL
from pm.pm_utils import generate_pm_text_files, compile_pm_files
from scripts import find_shortest_paths, process_inputs
from scripts.process_inputs import compose_converters


if __name__ == '__main__':

    print "Number of arguments:", len(sys.argv), 'arguments.'
    print "Argument List:", str(sys.argv)
    args = sys.argv

    config = None
    with open('sample_config.cfg') as data_file:    
        config = json.load(data_file)
        
    base_dir = config['base_dir']
    batches = config['batches']

    for batch in batches:
        batch_dir = os.path.join(base_dir, batch['batch_dir'])
        lm_dir = os.path.join(base_dir, batch['language_model'])
        pm_dir = os.path.join(base_dir, batch['prosodic_model'])
        slm_dir = batch['length_model']
        te_file = batch['test_file']

        #lmdir_global = os.path.join(base_dir,lm_dir)
        batch_input_fst_dir = os.path.join(batch_dir, "speech_fsts")
        os.makedirs(batch_input_fst_dir)
    
        te_rows = read_file(os.path.join(base_dir, te_file), ',', skip_header=True)
    
        #ONE: make speech_fsts from te_rows  
        lm_syms = load_symbol_table(lm_dir, LM_SYM_FILE)
        
        probability_file = os.path.join(pm_dir, te_file+"-probabilities.dat")
        if not os.path.exists(probability_file):
            print "NO PROBABILITY FILE FOUND AT ", probability_file
            continue #go onto the next batch TODO should create prob file here!
        
        prob_rows = read_file(probability_file, ' ', skip_header=True)
    
        generate_pm_text_files(lm_syms, te_rows, prob_rows, max_count=-1)
        compile_pm_files(sym_dir=lm_dir)
        
        #TWO: Assuming all the other model files are complete, we should be good to go
        
        lang_mod = os.path.join(lm_dir,LM_PRUNED)
        
        pmlm_dir = os.path.join(batch_dir, "pm_lm_composed")
        all_models_dir = os.path.join(batch_dir, "pm_lm_slm")
        all_models_in_dir = os.path.join(all_models_dir, "composed")
        all_models_shp_dir = os.path.join(all_models_dir, "shortest")
        all_models_out_dir = os.path.join(all_models_dir, "output")
        
        pm_only_dir = os.path.join(batch_dir, "pm_only")
        pmshp_dir = os.path.join(pm_only_dir, "shortest")
        pmouts_dir = os.path.join(pm_only_dir, "output")
        
        pm_lm_dir = os.path.join(batch_dir, "pm_lm")
        pmlm_indir = os.path.join(pm_lm_dir, "composed")
        pmlmshp_dir = os.path.join(pm_lm_dir, "shortest")
        pmlmouts_dir = os.path.join(pm_lm_dir, "output")
    
        find_shortest_paths.stringify_shortest_paths(pm_dir, pmshp_dir, pmouts_dir)
        
        #now just use the pruned LM file without slen modifier
        process_inputs(pm_dir, lang_mod, pmlm_dir)
        find_shortest_paths.stringify_shortest_paths(pmlm_dir, pmlmshp_dir, pmlmouts_dir)
        
        #use combined LM and slen modifier
        compose_converters(pm_dir, lm_dir, slm_dir)
        process_inputs(pm_dir, JOINT_LM_CV_SLM_FILE_GLOBAL, all_models_in_dir)
        find_shortest_paths.stringify_shortest_paths(all_models_in_dir, all_models_shp_dir, all_models_out_dir)
