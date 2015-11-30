import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm, datasets, preprocessing
from sklearn.naive_bayes import GaussianNB
import codecs
import sys
import grid_search as gs
from sklearn.metrics.classification import precision_recall_fscore_support
from multistage_segmenter.common import read_file


if __name__ == '__main__':
## eval1 training set
    print "\nLoading BULATS eval1 training data"
    eval1file = 'C:\\Users\\Russell\\Dropbox\\nlp_alta\\recreate_LG\\datafiles\\eval1-prosodicFeats_norm.csv'
    eval1 = read_file(eval1file)    
    samples, classes = filter(eval1)
        
    Xraw = samples
    scaler = preprocessing.StandardScaler().fit( np.array(Xraw) )    
    X = scaler.transform(Xraw)

    gnb = GaussianNB()

    print "HIT ANY KEY TO CONTINUE..."
    sys.stdin.readline()
    print "FITTING"
    
#     X = [[-1,-1],[-2,-3],[3,2],[8,3]]
#     Y = [0,0,1,1]
    y_pred = gnb.fit(X,classes).predict(X)
    print("XV: Number of mislabelled points out of a total %d points : %d" % (len(samples),(classes != y_pred).sum()))
    
#     predictions = clf.predict([[-3,-3],[2.6,3],[-3,2]])
#     print predictions
#     print clf.predict_proba([[-3,-3],[2.6,3],[-3,2]])
    
    ## pilot test set
    print "\nLoading BULATS pilot test data"
    pilotfile = 'C:\\Users\\Russell\\Dropbox\\nlp_alta\\recreate_LG\\datafiles\\pilot-prosodicFeats_norm.csv'
    pilot = read_file(pilotfile)
    samps_raw, tclasses = filter(pilot)
    
    tsamples = scaler.transform(samps_raw)
    y_pred = gnb.predict(tsamples)
    print("TEST: Number of mislabelled points out of a total %d points : %d" % (len(samps_raw),(tclasses != y_pred).sum()))
    
    prf = precision_recall_fscore_support(tclasses, y_pred, average='binary')
    
    print(prf)
    
#     for i,p in enumerate(y_pred):
#         if (p>0.5):
#             print str(i)+':', p, 'vs', classes[i]