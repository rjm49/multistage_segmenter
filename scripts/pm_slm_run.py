'''
Created on 30 Nov 2015

@author: Russell
'''
import json
import os
from mseg import create_gold_files
from mseg import find_shortest_paths
from mseg import evaluate_output
from mseg import lm_utils
import shutil
import glob

from mseg.common import read_file, LM_SYM_FILE, load_symbol_table, SYM_FILE, \
    save_symbol_table, ANYWORD
from mseg.pm_utils import generate_pm_text_files, compile_pm_files
from mseg.find_shortest_paths import convert_to_single_file
from mseg import bleu_break_scorer
import nltk

#nltk.download()

do_build = True
eq_chance=  True

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
        lm_utils.fstcompose(f, lm_file, outf)
        print "output:",outf

if __name__ == '__main__':
    print "running main_run"
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
        
        use_pos_tags = batch.get('use_pos_tags', False)

        gold_dir = os.path.join(batch_dir, "gold")
        all_models_dir = os.path.join(batch_dir, "pm_lm_slm")
        
        all_models_out_dir = os.path.join(all_models_dir, "output")
        all_models_in_dir = os.path.join(all_models_dir, "composed")
        all_models_shp_dir = os.path.join(all_models_dir, "shortest")
        
        pm_only_dir = os.path.join(batch_dir, "pm_only")
        pm_shp_dir = os.path.join(pm_only_dir, "shortest")
        pm_outs_dir = os.path.join(pm_only_dir, "output")
        
#         pm_lm_dir = os.path.join(batch_dir, "pm_lm")
#         pm_lm_in_dir = os.path.join(pm_lm_dir, "composed")
#         pm_lm_shp_dir = os.path.join(pm_lm_dir, "shortest")
#         pm_lm_outs_dir = os.path.join(pm_lm_dir, "output")

        pm_slm_dir = os.path.join(batch_dir, "pm_slm")
        pm_slm_in_dir = os.path.join(pm_slm_dir, "composed")
        pm_slm_shp_dir = os.path.join(pm_slm_dir, "shortest")
        pm_slm_outs_dir = os.path.join(pm_slm_dir, "output")


        if(do_build): 
            #lmdir_global = os.path.join(base_dir,lm_dir)
            batch_input_fst_dir = os.path.join(batch_dir, "speech_fsts")
            if not os.path.exists(batch_input_fst_dir):
                os.makedirs(batch_input_fst_dir)
        
            te_rows = read_file(os.path.join(base_dir, te_file), ',', skip_header=True)
        
            create_gold_files.generate_gold_files(gold_dir, te_rows)
        
            #ONE: make speech_fsts from te_rows
            if(eq_chance):
                lmsym_fname = os.path.join(base_dir, "slm_sym.dat")
            else:
                lmsym_fname = os.path.join(lm_dir,LM_SYM_FILE)

            lm_syms = load_symbol_table(lmsym_fname)
            
            
            te_syms = [r[5] for r in te_rows]
            all_syms = set(lm_syms + te_syms)
            pmsym_fname = os.path.join(batch_dir, SYM_FILE)
            save_symbol_table(all_syms, pmsym_fname)
            
            probability_file = os.path.join(pm_dir, (te_file+"-probabilities.dat"))
            if not os.path.exists(probability_file):
                print "NO PROBABILITY FILE FOUND AT ", probability_file, " - you need to create this first with train_pm.py"
                continue #go onto the next batch TODO should create prob file here!
            
            prob_rows = read_file(probability_file, ' ', skip_header=True)
        
            if use_pos_tags:
                segs = []
                for t in te_rows:
                    if not t[0] in segs:
                        segs.append(t[0])

                tox=[]
                cntr = 0
                emission_vals = []
                for seg in segs:
                    ws = [t[5] for t in te_rows if t[0]==seg ]
                    print "For seg=",seg,"got these tokens:",tox
                    tags = nltk.pos_tag(ws)
                    print "tags=",tags
                    for tag in tags:
                        emission_vals.append(tag[1])
                
                _ = raw_input("hit key")
            elif eq_chance:
                emission_vals = [ANYWORD for t in te_rows]
            else:
                emission_vals = [t[5] for t in te_rows]
                        
        
            generate_pm_text_files(batch_input_fst_dir, lm_syms, te_rows, prob_rows, max_count=-1, emission_values=emission_vals, equal_chance=eq_chance)
            
            compile_pm_files(batch_input_fst_dir, pmsym_fname, lmsym_fname)
            
            #TWO: Assuming all the other model files are complete, we should be good to go
            
            #lang_mod = os.path.join(lm_dir,LM_PRUNED)
            
            if eq_chance:
                slm_file = os.path.join(slm_dir,"slm.fst")
                lm_utils.fstarcsort(slm_file, ilabel_sort=True)

                process_inputs(batch_input_fst_dir, slm_file, pm_slm_in_dir)
                find_shortest_paths.stringify_shortest_paths(pm_slm_in_dir, pm_slm_shp_dir, pm_slm_outs_dir)

                R = convert_to_single_file("*.gld", gold_dir)        
                
                PMSLM_C = convert_to_single_file("*.fst", pm_slm_outs_dir)

                mc_report = evaluate_output.multi_col_report(batch_dir, output_dirs=("pm_slm",))
                mcrfile = open(os.path.join(batch_dir, "pmslm_report.csv"),"w")
                for r in mc_report:
                    rec_id = r["rec_id"]
                    words = r["words"]
                    gold = r["gold"]
                    pm_slm = r["pm_slm"]
                
                    mcrfile.write("recording, word, gold, pm_slm\n")
                    for tok in zip(words, gold, pm_slm):
                        s = ",".join(tok)
                        s = rec_id + "," + s + "\n"
                        mcrfile.write(s)
                mcrfile.close()

                bleu_PMSLM = bleu_break_scorer.getBLEU(PMSLM_C, R)
                print "for 50/50 + SLM, BLEU is:", bleu_PMSLM
