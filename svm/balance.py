'''
Created on 19 Nov 2015

@author: Russell
'''
from random import shuffle

def sep_classes(samples, classes):
    segs = []
    negs = []
    for i,s in enumerate(samples):
        if(classes[i]==1.0):
            segs.append(s)
        else:
            negs.append(s)
    return segs,negs

def shuff_trim_balance_classes(samples, classes, wgt=1.0, max_size=None):
    segs, negs = sep_classes(samples, classes)
    
    shuffle(negs)
    print("We have {0} boundary examples".format(len(segs)))
    negs = negs[:int(len(segs)*wgt)]
    if(max_size):
        negs = negs[0:max_size] 
        segs = segs[0:max_size]
    
    samples = negs + segs
    print("Using {0} data samples".format(len(samples)))
    
    #raw_input("press any key")

    classes = []
    for n in negs:
        classes.append(0.0)
    for s in segs:
        classes.append(1.0)
        
    return samples, classes