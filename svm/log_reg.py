import os

import scipy.stats
from sklearn import preprocessing
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import RandomizedSearchCV
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.metrics.classification import classification_report

from multistage_segmenter.common import DIR, EVAL1_FILE_NORMED, read_file, \
    PROSODIC_PREDICTION_FILE, filter_data_rows, PILOT_FILE_NORMED
import numpy as np


do_search = True
save_pkl = False
test_with_pilot = True

if __name__ == '__main__':
## eval1 training set
    print "\nLoading BULATS eval1 training data"
    eval1 = read_file(os.path.join(DIR,EVAL1_FILE_NORMED), ',', skip_header=True)
    pred_file = open(os.path.join(DIR,PROSODIC_PREDICTION_FILE),"w")
    #sel = [12,13,14,15,21,22,23,24]
    sel = range(7,30)
    train_samples, train_classes, train_headers = filter_data_rows(eval1, sel=sel, keep_headers=True)
    
    if(test_with_pilot):
        print "\nLoading BULATS pilot test data"
        pilot = read_file(os.path.join(DIR,PILOT_FILE_NORMED), ',', skip_header=False)
        pilot_samples, pilot_classes, pilot_headers = filter_data_rows(pilot, sel=sel, keep_headers=True)
        X_train = train_samples
        y_train = train_classes
        X_test = pilot_samples
        y_test = pilot_classes
    else:
        #don't use the pilot data, and instead hold out some of eval1 to test
        X_train, X_test, y_train, y_test = train_test_split(train_samples, train_classes, test_size=0.80, random_state=0, stratify=train_classes)
        
    #samps_raw, tclasses = X_test, y_test
    #TODO this code calls hacky routine that equalises the number of pos/neg items by shuffling and discarding negatives... should probably use class weighting on the svm itself
#     wgt = 12.0
#     
#     classWeight = {0:(1/(1+wgt)),1:(wgt/(1+wgt))}  
#     print "classWeight", classWeight

    k = 'rbf'
    cache = 800
        

#     samples, classes = shuff_trim_balance_classes(samples,classes)
    
    scaler = preprocessing.StandardScaler().fit( np.array(X_train) )

    X_train = scaler.transform(X_train)
    
    
    print "no samples", len(X_train)
    print "feature dim", len(X_train[0])
    print "no class specifiers", len(y_train)

    #set default values for gamma and C...
    best_gamma = 0.01  #3.0517578125e-05
    best_C = 0.01 # 0.5
    best_kernel='poly'
    best_degree = 2

    clf = None    
    #override the defaults with the results of a grid search if desired (takes a while)
    if(do_search):
        
        cmin, cmax, cstep = -5,  17,  2
        cr = range(cmin,cmax,cstep)
        print(cr)
        #c_range = [ pow(2, y) for y in cr]
        c_range = [0.001, 0.01, 1, 10, 100, 1000, 10000]
        print('c_range', c_range)
            
        param_grid = [
                    {'C': c_range },
                ]
        
        param_dist={'C': scipy.stats.expon(scale=100), 'class_weight':['balanced', None]}
        
        print scipy.stats.expon(scale=100)
        
        estr= LogisticRegression(class_weight='balanced')
        #estr= LogisticRegression()
#         searcher = GridSearchCV(estr, param_grid, n_jobs=-1, cv=3, verbose=True, scoring="recall")
        searcher = RandomizedSearchCV(estr, param_distributions=param_dist, n_iter=200, n_jobs=-1, cv=5, verbose=True, scoring='recall') 
#         searcher = LogisticRegressionCV(Cs=50, fit_intercept=True, cv=8, dual=False, penalty='l2', scoring='recall_weighted', solver='lbfgs', tol=0.0001, max_iter=100, class_weight='balanced', n_jobs=-1, verbose=1, refit=True, intercept_scaling=1.0, multi_class='ovr', random_state=None)
        searcher.fit(X_train,y_train)
      
#         print "best params =", searcher.best_params_
#         print "best score  =", searcher.best_score_
      
        clf=searcher

    print clf
    print clf.get_params()
    print clf.best_estimator_
    print clf.best_params_
    print clf.best_score_
    
    X_test = scaler.transform(X_test)
    print "num test cases", len(X_test)
    
    predictions = -1.0 * clf.predict_log_proba(X_test) #this is a list of pairs of probs in form [ [1-p, p],  ... ]
    #predictions = clf.predict_proba(X_test)
    predicted_classes = clf.predict(X_test)
    
    #print predicted_classes
    #print tclasses
    print("TEST: Number of mislabelled points out of a total %d points : %d" % (len(X_test),(y_test != predicted_classes).sum()))
    print(classification_report(y_test, predicted_classes))
    
    pred_file.write("labels 0 1\n") #this emulates an earlier file format for compatibility
    for sooth, p, pc in zip(y_test, predictions,predicted_classes):
        pred_file.write("%d %f %f %d\n" % (pc,p[0],p[1], sooth))
    pred_file.flush()
    pred_file.close()
    print "wrote predictions file:",pred_file