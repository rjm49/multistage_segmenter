import numpy as np
from sklearn import svm, datasets, preprocessing
import codecs
import sys
from random import shuffle
from sklearn.metrics.classification import precision_recall_fscore_support,\
    classification_report
from multistage_segmenter.common import *
from multistage_segmenter.svm.balance import sep_classes, shuff_trim_balance_classes
from sklearn.externals import joblib
from multistage_segmenter.svm.plot_data_dist import plot_compare
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
import scipy.stats

use_pilot = True
do_search = True
save_pkl = False

if __name__ == '__main__':
## eval1 training set
    print "\nLoading BULATS eval1 training data"
    eval1 = read_file(os.path.join(DIR,EVAL1_FILE_NORMED), ',', skip_header=True)
    pred_file = open(os.path.join(DIR,PROSODIC_PREDICTION_FILE),"w")
    #sel = [12,13,14,15,21,22,23,24]
    sel = range(7,30)
    samples, classes, headers = filter_data_rows(eval1, sel=sel, keep_headers=True)
    #samples, classes = shuff_trim_balance_classes(samples,classes,max_size=500)
    
    n=p=0.0
    for c in classes:
        if c==0:
            n+=1.0
        else:
            p+=1.0
    wgt = n/p
    print "n=",n," p=",p
    print "wgt=",wgt
    classWeight = { 1: wgt }
    
        ## pilot test set
    if(use_pilot):
        print "\nLoading BULATS pilot test data"
        pilot = read_file(os.path.join(DIR,PILOT_FILE_NORMED), ',', skip_header=False)
        samps_raw, tclasses, theaders = filter_data_rows(pilot, sel=sel, keep_headers=True)
          
        ptoks=[prow[5] for prow in pilot[1:]]          
        
        samples, X_test, classes, y_test = train_test_split(samples, classes, test_size=0.90, random_state=0, stratify=classes)
    else:
        samples, X_test, classes, y_test = train_test_split(samples, classes, test_size=0.20, random_state=0, stratify=classes)
        
    k = 'rbf'
    cache = 800
            
    scaler = preprocessing.StandardScaler().fit( np.array(samples) )

    X = scaler.transform(samples)
    Y = classes

    print X.mean(axis=0)
    print X.std(axis=0)
        
    print "no samples", len(samples)
    print "feature dim", len(samples[0])
    print "no class specifiers", len(classes)

    #FOR EVAL1
    best_gamma = 0.00159185299741  #3.0517578125e-05
    best_C = 21.529318599 # 0.5
    class_weight = 'balanced'
    #FOR PILOT
#     best_gamma = 0.00017237263255495504
#     best_C = 40.12005305543296
#     class_weight = {1: 14.839243498817966}
    
    best_kernel='rbf'
    best_degree = 2
    
    best_params = None
    #override the defaults with the results of a grid search if desired (takes a while)
    if(do_search):
        
#         cmin, cmax, cstep = -5,  17,  2
#         cr = range(cmin,cmax,cstep)
#         print(cr)
#         c_range = [ pow(2, y) for y in cr]
        c_range =[5, 50, 500, 5000]
        print('c_range', c_range)
    
#         gmin, gmax, gstep = -15, 5, 2
#         gr = range(gmin, gmax, gstep)
#         print(gr)
#         gamma_range = [ pow(2, y) for y in gr ]
        gamma_range = [0.05, 0.5, 5.0, 50]
        print('gamma_range', gamma_range)
        
        tuned_parameters = [
                    {   'kernel': ['rbf'],
                        'gamma': gamma_range,
                        'C': c_range,
                    },
                     
                    ]
        
        estr = svm.SVC(kernel=best_kernel, C=1.0, cache_size=cache, probability=True, class_weight=classWeight)
#         searcher = GridSearchCV(estr, tuned_parameters, cv=10, n_jobs=3, scoring='recall')
        
        param_dist={'C': scipy.stats.expon(scale=100), 'gamma': scipy.stats.expon(scale=.1), 'kernel': ['rbf'], 'class_weight':['balanced', classWeight]}
        
        searcher = RandomizedSearchCV(estr, param_distributions=param_dist, n_iter=100, n_jobs=-1, cv=5, verbose=True, scoring="recall")
        searcher.fit(X,Y)
        best_params = searcher.best_params_
        print "best_params:",best_params
        
        best_gamma=best_params['gamma'] if 'gamma' in best_params.keys() else best_gamma
        best_C=best_params['C'] if 'C' in best_params.keys() else best_C
        best_kernel=best_params['kernel'] if 'kernel' in best_params.keys() else best_kernel
        best_degree=best_params['degree'] if 'degree' in best_params.keys() else best_degree
        
    clf = None
    pickled = False
    pickled_model = "svm_classifier.pkl"
    
    if(os.path.exists(pickled_model) and os.path.isfile(pickled_model)):
        pickled = True
    
    if(pickled):
        clf = joblib.load(pickled_model)
    else: 
        clf = svm.SVC(#kernel=best_kernel, C=best_C, degree=best_degree, gamma=best_gamma, 
                      cache_size=cache, probability=True, 
                      #class_weight={1:wgt}, 
                      class_weight=class_weight,
                      verbose=True)
    print clf

    print "FITTING"
     
    clf.fit(X, Y)
    print clf
    
    if(not pickled and save_pkl):
        joblib.dump(clf, pickled_model)
    
    if(use_pilot):
        tsamples = scaler.transform(samps_raw)
        tclasses = tclasses
    else:
        tsamples = scaler.transform(X_test)
        tclasses = y_test
    
    print "no test cases", len(tsamples)
    
    predictions = -1.0 * clf.predict_log_proba(tsamples) #this is a list of pairs of probs in form [ [1-p, p],  ... ]
    predicted_classes = clf.predict(tsamples)
    
    print("TEST: Number of mislabelled points out of a total %d points : %d" % (len(tsamples),(tclasses != predicted_classes).sum()))
    print(classification_report(tclasses, predicted_classes))

    print len(clf.support_vectors_)
    
    pred_file.write("labels 0 1\n") #this emulates an earlier file format for compatibility
    for samp, p, pc in zip(ptoks,predictions,predicted_classes):
        pred_file.write("%d %f %f %s\n" % (pc,p[0],p[1],samp))
    pred_file.flush()
    pred_file.close()
    print "wrote predictions file:",pred_file