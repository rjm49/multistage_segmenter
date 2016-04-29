'''
Created on 24 Jun 2015

@author: Russell
'''
import codecs


## method to load data
def read_file(filename, skip=False, delim=' '):
    listobj = []  # empty list
    reader = codecs.open(filename, 'r')  # open file
    if(skip):
        next(reader)  # skip header line
    ## for each line in file
    for line in reader:
        line = line.rstrip()  # remove trailing characters
        rowin = line.split(delim)  # split on delimiter
        listobj.append((rowin))  # append to eval1 list (list of lists)
    print "number of tokens loaded:", len(listobj)
    return listobj

def convert_row(row):
    offset = 6
    maxx = 29
    outrow = ""
    outrow += row[offset]+" "
    for i in range(offset,len(row)):
        if i>offset: #0..29 rows
            outrow += str(i-offset) +":"+ str(row[i])
            if i==maxx:
                outrow += "\n"
            else:
                outrow += " "
    return outrow

if __name__ == '__main__':
    
    ## eval1 training set
    print "Analysing SVM output"
    
    in_dir = 'C:\\edrive\\libsvm-3.20\\tools\\'
    out_dir = 'C:\\Users\\Russell\\Dropbox\\nlp_alta\\recreate_LG\\svm_datafiles\\'
    word_dir = 'C:\\Users\\Russell\\Dropbox\\nlp_alta\\recreate_LG\\datafiles\\'
    infiles = ['test.dat']
    predfiles = ['test.dat.predict']
    wordfiles = ['pilot-prosodicFeats_norm.csv']
    
    for (inn,prd,wds) in zip(infiles,predfiles,wordfiles):
        reader = read_file(in_dir + inn)
        reader2 = read_file(in_dir + prd, True)
        reader3 = read_file(word_dir + wds, True, ',')

        false_pos = 0
        false_neg = 0
        true_neg = 0
        true_pos = 0
        num_breaks = 0
             
        for (row,prow,wrow) in zip(reader,reader2,reader3):
            tru = int(row[0])
            gue = int(prow[0])
            wrd = str(wrow[5])
            
            print tru, gue, wrd
  
            if (tru > 0):
                num_breaks += 1
            
            if(tru==gue):
                if tru == 0:
                    true_neg +=1
                if tru == 1:
                    true_pos +=1
            
            if(tru != gue):
                if tru == 0:
                    false_pos += 1
                if tru == 1:
                    false_neg += 1
            
        print "false positives=", false_pos
        print "false negatives=", false_neg
        print "true positives=", true_pos
        print "true negatives=", true_neg
        print "total segment breaks=", num_breaks
        
        r = float(true_pos) / float(false_pos + true_pos)
        p = float(true_pos) / float(num_breaks) 
        
        print "recall ", r
        print "precision ", p
        
        print "f score= ", p*r/(p+r) 