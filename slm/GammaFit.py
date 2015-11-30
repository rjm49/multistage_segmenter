from scipy.stats import gamma
import matplotlib.pyplot as plt

'''
Created on 4 Aug 2015

@author: Russell
'''

if __name__ == '__main__':
    alpha = 5
    loc = 100.5
    beta = 22
    r = gamma.rvs(alpha, loc=loc, scale=beta, size=1000)
    print r
    
    fit_alpha, fit_loc, fit_beta= gamma.fit(r)
    print(fit_alpha, fit_loc, fit_beta)