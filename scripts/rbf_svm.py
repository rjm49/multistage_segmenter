import os

import scipy.stats
from sklearn import svm, datasets, preprocessing
from sklearn.cross_validation import train_test_split
from sklearn.externals import joblib
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
from sklearn.metrics.classification import precision_recall_fscore_support, \
    classification_report

from common import read_file, filter_data_rows, DIR, EVAL1_FILE_NORMED,\
    PROSODIC_PREDICTION_FILE, PILOT_FILE_NORMED
import numpy as np
from svm.balance import sep_classes, shuff_trim_balance_classes
from svm.plot_data_dist import plot_compare
import sys
import shutil
from operator import itemgetter

save_pkl = False

# Utility function to report best scores
def report(grid_scores, n_top=3):
    top_scores = sorted(grid_scores, key=itemgetter(1), reverse=True)[:n_top]
    for i, score in enumerate(top_scores):
        print("Model with rank: {0}".format(i + 1))
        print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
              score.mean_validation_score,
              np.std(score.cv_validation_scores)))
        print("Parameters: {0}".format(score.parameters))
        print("")

if __name__ == '__main__':
## eval1 training set
    args = sys.argv
    
    if(len(args)==4):
        base_dir = args[0]
        pm_dir = args[1]
        data_file = args[2]
        test_file = args[3]
        out_file = args[4]
    else:
        base_dir = DIR
        pm_dir = "default_pm"
        data_file = EVAL1_FILE_NORMED
        test_file = PILOT_FILE_NORMED
        out_file = PROSODIC_PREDICTION_FILE
        balance = True
        do_search = True
#         use_pilot = False
        n_samples = 2000
        k = 'rbf'
        cache = 800
    
    print base_dir+"/"+data_file+" -SVM-> "+pm_dir+"/"+out_file
    
    #clear the output directory, or create it if it doesn't yet exist...
    output_dir = os.path.join(base_dir, pm_dir)
    if(os.path.exists(output_dir)):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    eval1 = read_file(os.path.join(base_dir, data_file), ',', skip_header=True)
    #sel = [12,13,14,15,21,22,23,24]
    sel = range(7,30)

    if(n_samples>0):
        eval1 = eval1[0:n_samples]
    
    #samples, classes, headers = filter_data_rows(eval1, sel=sel, keep_headers=True)
    #samples, classes = shuff_trim_balance_classes(samples,classes,max_size=500)
    
    headers = [eval1[0][i] for i in sel]
    words = [r[5] for r in eval1]
    samples = [[float(r[i]) for i in sel] for r in eval1]
    classes = [float(r[6]) for r in eval1]
        
        
    print samples[0:10]
#     n=p=0.0
#     for c in classes:
#         if c==0:
#             n+=1.0
#         else:
#             p+=1.0
#     wgt = n/p
#     print "n=",n," p=",p
#     print "wgt=",wgt
#     classWeight = { 1: wgt }
    
    print classes
    p = sum(c==1.0 for c in classes) # count the positive instances
    n = len(classes) - p # derive the negative instances
    print "n=",n," p=",p
    wgt=float(n)/float(p) # cast and divide
    print "wgt=",wgt
    classWeight = { 1: wgt }
    
    
# we remove the option of testing against the pilot data - we just want to see what works best on held out training data
#     # pilot test set
#     if(use_pilot):
#         print "\nLoading ",test_file
#         pilot = read_file(os.path.join(base_dir, test_file), ',', skip_header=False)
#         #samps_raw, tclasses, theaders = filter_data_rows(pilot, sel=sel, keep_headers=True)
#         theaders = [pilot[0][i] for i in sel]
#         ptoks = [r[5] for r in pilot[1:]]
#         samps_raw = [[r[i] for i in sel] for r in pilot[1:]]
#         tclasses = [r[6] for r in pilot[1:]]
#            
#         samples, X_test, classes, y_test = train_test_split(samples, classes, test_size=0.90, random_state=0, stratify=classes)
#     else:
    
    
    
    tr_samples, te_samples, tr_classes, te_classes = train_test_split(samples, classes, test_size=0.20, random_state=0, stratify=classes)
                    
    scaler = preprocessing.StandardScaler().fit( np.array(tr_samples) )

    tr_samples = scaler.transform(tr_samples)

    print tr_samples[0:10]
    print tr_samples.mean(axis=0)
    print tr_samples.std(axis=0)
            
    best_kernel='rbf'
    best_degree = 2
    
    clf = None
    best_params = None
    #override the defaults with the results of a grid search if desired (takes a while)
    if(do_search):
        
#         cmin, cmax, cstep = -5,  17,  2
#         cr = range(cmin,cmax,cstep)
#         print(cr)
#         c_range = [ pow(2, y) for y in cr]
        c_range =(0.005, 0.5, 5, 50, 500, 5000, 50000)
        print('c_range', c_range)
    
#         gmin, gmax, gstep = -15, 5, 2
#         gr = range(gmin, gmax, gstep)
#         print(gr)
#         gamma_range = [ pow(2, y) for y in gr ]
        gamma_range = (0.00005, 0.0005, 0.005, 0.05, 0.5, 5.0, 50, 500)
        print('gamma_range', gamma_range)
        
        tuned_parameters = [
                    {   'kernel': ['rbf'],
                        'gamma': gamma_range,
                        'C': c_range,
                        'class_weight':['balanced', classWeight],
                    },
                     
                    ]
        
        estr = svm.SVC(kernel='rbf', cache_size=cache, probability=True)
#         searcher = GridSearchCV(estr, tuned_parameters, cv=5, n_jobs=-1, scoring='recall', verbose=True)
        
        param_dist={'C': scipy.stats.expon(scale=100), 'gamma': scipy.stats.expon(scale=.1), 'class_weight':['balanced', classWeight]}
#         param_dist={'C': c_range, 'gamma': gamma_range, 'kernel': ['rbf'], 'class_weight':['balanced', classWeight]}        
        
        searcher = RandomizedSearchCV(estr, param_distributions=param_dist, n_iter=1000, n_jobs=-1, cv=5, verbose=True, scoring="recall")
        
        
        searcher.fit(tr_samples,tr_classes)
        report(searcher.grid_scores_)
                
        clf = searcher.best_estimator_
        best_params = searcher.best_params_

        print "COMPARING CLF PARAMS WITH BEST PARAMS (shd be same)"
        print clf.get_params()
        print best_params
        
        
#         best_gamma=best_params['gamma'] if 'gamma' in best_params.keys() else best_gamma
#         best_C=best_params['C'] if 'C' in best_params.keys() else best_C
#         best_kernel=best_params['kernel'] if 'kernel' in best_params.keys() else best_kernel
#         best_degree=best_params['degree'] if 'degree' in best_params.keys() else best_degree
   
           
    pickled = False
    pickled_model = "svm_classifier.pkl"
    
    if(os.path.exists(pickled_model) and os.path.isfile(pickled_model)):
        pickled = True
    
    if(pickled):
        clf = joblib.load(pickled_model)
    else:
        pass #we just use the clf from the search stage 
#         clf = svm.SVC(#kernel=best_kernel, C=best_C, degree=best_degree, gamma=best_gamma, 
#                       cache_size=cache, probability=True, 
#                       #class_weight={1:wgt}, 
#                       class_weight=class_weight,
#                       verbose=True)



    print clf

    print "FITTING"
    print tr_samples[0:10]
    print tr_classes[0:10] 
     
    clf.fit(tr_samples, tr_classes)
    print clf
    
    if(not pickled and save_pkl):
        joblib.dump(clf, pickled_model)
    
    #NOW TO TEST AGAINST HELD-OUT/TEST DATA
    te_samples = scaler.transform(te_samples)
    
    print "no test cases", len(te_samples)
    
    predictions = -1.0 * clf.predict_log_proba(te_samples) #this is a list of pairs of probs in form [ [1-p, p],  ... ]
    predicted_classes = clf.predict(te_samples)
    
    print("TEST: Number of mislabelled points out of a total %d points : %d" % (len(te_samples),(te_classes != predicted_classes).sum()))
    print(classification_report(te_classes, predicted_classes))

    print len(clf.support_vectors_)
    
    pred_file = open(os.path.join(base_dir, pm_dir ,out_file),"w")
    pred_file.write("labels 0 1\n") #this emulates an earlier file format for compatibility
    for word, prob_tuple, guessed_class in zip(words,predictions,predicted_classes):
        pred_file.write("%d %f %f %s\n" % (guessed_class,prob_tuple[0],prob_tuple[1],word))

    pred_file.close()
    print "wrote predictions file:",pred_file