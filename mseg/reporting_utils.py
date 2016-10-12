'''
Created on Oct 12, 2016

@author: rjm49
'''

def get_prF(gold, hyps):
    (tp,tn,fp,fn) = get_counts(gold,hyps)
    p = 1.0 if (tp+fp==0) else (tp / (tp + fp)) #cases found / (cases found + wrongly assumed cases)
    r = 1.0 if (tp+fn==0) else (tp / (tp + fn)) #cases found / (cases found + cases not found) 
    #print p, r
    F = 0 if (p+r==0) else (2*p*r / (p+r))
    return (p,r,F)

def get_accuracy(gold,hyps):
    (tp,tn,fp,fn) = get_counts(gold,hyps)
    acc = (tp+tn)/(tp+tn+fp+fn)
    return acc

def get_baseline_accuracy(gold,hyps):
    (tp,tn,fp,fn) = get_counts(gold,hyps)
    
    #we do not hypothesis any postives in the baseline
    tn += fp #move all fp to tn
    fn += tp #move all tp to fn

# the following commented steps are illustrative .. we've simplified them out
#     tp=0
#     fp=0

#    acc = (tp+tn)/(tp+tn+fp+fn)
    base_acc = tn / (tn+fn)
    return base_acc

def get_counts(gold, hyps):
    tp=0.0
    fp=0.0
    fn=0.0
    tn=0.0
    for g,h in zip(gold,hyps):        
        if (h==1 and g==1):
            tp +=1
        elif (h==1 and g==0):
            fp +=1
        elif (h==0 and g==1):
            fn +=1
        elif (h==0 and g==0):
            tn +=1
    return (tp, tn, fp, fn)

def mini_summary(name, gold, hyps):
    print "STATS FOR ", name
    print "(tp,tn,fp,fn)=", get_counts(gold, hyps)
    p,r,F = get_prF(gold, hyps)
    print "prF=", p,r,F
    acc = get_accuracy(gold, hyps)
    print "acc=", acc
    b_acc = get_baseline_accuracy(gold, hyps)
    print "b_acc=", b_acc