#!/usr/bin/env python

# Generate the sctrips for submitting decode task on odyssey.
# Songpeng Zu 
# The original script is from Daniel.
# 2015-03-03

#-- Import modules
import glob, subprocess, sys, os, optparse
script_path = os.path.dirname(__file__)
myutils_path = os.path.join(script_path, '../myutils')
sys.path.append(myutils_path)
import myos
import general
import execs_commands 
import numpy as np
import math 

def splitinteger(integer,splitnum):
    """Split an integer into roughly equal groups.
       For example:
       splitinteger(100,2)
       Result: [[1,50],[51,100]]
    """
    n = int(math.ceil(integer/splitnum))
    newseq = []
    for i in range(1,splitnum):
        newseq.append([(i-1)*n+1,i*n])
    newseq.append([(splitnum-1)*n+1,integer])
    return(newseq)

def write_DECODE_jobs(logs_dir, input_dir, gene_residual_file, tissuenm, outdir, splitnum = 20, execute = False):
    qname = "serial_requeue" 
    mem_usage = "25000"
    myos.check_if_directory_exists_create_it(logs_dir)
    myos.check_if_directory_exists_create_it(outdir)
    genetotalnum = myos.wccount(input_dir+"genelocsnp")
    taskseq = splitinteger(genetotalnum,splitnum)
    for i in range(0,splitnum):
        job_name = 'gtex_decode'+'_'+str(taskseq[i][0])+'_'+str(taskseq[i][1])
        bsubcmd = myos.write_bsub_string_no_rm_logs_dir(logs_dir,job_name,qname=qname,mem_usage=mem_usage, time='180')
        if os.path.exists(gene_residual_file) is False:
            print "Cannot find some input files!"
            return 0
        exec_cmd = execs_commands.gtex_decode(gene_residual_file, taskseq[i][0], taskseq[i][1],tissuenm,outdir)
        print exec_cmd
        job_script_fn = bsubcmd.split(' ')[-1]
        with open(job_script_fn,'a') as job_script_f:
            print bsubcmd
            job_script_f.write('echo \"%s\"\n' %(exec_cmd))
            job_script_f.write(exec_cmd+'\n')
        if execute:
            os.system(bsubcmd)
    return 0

def main():
    logs_dir = "/n/home00/szu/gtex/logs/"
    input_dir = "/n/home00/szu/KR_eQTL/GTex/"
    outdir = "/n/home00/szu/gtex/"    
    
#    gene_residual_file = "/n/home00/szu/gtex/expr_residual/expr_residual_Breast.txt"
#    tissuenm = "Breast"
    
#    gene_residual_file = "/n/home00/szu/gtex/expr_residual/expr_residual_Adipose.txt"
#    tissuenm = "Adipose"

#    gene_residual_file = "/n/home00/szu/gtex/expr_residual/expr_residual_BloodVessel.txt"
#    tissuenm = "BloodVessel"
    
#    gene_residual_file = "/n/home00/szu/gtex/expr_residual/expr_residual_Brain.txt"
#    tissuenm = "Brain"
    
#    gene_residual_file = "/n/home00/szu/gtex/expr_residual/expr_residual_Colon.txt"
#    tissuenm = "Colon"
    
#    gene_residual_file = "/n/home00/szu/gtex/expr_residual/expr_residual_Esophagus.txt"
#    tissuenm = "Esophagus"
    
#    gene_residual_file = "/n/home00/szu/gtex/expr_residual/expr_residual_Heart.txt"
#    tissuenm = "Heart"
    
#    gene_residual_file = "/n/home00/szu/gtex/expr_residual/expr_residual_Lung.txt"
#    tissuenm = "Lung"
    
#    gene_residual_file = "/n/home00/szu/gtex/expr_residual/expr_residual_Muscle.txt"
#    tissuenm = "Muscle"
    
    gene_residual_file = "/n/home00/szu/gtex/expr_residual/expr_residual_Nerve.txt"
    tissuenm = "Nerve"
    
    outdirspecific = outdir + tissuenm
    logspecific = logs_dir + tissuenm
    splitnum = 50

    write_DECODE_jobs(logspecific,input_dir,gene_residual_file,tissuenm,outdirspecific,splitnum,True)

if __name__ == "__main__":
    main()


    
