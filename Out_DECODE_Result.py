#!/usr/bin/python

# Output the results of eQTL detection by DECODE
# Songpeng Sam Zu
# 20140526

import sys
import re
import os
#import numpy as np

def ReadFiles(filename):
    return [line.strip() for line in open(filename,'r')]

def JudgeValue(scorelist,bfcut):
    # Note: we return the index indexed by 1 not 0 in python.
    tmpvec = []
    tmp = 0
    for i in scorelist:
        tmp = tmp + 1
        if float(i) >= bfcut:
            tmpvec.append(tmp)
    return tmpvec

def OutDECODE(genetosnpfile,genetosnpbf,bfcut,outfilename):

    # Load Files.
    gene2snpname = ReadFiles(genetosnpfile)
    gene2snpbf = ReadFiles(genetosnpbf)

    # Finding Bayes Factors larger than bfcut.

    outfile = open(outfilename,'a')
    
    for bfline in gene2snpbf:
        bfvec = bfline.split('\t')
        genename = bfvec.pop(0)
        print(genename)
        locposvec = JudgeValue(bfvec,bfcut)
        if locposvec:
            for nmline in gene2snpname:
                if genename in nmline:
                    nmvec = nmline.split('\t')
                    #nmvec.pop(0)
                    for ele in locposvec:
                        tmplist = []
                        tmplist.append(genename)
                        tmplist.append(nmvec[ele])
                        tmplist.append(bfvec[ele-1])
                        outfile.write("%s\n" %("\t".join(tmplist)))
                    break
    outfile.close()                                  
    return 0
def main():
    # something should be here.
if __name__ == "__main__":

    genetosnpfile = "genelocsnp"
    filenames = "Blood_bfscore_1"
    testfile3 = "outputtest"
    testcut = 1
    OutDECODE(testfile1,testfile2,testcut,testfile3)
    
    
    
