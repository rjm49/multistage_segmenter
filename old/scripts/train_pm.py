#!/usr/bin/env python
'''
Created on May 16, 2016

@author: rjm49
'''
import argparse
from operator import itemgetter
import os
import sys

from numpy.random.mtrand import np
import scipy.stats
from sklearn import preprocessing, svm
from sklearn.cross_validation import train_test_split
from sklearn.externals import joblib
from sklearn.grid_search import RandomizedSearchCV
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.metrics.classification import classification_report

from mseg.common import TRAIN_FILE_DEFAULT, TEST_FILE_DEFAULT, read_file


overwrite_pkl = True

def dissect(data, selection_columns):
    headers = [data[0][i] for i in selection_columns]
    words = [r[5] for r in data]
    samples = [[float(r[i]) for i in selection_columns] for r in data]
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

def main(args):
## tr_data training set
    parser = argparse.ArgumentParser()
    parser.add_argument("base_dir", nargs='?', default= os.path.join(os.getcwd(),"mseg_workspace"), help="this is the working directory, all sub dirs live under it")
    parser.add_argument("pm_dir", nargs='?', default="pm_default", help="this is the directory in which to store the prosodic model file")
    parser.add_argument("training_file", nargs='?', default=TRAIN_FILE_DEFAULT, help="name of CSV file that contains correctly annotated training examples")
    parser.add_argument("test_file", nargs='?', default=TEST_FILE_DEFAULT, help="name of CSV file that contains mysterious cases that must be tested")
    parser.add_argument("-lr", "--logistic_regression", default=False, action="store_true", help="use logistic regression classifier (default is RBF-SVM)")
    args = parser.parse_args()

    base_dir = args.base_dir
    pm_dir = args.pm_dir
    tr_file = args.training_file
    test_fname = args.test_file
    use_lr = args.logistic_regression
    
#     if(len(args)==3):
#         base_dir = args[0]
#         pm_dir = args[1]
#         tr_file = args[2]
#         test_fname = args[3]
#     else:
#         base_dir = DIR
#         pm_dir = "pm_default"
#         tr_file = TRAIN_FILE_DEFAULT
#         test_fname = TEST_FILE_DEFAULT
# #         do_search = False
# #         use_pilot = False
    n_samples = -1
    cache = 800
    
#     pm_dir= raw_input("enter PM name: [%s]" % pm_dir) or pm_dir
#     tr_file = raw_input("enter PM training file name: [%s]" % tr_file) or tr_file
    
    tr_data = read_file(os.path.join(base_dir, tr_file), ',', skip_header=True)
    
#     test_fname = raw_input("enter file to test on: [%s]" % test_fname) or test_fname
#     use_lr = bool(raw_input("use logistic regression [False]?")) or False

    if not use_lr:
        n_samples = 6000
        out_fname = test_fname+"-probabilities.dat"
        report_fname = test_fname+"-report.txt"
    else: 
        out_fname = test_fname+"-probabilities.dat"
        report_fname = test_fname+"-report-LR.txt"

    out_file = os.path.join(base_dir, pm_dir, out_fname)
    report_fname = os.path.join(base_dir, pm_dir, report_fname)
    #clear extant predictions file
    if(os.path.exists(out_file)):
        os.remove(out_file)
        print "removed",out_file
        
    print base_dir+"/"+tr_file+" -SVM-> ",out_file
    

    test_data = read_file(os.path.join(base_dir, test_fname), ',', skip_header=True)
    
    #sel = [12,13,14,15,21,22,23,24]
    sel = range(7,30)
    #sel = [8,21,29, 24,25,27]

    (_, _, tr_samples, tr_classes) = dissect(tr_data, sel)
    (_, te_words, te_samples, te_classes) = dissect(test_data, sel)
       
    if n_samples>0:
        tr_samples, _, tr_classes, _ =  train_test_split(tr_samples, tr_classes, train_size=n_samples, stratify=tr_classes) 
    
    p = sum(c==1.0 for c in tr_classes) # count the positive instances
    n = len(tr_classes) - p # derive the negative instances
    print "n=",n," p=",p
    wgt=float(n)/float(p) # cast and divide
    print "wgt=",wgt
#     classWeight = { 1: wgt }
    
    
    #tr_samples, te_samples, tr_classes, te_classes = train_test_split(samples, classes, test_size=0.20, random_state=0, stratify=classes)
                    
    scaler = preprocessing.StandardScaler().fit( np.array(tr_samples) )
    tr_samples = scaler.transform(tr_samples)

             
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
        
        c_dist =  scipy.stats.expon(scale=100)
        gamma_dist = scipy.stats.expon(scale=.01)
        
        if use_lr:
            estr = LogisticRegression(class_weight='balanced')
#             estr = LogisticRegression()
            param_dist={'C': c_dist }
        else:
            estr = svm.SVC(kernel='rbf', cache_size=800, probability=True, class_weight='balanced' )
            #estr = svm.LinearSVC(class_weight='balanced')
            param_dist={'C': c_dist , 'gamma': gamma_dist}
            
        
        #searcher = RandomizedSearchCV(estr, param_distributions=param_dist, n_iter=100, n_jobs=-1, cv=5, verbose=True ) #, scoring="recall")
        searcher = RandomizedSearchCV(estr, param_distributions=param_dist, n_iter=100, n_jobs=-1, verbose=True, scoring="recall")
        searcher.fit(tr_samples,tr_classes)
        report(searcher.grid_scores_)
        clf = searcher.best_estimator_         

        print "COMPARING CLF PARAMS WITH BEST PARAMS (shd be same)"
        print clf.get_params()
        print best_params
        
        joblib.dump(clf, pickled_model)
        
    print clf

#     print "FITTING"     
#     clf.set_params(verbose=True)
#     clf.fit(tr_samples, tr_classes)
#     print clf
     
    
    #NOW TO TEST AGAINST HELD-OUT/TEST DATA
    te_samples = scaler.transform(te_samples)
    
    print "no test cases", len(te_samples)
    
    predictions = -1.0 * clf.predict_log_proba(te_samples) #this is a list of pairs of probs in form [ [1-p, p],  ... ]
    #predictions = -1.0 * clf.decision_function(te_samples)
    print predictions
    predicted_classes = clf.predict(te_samples)
    
    print("TEST: Number of mislabelled points out of a total %d points : %d" % (len(te_samples),(te_classes != predicted_classes).sum()))
    print(classification_report(te_classes, predicted_classes))

    
    rpt = open(report_fname, "w")
    rpt.write(classification_report(te_classes, predicted_classes))
    rpt.write("\n")
    rpt.close()
    print "wrote report file", rpt
    
    pred_file = open(out_file,"w")
    pred_file.write("labels 0 1\n") #this emulates an earlier file format for compatibility
    for word, prob_tuple, guessed_class in zip(te_words,predictions,predicted_classes):
        pred_file.write("%d %f %f %s\n" % (guessed_class,prob_tuple[0],prob_tuple[1],word))

    pred_file.close()
    print "wrote predictions file:",pred_file
    

if __name__ == '__main__':
    main(sys.argv[1:])