import codecs
import os
import sys

from sklearn import svm, datasets, preprocessing
from sklearn.metrics.classification import precision_recall_fscore_support
from sklearn.naive_bayes import GaussianNB

import grid_search as searcher
import matplotlib.pyplot as plt
from common import read_file, DIR, TRAIN_FILE_DEFAULT, \
    filter_data_rows, TEST_FILE_DEFAULT
import numpy as np


if __name__ == '__main__':
## eval1 training set
    print "\nLoading BULATS eval1 training data"
    eval1file = os.path.join(DIR,TRAIN_FILE_DEFAULT)
    eval1 = read_file(eval1file, ',', skip_header=True) 
    sel = range(7,30)
    samples, classes = filter_data_rows(eval1, sel=sel)
        
    Xraw = samples
    scaler = preprocessing.StandardScaler().fit( np.array(Xraw) )    
    tr_samples = scaler.transform(Xraw)

    gnb = GaussianNB()

    print "HIT ANY KEY TO CONTINUE..."
    sys.stdin.readline()
    print "FITTING"
    
#     tr_samples = [[-1,-1],[-2,-3],[3,2],[8,3]]
#     Y = [0,0,1,1]
    y_pred = gnb.fit(tr_samples,classes).predict(tr_samples)
    print("XV: Number of mislabelled points out of a total %d points : %d" % (len(samples),(classes != y_pred).sum()))
    
#     predictions = clf.predict([[-3,-3],[2.6,3],[-3,2]])
#     print predictions
#     print clf.predict_proba([[-3,-3],[2.6,3],[-3,2]])
    
    ## pilot test set
    print "\nLoading BULATS pilot test data"
    pilotfile = os.path.join(DIR,TEST_FILE_DEFAULT)
    pilot = read_file(pilotfile, ',', skip_header=True) 
    samps_raw, tclasses = filter_data_rows(pilot, sel=sel)
    
    tsamples = scaler.transform(samps_raw)
    y_pred = gnb.predict(tsamples)
    
    print y_pred
    print tclasses
    
    print("TEST: Number of mislabelled points out of a total %d points : %d" % (len(samps_raw),(tclasses != y_pred).sum()))
    
    prf = precision_recall_fscore_support(tclasses, y_pred, average='binary')
    
    print(prf)
    
#     for i,p in enumerate(y_pred):
#         if (p>0.5):
#             print str(i)+':', p, 'vs', classes[i]