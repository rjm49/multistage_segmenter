'''
Created on 24 Jun 2015

@author: Russell
'''
import codecs


## method to load data
def read_file(filename):
    listobj = []  # empty list
    reader = codecs.open(filename, 'r')  # open file
    next(reader)  # skip header line
    ## for each line in file
    for line in reader:
        line = line.rstrip()  # remove trailing characters
        rowin = line.split(',')  # split on commas
        listobj.append((rowin))  # append to eval1 list (list of lists)
    print "number of tokens loaded:", len(listobj)
    return listobj

def convert_row(row):
    offset = 6
    #maxx = 29
    maxx = 11 #let's see what happens if we just try the first five (pause/duration) features
    outrow = ""
    outrow += row[offset]+" "
    for i in range(offset,len(row)):
        if i>offset: #0..29 rows
            outrow += str(i-offset) +":"+ str(row[i])
            if i==maxx:
                outrow += "\n"
                return outrow
            else:
                outrow += " "
    return outrow

if __name__ == '__main__':
    
    ## eval1 training set
    print "\nConverting prosodic data files into SVM parameters"
    
    in_dir = 'C:\\Users\\Russell\\Dropbox\\nlp_alta\\recreate_LG\\datafiles\\'
    out_dir = 'C:\\Users\\Russell\\Dropbox\\nlp_alta\\recreate_LG\\svm_datafiles\\'
    infiles = ['eval1-prosodicFeats_norm.csv','pilot-prosodicFeats_norm.csv']
    outfiles = ['train.dat','test.dat']
    
    for (inn,out) in zip(infiles,outfiles):
        reader = read_file(in_dir + inn)
        writer = codecs.open(out_dir + out, 'w')
     
        for row in reader:
            writer.write(convert_row(row))
         
        writer.close()
    