#!/usr/bin/env python
'''
Created on May 16, 2016

@author: rjm49
'''

import os

import scipy.stats
from sklearn import svm, datasets, preprocessing
from sklearn.cross_validation import train_test_split
from sklearn.externals import joblib
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
from sklearn.metrics.classification import precision_recall_fscore_support, \
    classification_report

from common import read_file, filter_data_rows, DIR, TRAIN_FILE_DEFAULT,\
    PROSODIC_PREDICTION_FILE, TEST_FILE_DEFAULT
import numpy as np
from svm.balance import sep_classes, shuff_trim_balance_classes
from svm.plot_data_dist import plot_compare
import sys
import shutil
from operator import itemgetter

overwrite_pkl = True

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
        pm_dir = "pm_default"
        data_file = TRAIN_FILE_DEFAULT
        test_file = TEST_FILE_DEFAULT
        out_file = PROSODIC_PREDICTION_FILE
        do_search = True
#         use_pilot = False
        n_samples = 500
        cache = 800
    
    print base_dir+"/"+data_file+" -SVM-> "+pm_dir+"/"+out_file
    
    eval1 = read_file(os.path.join(base_dir, data_file), ',', skip_header=True)
    #sel = [12,13,14,15,21,22,23,24]
    sel = range(7,30)

    if(n_samples>0):
        eval1 = eval1[0:n_samples]
    
    headers = [eval1[0][i] for i in sel]
    words = [r[5] for r in eval1]
    samples = [[float(r[i]) for i in sel] for r in eval1]
    classes = [float(r[6]) for r in eval1]
        
    print classes
    p = sum(c==1.0 for c in classes) # count the positive instances
    n = len(classes) - p # derive the negative instances
    print "n=",n," p=",p
    wgt=float(n)/float(p) # cast and divide
    print "wgt=",wgt
    classWeight = { 1: wgt }
    
    
    tr_samples, te_samples, tr_classes, te_classes = train_test_split(samples, classes, test_size=0.20, random_state=0, stratify=classes)
                    
    scaler = preprocessing.StandardScaler().fit( np.array(tr_samples) )

    tr_samples = scaler.transform(tr_samples)

    print tr_samples[0:10]
    print tr_samples.mean(axis=0)
    print tr_samples.std(axis=0)
            
    clf = None
    best_params = None
    #override the defaults with the results of a grid search if desired (takes a while)
    
    
    prosodic_pred_file = os.path.join(base_dir, pm_dir ,out_file)
    
    
        #clear the output directory, or create it if it doesn't yet exist...
    output_dir = os.path.join(base_dir, pm_dir)
    if(os.path.exists(prosodic_pred_file)):
        os.remove(prosodic_pred_file)
    
    #pickled = False
    pickled_model = os.path.join(output_dir, "svm_classifier.pkl")
    
    print pickled_model
        
    if(os.path.exists(pickled_model) and not overwrite_pkl):
        clf = joblib.load(pickled_model)
        print "loaded pickled model..."
    
    else:
        if not os.path.exists(output_dir): #output dir doesn't exist so make it
            os.makedirs(output_dir)
        
        cmin, cmax, cstep = -5,  17,  2
        cr = range(cmin,cmax,cstep)
        print(cr)
        c_range = [ pow(2, y) for y in cr]
        #c_range =(0.005, 0.5, 5, 50, 500, 5000, 50000)
        print('c_range', c_range)
    
        gmin, gmax, gstep = -15, 5, 2
        gr = range(gmin, gmax, gstep)
        print(gr)
        gamma_range = [ pow(2, y) for y in gr ]
        #gamma_range = (0.00005, 0.0005, 0.005, 0.05, 0.5, 5.0, 50, 500)
        print('gamma_range', gamma_range)
        
        tuned_parameters = [
                    {   'kernel': ['rbf'],
                        'gamma': gamma_range,
                        'C': c_range,
                        'class_weight':['balanced', classWeight],
                    },
                     
                    ]
        
        estr = svm.SVC(kernel='rbf', cache_size=cache, probability=True)
        searcher = GridSearchCV(estr, tuned_parameters, cv=5, n_jobs=-1, scoring='recall', verbose=True)
        
        c_dist =  scipy.stats.expon(scale=100)
        gamma_dist = scipy.stats.expon(scale=.1)
                
        param_dist={'C': c_dist, 'gamma': gamma_dist, 'class_weight':['balanced', classWeight]}

#         searcher = RandomizedSearchCV(estr, param_distributions=param_dist, n_iter=1000, n_jobs=-1, cv=5, verbose=True, scoring="recall")
        
        
        searcher.fit(tr_samples,tr_classes)
        report(searcher.grid_scores_)
                
        clf = searcher.best_estimator_
        best_params = searcher.best_params_

        print "COMPARING CLF PARAMS WITH BEST PARAMS (shd be same)"
        print clf.get_params()
        print best_params
        
        joblib.dump(clf, pickled_model)
           

    print clf

    print "FITTING"     
    clf.fit(tr_samples, tr_classes)
    print clf
    
    
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