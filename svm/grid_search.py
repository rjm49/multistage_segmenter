'''
Created on 5 Nov 2015

@author: Russell
'''

from __future__ import print_function

from sklearn import datasets
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.svm import SVC
from numpy.f2py.auxfuncs import throw_error

print(__doc__)

def grid_search(samples, classes, wgt):
    if(len(samples)!=len(classes)):
        print("grid_search: mismatching lens of samples and classes")
        return None

    X = samples
    y = classes
    
    # Split the dataset in two equal parts
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=0)
    
    gmin, gmax, gstep = -15, 5, 2
    gr = range(gmin, gmax, gstep)
    print(gr)
    gamma_range = [ pow(2, y) for y in gr ]
    
    cmin, cmax, cstep = -5,  17,  2
    cr = range(cmin,cmax,cstep)
    print(cr)
    c_range = [ pow(2, y) for y in cr]
    
    print('gamma_range', gamma_range)
    print('c_range', c_range)
    
    
    tuned_parameters = [{ #'kernel': ['rbf'],
                         'gamma': gamma_range, #step -2
                         'C': c_range},] #step 2
    
    
    print("# Tuning hyper-parameters")
    print()

    #class_weight={1:2},
    estr = SVC(kernel='rbf', C=1.0, cache_size=6000, class_weight={ 0:wgt }, probability=False)
    #estr = SVC(C=1.0)
    clf = GridSearchCV(estr, tuned_parameters, cv=5, n_jobs=3)
    clf.fit(X_train, y_train)
    
    print("Best parameters set found on development set:")
    print()
    print(clf.best_params_)
    print()
    
    print("Grid scores on development set:")
    print()
    for params, mean_score, scores in clf.grid_scores_:
        print("%0.3f (+/-%0.03f) for %r" % (mean_score, scores.std() * 2, params))
    print()

    print("Detailed classification report:")
    print()
    print("The model is trained on the full development set.")
    print("The scores are computed on the full evaluation set.")
    print()
    y_true, y_pred = y_test, clf.predict(X_test)
    print(classification_report(y_true, y_pred))
    print()
    
    return clf.best_params_