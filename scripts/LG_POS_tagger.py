'''
Created on Jul 7, 2016

@author: rjm49
'''
from __future__ import division
import os
from nltk import word_tokenize, pos_tag

#nltk.download()

in_path = '/home/rjm49/mseg/e1'
out_path = '/home/rjm49/mseg/e1'
fname = 'normed.txt'
out_fname = 'pos_out.txt'

raw_file = open(os.path.join(in_path,fname), 'r')
raw_text = raw_file.read();
raw_file.close()

sents = raw_text.split('\n')
t_sents = []

print len(sents), 'sentences'

for sent in sents:
    tox = sent.split()
    tox = ['.' if x=="<break>" else x for x in tox]
    tox = [x.upper() if (len(x)==1 and x!='a') else x for x in tox]
        
    #tox = word_tokenize(sent)
    #print tox
    t_sent = pos_tag(tox)
    #print t_sent
    t_sents.append(t_sent)
    
# _ = raw_input("hit key")

out_file = open(os.path.join(out_path,out_fname), 'w')

for t_sent in t_sents:
    out_str=''
    for tok in t_sent:
        #print tok
        #out_str = out_str + ' ' + tok[0].lower() + '/' + tok[1]
        out_str = out_str + ' ' + ('<break>' if tok[0]=='.' else tok[1])
    out_str = out_str.strip()
    print out_str
    out_file.write(out_str+'\n')
out_file.close()
print 'Wrote: ' + str(out_file) + '\n'