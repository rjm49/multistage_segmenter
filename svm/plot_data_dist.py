import os
import sys

from sklearn import svm, datasets, preprocessing

import matplotlib.pyplot as plt
from common import *
import numpy as np


def plot_compare(samples, classes, headers):
    scaler = preprocessing.StandardScaler().fit( np.array(samples) )
    samples = scaler.transform(samples)
    print "no test cases", len(samples)
    
    num_feats = len(headers)
    
    segs = []
    negs = []
    for n in range(len(samples)):
        if(classes[n]==1):
            segs.append(samples[n])
        else:
            negs.append(samples[n])
    
    np_samples = np.array(samples)
    segs_arr = np.array(segs)
    negs_arr = np.array(negs)
    
    for i in range(num_feats):
        
        if(len(headers)!=num_feats):
            print("headers != num_feats")
            print(len(headers))
            print(len(segs_arr[0]))
            break
    
        feat_name = headers[i]
        print(i)
        
        
        
        
        for j,arr in enumerate([segs_arr, negs_arr]):
            
            vals = arr[:,i]
    #         maxx = max(vals)
    #         minn = min(vals)
    #         mean = np.mean(vals)
    #         sdev = np.std(vals)
    
            #use the scaling values from all data
            maxx = max(vals)
            minn = min(vals)
            mean = np.mean(vals)
            sdev = np.std(vals)
    
            plot_num = (2*i)+j+1
            print feat_name
            print("-({})----({})".format(plot_num, feat_name))
         
            rng = maxx - minn
            vals = (vals-mean) / rng#centre the distro and divide by the range to get values in [-1,1]
     
            print(min(vals), np.mean(vals), max(vals))
    #         thresh = 2.0*np.std(vals)
    #         print "thresh be ", thresh
            
            #scaler = preprocessing.StandardScaler().fit( np.array(vals) )
            #vals = scaler.transform(vals)
    
            colour = "red" if (plot_num % 2 == 0) else "blue"
            
            # Plot the decision boundary. For that, we will assign a color to each
            # point in the mesh [x_min, m_max]x[y_min, y_max].
            plt.subplot((2*num_feats), 1, plot_num)
            plt.subplots_adjust(wspace=0.4, hspace=0.4)
        
            plt.hist(vals, bins=100, color=colour)
            # Plot also the training points
            plt.xticks(())
            plt.yticks(())
            if j==0:
                plt.ylabel(str(i))
            plt.axvline(0.0, color="black")
            #plt.axvline(np.mean(vals), color="green")
            plt.axvline(min(vals), color="green")
            plt.axvline(max(vals), color="green")
            plt.xlim([-1.0,1.0])
    plt.show()
    
if __name__ == '__main__':
    all_rows = read_file(os.path.join(DIR,EVAL1_FILE_NORMED), ',', skip_header=False)
    (samples, classes, headers) = filter_data_rows(all_rows, keep_headers=True)
    plot_compare(samples, classes, headers)
