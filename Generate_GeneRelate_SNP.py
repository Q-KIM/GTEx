#!/usr/bin/python

# Generate the gene-related SNPs.
# Songpeng Sam Zu
# 20140518

import sys
import re
import os

def GeneRelSNP(snplocationfile,genelocationfile,snpchrlocfile,outname,startline,endline):

    # load file.
    with open(genelocationfile) as g:
        geneloc = g.readlines()
    g.close()
    with open(snplocationfile) as s:
        snploc = s.readlines()
    s.close()
    with open(snpchrlocfile) as t:
        chrloc = t.readlines()
    t.close()

    # Map and Write to file.

    cutnum = 1000000
    startline = startline - 1
    endline = endline # Note python array[m:n] return array[m,n-1] 
    outfile = open(outname,'w')
    for gline in geneloc[startline:endline]:
        gline = gline.strip()
        genevec = gline.split('\t')
        print(genevec[0])
        tmplist = []
        tmplist.append(genevec[0])
        
        snplocstart = 0
        snplocend = 0
        for tline in chrloc:
            if genevec[1] in tline:
                tlinevec = tline.split('\t')
                snplocstart = int(tlinevec[1]) - 1
                snplocend = int(tlinevec[2]) 
                break
        
        for sline in snploc[snplocstart:snplocend]:
            snpvec = sline.split('\t')
            if (int(snpvec[2]) >= (int(genevec[2])-cutnum))& (int(snpvec[2])<= (int(genevec[3])+cutnum)):
                tmplist.append(snpvec[0])
        outfile.write("%s\n" %("\t".join(tmplist)))
    outfile.close()
    return 0

        
if "__main__" == __name__:
    genelocationfile = "Gene_Location"
    snplocationfile = "snp_position_infor"
    snpchrlocfile = "snp.chr.loc"
    
    #outname = "genelocSNPtest"
    GeneRelSNP(snplocationfile,genelocationfile,snpchrlocfile,sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))

