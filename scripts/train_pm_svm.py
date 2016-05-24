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
import random

overwrite_pkl = False

def dissect(data):
    headers = [data[0][i] for i in sel]
    words = [r[5] for r in data]
    samples = [[float(r[i]) for i in sel] for r in data]
    classes = [float(r[6]) for r in data]
    return (headers, words, samples, classes)

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
## tr_data training set
    args = sys.argv
    
    if(len(args)==4):
        base_dir = args[0]
        pm_dir = args[1]
        tr_file = args[2]
        test_fname = args[3]
    else:
        base_dir = DIR
        pm_dir = "pm_default"
        tr_file = TRAIN_FILE_DEFAULT
        test_fname = TEST_FILE_DEFAULT
        do_search = True
#         use_pilot = False
        n_samples = 2000
        cache = 800
    
    pm_dir= raw_input("enter PM name: [%s]" % pm_dir) or pm_dir
    tr_file = raw_input("enter PM training file name: [%s]" % tr_file) or tr_file
    
    tr_data = read_file(os.path.join(base_dir, tr_file), ',', skip_header=True)
    
    test_fname = raw_input("enter file to test on: [%s]" % test_fname) or test_fname
    out_fname = test_fname+"-probabilities.dat"
    out_file = os.path.join(base_dir, pm_dir, out_fname)
    #clear extant predictions file
    if(os.path.exists(out_file)):
        os.remove(out_file)
        print "removed",out_file
        
    print base_dir+"/"+tr_file+" -SVM-> ",out_file
    

    test_data = read_file(os.path.join(base_dir, test_fname), ',', skip_header=True)
    
    #sel = [12,13,14,15,21,22,23,24]
    sel = range(7,30)

    if(n_samples>0):
        tr_data = random.sample(tr_data, n_samples)
        
    (tr_headers, tr_words, tr_samples, tr_classes) = dissect(tr_data)
    (te_headers, te_words, te_samples, te_classes) = dissect(test_data)
    
    p = sum(c==1.0 for c in tr_classes) # count the positive instances
    n = len(tr_classes) - p # derive the negative instances
    print "n=",n," p=",p
    wgt=float(n)/float(p) # cast and divide
    print "wgt=",wgt
    classWeight = { 1: wgt }
    
    
    #tr_samples, te_samples, tr_classes, te_classes = train_test_split(samples, classes, test_size=0.20, random_state=0, stratify=classes)
                    
    scaler = preprocessing.StandardScaler().fit( np.array(tr_samples) )
    tr_samples = scaler.transform(tr_samples)

#     print tr_samples[0:10]
#     print tr_samples.mean(axis=0)
#     print tr_samples.std(axis=0)
             
    clf = None
    best_params = None
    #override the defaults with the results of a grid search if desired (takes a while)
    
        
    #pickled = False
    pkl_dir = os.path.join(base_dir, pm_dir, "pkl")
    pickled_model = os.path.join(pkl_dir, "svm_classifier.pkl")
    
    if(os.path.exists(pickled_model) and not overwrite_pkl):
        clf = joblib.load(pickled_model)
        clf.set_params(verbose=True)
        print "loaded pickled model...", pickled_model
    
    else:
        if not os.path.exists(pkl_dir): #output dir doesn't exist so make it
            os.makedirs(pkl_dir)
            print "made dir for pickled model:", pkl_dir
        
        cmin, cmax, cstep = -5,  17,  2
        cr = range(cmin,cmax,cstep)
        print(cr)
        #c_range = [ pow(2, y) for y in cr]
        #c_range =(0.005, 0.5, 5, 50, 500, 5000, 50000)
        c_range = (0.5, 50, 5000)
        print('c_range', c_range)
    
        gmin, gmax, gstep = -15, 5, 2
        gr = range(gmin, gmax, gstep)
        print(gr)
        #gamma_range = [ pow(2, y) for y in gr ]
        #gamma_range = (0.00005, 0.0005, 0.005, 0.05, 0.5, 5.0, 50, 500)
        gamma_range = (0.0005, 0.05, 5.0, 500)
        
        print('gamma_range', gamma_range)
        
        tuned_parameters = [
                    {
                        'gamma': gamma_range,
                        'C': c_range,
                    },   
                ]
        
        estr = svm.SVC(kernel='rbf', cache_size=cache, probability=True, class_weight='balanced')
        #searcher = GridSearchCV(estr, tuned_parameters, cv=5, n_jobs=-1, scoring='recall', verbose=True)
        
        c_dist =  scipy.stats.expon(scale=100)
        gamma_dist = scipy.stats.expon(scale=.01)
        
#         crvs= c_dist.rvs(size=100)
#         print crvs
#         print crvs.mean(axis=0)
#         
#         grvs = gamma_dist.rvs(size=100)
#         print grvs
#         print grvs.mean(axis=0)
        
#         best = 0.0
#         for c in c_range:
#             for g in gamma_range:
#                 param_dist={'C': scipy.stats.expon(scale=c), 'gamma': scipy.stats.expon(scale=g)}
#                 searcher = RandomizedSearchCV(estr, param_distributions=param_dist, n_iter=50, n_jobs=-1, cv=4, verbose=True, scoring="recall")
#                 searcher.fit(tr_samples,tr_classes)
#                 print "PARAMS:", c, g
#                 report(searcher.grid_scores_)
#                 
#                 #clf = searcher.best_estimator_
#                 #best_params = searcher.best_params_
#                 if(searcher.best_score_ > best):
#                     best = searcher.best_score_
#                     clf = searcher.best_estimator_
#                     best_params = searcher.best_params_

        param_dist={'C': c_dist, 'gamma': gamma_dist}
        searcher = RandomizedSearchCV(estr, param_distributions=param_dist, n_iter=100, n_jobs=-1, cv=5, verbose=True, scoring="recall")
        searcher.fit(tr_samples,tr_classes)
        report(searcher.grid_scores_)
        clf = searcher.best_estimator_
                            

        print "COMPARING CLF PARAMS WITH BEST PARAMS (shd be same)"
        print clf.get_params()
        print best_params
        
        joblib.dump(clf, pickled_model)
           

    print clf

    print "FITTING"     
    clf.fit(tr_samples, tr_classes)
    clf.set_params(verbose=True)
    print clf
    
    
    #NOW TO TEST AGAINST HELD-OUT/TEST DATA
    te_samples = scaler.transform(te_samples)
    
    print "no test cases", len(te_samples)
    
    predictions = -1.0 * clf.predict_log_proba(te_samples) #this is a list of pairs of probs in form [ [1-p, p],  ... ]
    predicted_classes = clf.predict(te_samples)
    
    print("TEST: Number of mislabelled points out of a total %d points : %d" % (len(te_samples),(te_classes != predicted_classes).sum()))
    print(classification_report(te_classes, predicted_classes))

    print len(clf.support_vectors_)
    
    pred_file = open(out_file,"w")
    pred_file.write("labels 0 1\n") #this emulates an earlier file format for compatibility
    for word, prob_tuple, guessed_class in zip(te_words,predictions,predicted_classes):
        pred_file.write("%d %f %f %s\n" % (guessed_class,prob_tuple[0],prob_tuple[1],word))

    pred_file.close()
    print "wrote predictions file:",pred_file
