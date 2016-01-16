import numpy as np
from sklearn import svm, datasets, preprocessing
import codecs
import sys
import grid_search as gs
from random import shuffle
from sklearn.metrics.classification import precision_recall_fscore_support,\
    classification_report
from multistage_segmenter.common import *
from multistage_segmenter.svm.balance import sep_classes, shuff_trim_balance_classes
from sklearn.externals import joblib

do_grid_search = False

if __name__ == '__main__':
## eval1 training set
    print "\nLoading BULATS eval1 training data"
    eval1 = read_file(os.path.join(DIR,EVAL1_FILE_NORMED), ',', skip_header=True)
    pred_file = open(os.path.join(DIR,PROSODIC_PREDICTION_FILE),"w")
    #sel = [12,13,14,15,21,22,23,24]
    sel = range(7,30)
    samples, classes = filter_data_rows(eval1, sel=sel)

    #TODO this code calls hacky routine that equalises the number of pos/neg items by shuffling and discarding negatives... should probably use class weighting on the svm itself
    samples, classes = shuff_trim_balance_classes(samples,classes)

    scaler = preprocessing.StandardScaler().fit( np.array(samples) )
    
    X = scaler.transform(samples)
    
    print X.mean(axis=0)
    print X.std(axis=0)
    
    Y = classes
    
#     for i,s in enumerate(samples):
#         print s
#         print classes[i]
    
    print "no samples", len(samples)
    print "feature dim", len(samples[0])
    print "no classes", len(classes)

    #set default values for gamma and C...
    best_gamma = 3.0517578125e-05
    best_C = 0.5
    
    #override the defaults with the results of a grid search if desired (takes a while)
    if(do_grid_search):
        best_params = gs.grid_search(samples, classes)
        best_gamma=best_params['gamma']
        best_C=best_params['C']
       
    #clf = svm.SVC(kernel='linear', gamma=0.7, C=1.0, probability=True)
    
    clf = None
    pickled_model = "svm_classifier.pkl"
    
    if(os.path.exists(pickled_model) and os.path.isfile(pickled_model)):
        pickled = True
    
    if(pickled):
        clf = joblib.load(pickled_model)
    else: 
        clf = svm.SVC(kernel='rbf', C=best_C, gamma=best_gamma, cache_size=2000, probability=True)
    print clf

    print "HIT ANY KEY TO CONTINUE..."
#    sys.stdin.readline()
    print "FITTING"
     
    clf.fit(X, Y)
    print clf
    
    if(not pickled):
        joblib.dump(clf, pickled_model) 
    
    ## pilot test set
    print "\nLoading BULATS pilot test data"
    pilot = read_file(os.path.join(DIR,PILOT_FILE_NORMED), ',', skip_header=True)
    samps_raw, tclasses = filter_data_rows(pilot, sel=sel)
    
    tsamples = scaler.transform(samps_raw)
    print "no test cases", len(tsamples)
    
    predictions = clf.predict_proba(tsamples) #this is a list of pairs of probs in form [ [1-p, p],  ... ]
    p_classes = clf.predict(tsamples)
    
    print p_classes
    print tclasses
    print("TEST: Number of mislabelled points out of a total %d points : %d" % (len(tsamples),(tclasses != p_classes).sum()))
    print(classification_report(tclasses, p_classes))

    print len(clf.support_vectors_)
    
    for p in predictions:
        pred_file.write(str(p)+"\n")
    pred_file.flush()
    pred_file.close()