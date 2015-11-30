## import modules
import nltk, csv, codecs, collections
from random import shuffle
from nltk.util import ngrams
from collections import Counter
import nltk.metrics
import sys

## method to load data
def read_file(filename , n=0):
    listobj = []  # empty list
    reader = codecs.open(filename, 'r')  # open file
    next(reader)  # skip header line
    ## for each line in file
    i=0
    for line in reader:
        if n>0 and i>=n:
            break
        line = line.rstrip()  # remove trailing characters
        rowin = line.split(',')  # split on commas
        listobj.append((rowin))  # append to eval1 list (list of lists)
        i+=1
    print "number of tokens loaded:", len(listobj)
    return listobj

## method for feature sets
def item_feats(listobj, rowno):
    features = {}
    features['prepause'] = listobj[rowno][7]
    features['postpause'] = listobj[rowno][8]
    features['phonDurFinal'] = listobj[rowno][9]
    features['phonDurVowels'] = listobj[rowno][10]
    features['phonDurMax'] = listobj[rowno][11]
    features['f0diffWplus1'] = listobj[rowno][12]
    features['f0diffEndWminF0'] = listobj[rowno][13]
    features['f0diffMeanWminF0'] = listobj[rowno][14]
    features['f0diffStartWminF0'] = listobj[rowno][15]
    features['f0diffMeanWplus1minF0'] = listobj[rowno][16]
    features['f0maxW'] = listobj[rowno][17]
    features['f0minW'] = listobj[rowno][18]
    features['f0maxWplus1'] = listobj[rowno][19]
    features['f0minWplus1'] = listobj[rowno][20]
    features['EdiffWplus1'] = listobj[rowno][21]
    features['EdiffEndWminE'] = listobj[rowno][22]
    features['EdiffMeanWminE'] = listobj[rowno][23]
    features['EdiffStartWminE'] = listobj[rowno][24]
    features['EdiffMeanWplus1minE'] = listobj[rowno][25]
    features['EmaxW'] = listobj[rowno][26]
    features['EminW'] = listobj[rowno][27]
    features['EmaxWplus1'] = listobj[rowno][28]
    features['EminWplus1'] = listobj[rowno][29]
    return features

## method to index labels and extract feature sets
def get_feats(listobj):

    index_boundaries = [(row, "sb" + listobj[row][6]) for row in range(1, len(listobj))]
#     print index_boundaries
#     sys.stdin.readline()
    
    featsets = [(item_feats(listobj, n), bound) for (n, bound) in index_boundaries]
#    shuffle(featsets)  # randomize order
#     for fs in featsets:
#         print fs
    #sys.stdin.readline()
    return featsets

## metrics: classifier accuracy, precision, recall, F-measure
def classifi_metrics(classifi):
    print 'overall accuracy:', nltk.classify.accuracy(classifi, testfeats)
    refset = collections.defaultdict(set)
    testset = collections.defaultdict(set)
    text = ''  # build a new 'transcript' with the hypothesised sentence boundaries
    ## expected and observed labels foreach token
    for i, (feats, label) in enumerate(testfeats):
        text += pilot[i][5].strip('\"') + ' '
        refset[label].add(i)
        observed = classifi.classify(feats)
        testset[observed].add(i)
        if observed == 'sb1':
            text = text.rstrip()
            text += '.\n'
    ## now print for each label
    sbounds = ["sb0", "sb1"]
    for sb in sbounds:
        print "\nSENTENCE BOUNDARY: %s" % sb
        print 'precision:', nltk.metrics.precision(refset[sb], testset[sb])
        print 'recall:', nltk.metrics.recall(refset[sb], testset[sb])
        print 'F-measure:', nltk.metrics.f_measure(refset[sb], testset[sb])
    return text


if __name__ == '__main__':

    folder = "C:\\Users\\Russell\\Dropbox\\nlp_alta\\recreate_LG\\datafiles\\"
    n = 10000

    ## eval1 training set
    print "\nLoading BULATS eval1 training data"
    eval1file = folder+'eval1-prosodicFeats.csv'
    eval1 = read_file(eval1file, n)
    
    ## pilot test set
    print "\nLoading BULATS pilot test data"
    pilotfile = folder+'pilot-prosodicFeats.csv'
    pilot = read_file(pilotfile, 1000)

    print "\nBuilding test and training feature sets..."
    ## build test and training feature sets
    trainfeats = get_feats(eval1)
    testfeats = get_feats(pilot)
    print "\nDone"

    ## naive Bayes classifier
    print "\nTraining naive Bayes classifier..."
    nbClassifier = nltk.NaiveBayesClassifier.train(trainfeats)
    transcript = classifi_metrics(nbClassifier)
    #print transcript
    
    ## and i think this is an svm classifier (http://www.nltk.org/api/nltk.classify.html)
    from sklearn.svm import SVC
    from nltk.classify.scikitlearn import SklearnClassifier
    classif = SklearnClassifier(SVC(kernel='rbf',probability=True))
    print "\nTraining SVM classifier..."
    svmClassifier = classif.train(trainfeats)
    transcript = classifi_metrics(svmClassifier)
    #print transcript
