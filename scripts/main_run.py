'''
Created on 30 Nov 2015

@author: Russell Moore (rjm49@cam.ac.uk)
'''
import argparse
import glob
import json
import os
import shutil
import sys

import nltk

from mseg import bleu_break_scorer, lm_utils, create_gold_files, \
    find_shortest_paths, evaluate_output
from mseg.common import read_file, LM_SYM_FILE, load_symbol_table, SYM_FILE, \
    save_symbol_table
from mseg.find_shortest_paths import convert_to_single_file
from mseg.pm_utils import generate_pm_text_files, compile_pm_files
import mseg.reporting_utils as report_utils


#nltk.download()
do_build = True
#eq_chance=  False
compose_lm_slm = True
SYMBOL_COL = 5


def write_bleus_to_file(R, cands, bfile, order=4, strict=True):
    smode = "strict" if strict else "lax"    
    bfile.write("BLEU-%d SCORES (%s)\n" % (order, smode))
    for cpair in cands:
        c_name = cpair[0]
        C = cpair[1]
        bleu_pair = bleu_break_scorer.getBLEU(C, R, N=order, strict=strict)
        
        
#         print c_name, order, smode, bleu_pair
        
        bfile.write("%s = %f \n" % (c_name, bleu_pair[0]))
#         bfile.write("Mod'd prec'ns:\n")
        for p in enumerate(bleu_pair[1]):
            bfile.write("p_%d=%f " % (p[0]+1, p[1]))
        BP = bleu_pair[2]
        if(BP<1.0):
            bfile.write("Brev pen=%f\n" % BP)
        bfile.write("\n")
    bfile.write("- - - - -\n")
    
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


def posify(te_rows):
    segs = []
    for t in te_rows:
        if not t[0] in segs:
            segs.append(t[0])
    
    emission_vals = []
    for seg in segs:
        ws = [t[SYMBOL_COL] for t in te_rows if t[0] == seg]
        ws = [x.upper() if (len(x) == 1 and x != 'a') else x for x in ws]
        print "For seg=", seg, "got these tokens:", ws
        tags = nltk.pos_tag(ws)
        print "tags=", tags
        for tag in tags:
            emission_vals.append(tag[1])
    return emission_vals

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", nargs='?', default= os.path.join(os.getcwd(),"mseg_config.cfg"), help="configuration file for the multistage segmenter")
    args = parser.parse_args()
    
    print "running main_run"
    config_fname = args.config_file
    with open(config_fname) as data_file:
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
              
            te_syms = [r[SYMBOL_COL] for r in te_rows]
    
            all_syms = set(lm_syms + te_syms)
            pmsym_fname = os.path.join(batch_dir, SYM_FILE)
            save_symbol_table(all_syms, pmsym_fname)
            
            probability_file = os.path.join(pm_dir, (te_file+"-probabilities.dat"))
            if not os.path.exists(probability_file):
                print "No prosodic probability file found: ", probability_file, " - you need to create this first with train_pm.py"
                continue #go onto the next batch TODO should create prob file here!
            
            prob_rows = read_file(probability_file, ' ', skip_header=True)
        
            if use_pos_tags:
                emission_vals = posify(te_rows)
            else:
                emission_vals = te_syms
                        
        
            generate_pm_text_files(batch_input_fst_dir, lm_syms, te_rows, prob_rows, max_count=-1, emission_values=emission_vals, pm_weight=pm_weight)
            compile_pm_files(batch_input_fst_dir, pmsym_fname, lmsym_fname)
            
            #TWO: Assuming all the other model files are complete, we should be good to go
            
            #lang_mod = os.path.join(lm_dir,LM_PRUNED)
            lang_mod = os.path.join(lm_dir,"mod.pru")
#             lang_mod = os.path.join(lm_dir,"lm.mod")

                    
            print "joined up working dir names"
   
            find_shortest_paths.stringify_shortest_paths(batch_input_fst_dir, pm_shp_dir, pm_outs_dir)
            
  
            #now just use the pruned LM file without slen modifier
            process_inputs(batch_input_fst_dir, lang_mod, pm_lm_in_dir)
            find_shortest_paths.stringify_shortest_paths(pm_lm_in_dir, pm_lm_shp_dir, pm_lm_outs_dir) #(input_dir, shortpath_dir, strings_dir
            
            #use combined LM and slen modifier
            slm_file = os.path.join(slm_dir,"slm.fst")
            lm_slm = os.path.join(batch_dir,"lm_slm.fst") 
            
            if compose_lm_slm:
                lm_utils.fstarcsort(slm_file, ilabel_sort=True)
                lm_utils.fstcompose(lang_mod, slm_file, lm_slm)
                lm_utils.fstimmut(lm_slm, lm_slm)
                     
                process_inputs(batch_input_fst_dir, lm_slm, all_models_in_dir)
            
        print "doing find shortest paths..."
        find_shortest_paths.stringify_shortest_paths(all_models_in_dir, all_models_shp_dir, all_models_out_dir)

        R = convert_to_single_file("*.gld", gold_dir)        
        C = convert_to_single_file("*.fst", all_models_out_dir)
        
        PM_C = convert_to_single_file("*.fst", pm_outs_dir)
        PMLM_C = convert_to_single_file("*.fst", pm_lm_outs_dir)
        
        cands = (("PM", PM_C),
                 ("PM_LM",PMLM_C),
                 ("PM_LM_SLM",C))
        
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
            for row in zip(words, gold, pm, pm_lm, pm_lm_slm):
                s = ",".join(row)
                s = rec_id + "," + s + "\n"
                mcrfile.write(s)
        mcrfile.close()

        bfile = open(os.path.join(batch_dir, batch_name+"-SCORES.txt"),"w")
        bfile.write(batch_name+"\n\n");
        
        #report BLEU-like scores for 4- and 3-grammes in both strict and lax counting modes
        for o in (4,3):
            for s in (True,False):
                write_bleus_to_file(R, cands, bfile, o, strict=s)

        #create a list of {0,1} values to show break or no break
        #golds=[r["gold"] for r in mc_report]
        golds=[ int(item) for r in mc_report for item in r['gold']]
        for m in ("pm_only", "pm_lm", "pm_lm_slm"):        
            hyps=[int(item) for r in mc_report for item in r[m]]
            prF = report_utils.get_prF(golds, hyps)
            b_acc = report_utils.get_baseline_accuracy(golds, hyps)
            acc = report_utils.get_accuracy(golds, hyps)
            bfile.write("prF (%s)=%s\n" % (m,str(prF)))
            bfile.write("acc (%s)=%s with delta=%s\n" % (m,str(acc),str(acc-b_acc)))
            bfile.write("- - - - - -\n")
        bfile.close()
        
        print "Wrote bleu scores to file: ", bfile
        
if __name__ == '__main__':
    main(sys.argv[1:])