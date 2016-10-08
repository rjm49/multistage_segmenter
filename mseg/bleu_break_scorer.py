'''
Created on Jun 18, 2016

@author: rjm49
'''
from math import exp, log
from mseg.common import BREAK

#set max n-gram length

def getBLEU(C,R, N=4, breaks_only=True, strict=False):    
    s=0.0
    precisions = []

    for n in range(1,N+1):
        wN = 1.0/N
        p_n = p(C, R, n, breaks_only=breaks_only, strict=strict)
        #print "N=",n, "p_n=", p_n
        precisions.append(p_n)
        if p_n > 0:
            s += wN * log(p_n)
            
    bp = BP(C,R)
    bleu = bp * exp(s)
    return (bleu, precisions, bp)
    
def p(C, R, n, breaks_only=True, strict=False):
    #first we need all n-grams in Candidate
    ngrams = get_ngrams_in_cand(C, n, breaks_only=breaks_only, louche_mode=(not strict))
    
    num=0.0
    denom=0.0
    for g in ngrams:
        cand_ct = ct(C,g)
        ref_ct = ct(R,g)
        ct_clip = min(ref_ct, cand_ct)
        
        #print "for ngram ",g,"ref_ct=",ref_ct,"cand_ct=",cand_ct,"ct_clip=",ct_clip
        
        num += ct_clip
        denom += cand_ct    
    r = float(num)/float(denom)
#     print g, num, denom, r
    return r
    
def ct(C, g):
    '''counts the number of ngrams in a text corpus'''
    C = C.split() # convert to list
    ct = 0
    n = len(g)
    for i in range(len(C)-n+1):
        x = tuple(C[i:i+n])
        if (g == x): 
            ct += 1
    return ct


def BP(C,R):
    c = float(len(C.split()))
    r = float(len(R.split()))
    if c>r:
        return 1.0
    else:
        return exp(1.0-(r/c))

def get_ngrams_in_cand(C, n, breaks_only=False, louche_mode=False):
    C = C.split() # convert to list
    output = set()
    for i in range(len(C)-n+1):
        g = tuple(C[i:i+n])
        if (not breaks_only) or (louche_mode and (BREAK in g)) or g[-1]==BREAK:
            output.add(g)
      
    print "candidate "+str(n)+"-grams: ",output
    return output #shd now be the set of all (n)-grams in C 

    
if __name__ == '__main__':
    print "calculating BLEU for test sentences"
    
    C = "the cat sat on the mat <break> the dog sat <break> by the door eating <break> a bone"
#     C = "the cat sat on the mat <break> the dog sat by the door eating a bone"
    R = "the cat sat on the mat <break> the dog sat by the door eating <break> a bone"
    
    print getBLEU(C, R, strict=False)
    print getBLEU(C, R, strict=True)
    
    
    