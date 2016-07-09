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
    save_symbol_table, LM_PRUNED, ANYWORD
from pm.pm_utils import generate_pm_text_files, compile_pm_files
from find_shortest_paths import convert_to_single_file
import bleu_break_scorer
import nltk

#nltk.download()

do_build = True
eq_chance=  False

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
        
        batch_name = batch['batch_dir']
        batch_dir = os.path.join(base_dir, batch_name)
        lm_dir = os.path.join(base_dir, batch['language_model'])
        pm_dir = os.path.join(base_dir, batch['prosodic_model'])
        slm_dir = os.path.join(base_dir,batch['length_model'])
        te_file = batch['test_file']
        
        use_pos_tags = batch.get('use_pos_tags', False)
        pm_weight = batch.get('pm_weight', 1)

        gold_dir = os.path.join(batch_dir, "gold")
        all_models_dir = os.path.join(batch_dir, "pm_lm_slm")
        
        all_models_out_dir = os.path.join(all_models_dir, "output")
        all_models_in_dir = os.path.join(all_models_dir, "composed")
        all_models_shp_dir = os.path.join(all_models_dir, "shortest")
        
        pm_only_dir = os.path.join(batch_dir, "pm_only")
        pm_shp_dir = os.path.join(pm_only_dir, "shortest")
        pm_outs_dir = os.path.join(pm_only_dir, "output")
        
        pm_lm_dir = os.path.join(batch_dir, "pm_lm")
        pm_lm_in_dir = os.path.join(pm_lm_dir, "composed")
        pm_lm_shp_dir = os.path.join(pm_lm_dir, "shortest")
        pm_lm_outs_dir = os.path.join(pm_lm_dir, "output")

        pm_slm_dir = os.path.join(batch_dir, "pm_slm")
        pm_slm_in_dir = os.path.join(pm_lm_dir, "composed")
        pm_slm_shp_dir = os.path.join(pm_lm_dir, "shortest")
        pm_slm_outs_dir = os.path.join(pm_lm_dir, "output")


        if(do_build): 
            #lmdir_global = os.path.join(base_dir,lm_dir)
            batch_input_fst_dir = os.path.join(batch_dir, "speech_fsts")
            if not os.path.exists(batch_input_fst_dir):
                os.makedirs(batch_input_fst_dir)
        
            te_rows = read_file(os.path.join(base_dir, te_file), ',', skip_header=True)
        
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
        
            if use_pos_tags:
                segs = []
                for t in te_rows:
                    if not t[0] in segs:
                        segs.append(t[0])

                cntr = 0
                emission_vals = []
                for seg in segs:
                    ws = [t[5] for t in te_rows if t[0]==seg ]
                    ws = [x.upper() if (len(x)==1 and x!='a') else x for x in ws]
                    print "For seg=",seg,"got these tokens:",ws
                    tags = nltk.pos_tag(ws)
                    print "tags=",tags
                    for tag in tags:
                        emission_vals.append(tag[1])
                
                _ = raw_input("hit key")
            elif eq_chance:
                emission_vals = [ANYWORD for t in te_rows]
            else:
                emission_vals = [t[5] for t in te_rows]
                        
        
            generate_pm_text_files(batch_input_fst_dir, lm_syms, te_rows, prob_rows, max_count=-1, emission_values=emission_vals, equal_chance=eq_chance, pm_weight=pm_weight)
            
            compile_pm_files(batch_input_fst_dir, pmsym_fname, lmsym_fname)
            
            #TWO: Assuming all the other model files are complete, we should be good to go
            
            #lang_mod = os.path.join(lm_dir,LM_PRUNED)
            lang_mod = os.path.join(lm_dir,"mod.pru")
#             lang_mod = os.path.join(lm_dir,"lm.mod")

                    
            print "joined up cretinous dir names"
   
            find_shortest_paths.stringify_shortest_paths(batch_input_fst_dir, pm_shp_dir, pm_outs_dir)
            
            if eq_chance:
                slm_file = os.path.join(slm_dir,"slm.fst")
                lm_gen.fstarcsort(slm_file, ilabel_sort=True)

                process_inputs(batch_input_fst_dir, slm_file, pm_slm_in_dir)
                find_shortest_paths.stringify_shortest_paths(pm_slm_in_dir, pm_slm_shp_dir, pm_slm_outs_dir)

                R = convert_to_single_file("*.gld", gold_dir)        
                
                PMSLM_C = convert_to_single_file("*.fst", pm_slm_outs_dir)

                bleu_PM = bleu_break_scorer.getBLEU(PMSLM_C, R)

                mc_report = evaluate_output.multi_col_report(batch_dir)
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

            
            else:
                #now just use the pruned LM file without slen modifier
                process_inputs(batch_input_fst_dir, lang_mod, pm_lm_in_dir)
                find_shortest_paths.stringify_shortest_paths(pm_lm_in_dir, pm_lm_shp_dir, pm_lm_outs_dir) #(input_dir, shortpath_dir, strings_dir
                
                #use combined LM and slen modifier
                slm_file = os.path.join(slm_dir,"slm.fst")
                lm_slm = os.path.join(batch_dir,"lm_slm.fst") 
                
                lm_gen.fstarcsort(slm_file, ilabel_sort=True)
                lm_gen.fstcompose(lang_mod, slm_file, lm_slm)
                lm_gen.fstimmut(lm_slm, lm_slm)
                        
                process_inputs(batch_input_fst_dir, lm_slm, all_models_in_dir)
                find_shortest_paths.stringify_shortest_paths(all_models_in_dir, all_models_shp_dir, all_models_out_dir)

        R = convert_to_single_file("*.gld", gold_dir)        
        C = convert_to_single_file("*.fst", all_models_out_dir)
        
        PM_C = convert_to_single_file("*.fst", pm_outs_dir)
        PMLM_C = convert_to_single_file("*.fst", pm_lm_outs_dir)
        
        evaluate_output.eval_segmenter_output(batch_dir)
        
        mc_report = evaluate_output.multi_col_report(batch_dir)
        mcrfile = open(os.path.join(batch_dir, "mc_report.csv"),"w")
        for r in mc_report:
            rec_id = r["rec_id"]
            words = r["words"]
            gold = r["gold"]
            pm = r["pm_only"]
            pm_lm = r["pm_lm"]
            pm_lm_slm = r["pm_lm_slm"]
        
            mcrfile.write("recording, word, gold, pm_only, pm_lm, pm_lm_slm\n")
            for tok in zip(words, gold, pm, pm_lm, pm_lm_slm):
                s = ",".join(tok)
                s = rec_id + "," + s + "\n"
                mcrfile.write(s)
        mcrfile.close()
                        

        bleu = bleu_break_scorer.getBLEU(C, R, N=4)
        bleu_PM = bleu_break_scorer.getBLEU(PM_C, R, N=4)
        bleu_PMLM = bleu_break_scorer.getBLEU(PMLM_C, R, N=4)
        
        print "BLEU-4"
        print "PM", bleu_PM[0]
        print "PM_LM", bleu_PMLM[0]
        print "PM_LM_SLM", bleu[0]

        bleu3 = bleu_break_scorer.getBLEU(C, R, N=3)
        bleu_PM3 = bleu_break_scorer.getBLEU(PM_C, R, N=3)
        bleu_PMLM3 = bleu_break_scorer.getBLEU(PMLM_C, R, N=3)
               
        print "BLEU-3"
        print "PM", bleu_PM3[0]
        print "PM_LM", bleu_PMLM3[0]
        print "PM_LM_SLM", bleu3[0]    
        
        bfile = open(os.path.join(batch_dir, batch_name+"-BLEUs.txt"),"w")
        bfile.write("Quadrigram BLEU4 scores\n")
        bfile.write("pm BLEU4 = %f \n" % bleu_PM[0])
        bfile.write("pm_lm BLEU4 = %f \n" % bleu_PMLM[0])
        bfile.write("combined BLEU4 = %f \n" % bleu[0])
        bfile.write("\nmodified precisions\n")
        bfile.write("pm  = %s \n" % (bleu_PM[1],))
        bfile.write("pm_lm  = %s \n" % (bleu_PMLM[1],))
        bfile.write("combined  = %s \n" % (bleu[1],))
        bfile.write("\n")
        bfile.write("Trigram BLEU3 scores\n")
        bfile.write("pm BLEU3 = %f \n" % bleu_PM3[0])
        bfile.write("pm_lm BLEU3 = %f \n" % bleu_PMLM3[0])
        bfile.write("combined BLEU3 = %f \n" % bleu3[0])
        bfile.write("\nmodified precisions\n")
        bfile.write("pm  = %s \n" % (bleu_PM3[1],))
        bfile.write("pm_lm  = %s \n" % (bleu_PMLM3[1],))
        bfile.write("combined  = %s \n" % (bleu3[1],))
        
        bfile.close()
        