#!/usr/bin/env python

# Import modules
import glob, subprocess, sys, os, optparse
script_path = os.path.dirname(__file__)
myutils_path = os.path.join(script_path, '../myutils')
sys.path.append(myutils_path)
import myos
import general
import execs_commands 
import numpy as np

def write_InferDPB_jobs(output_dir, logs_dir, input_dir, ncore = '4', threadnum = 4, execute = False):
    qname = "serial_requeue" 
    mem_usage = "1000"
    #threadnum = 4
    myos.check_if_directory_exists_create_it(output_dir)
    myos.check_if_directory_exists_create_it(logs_dir)
    #batch_number = 1 # counter of batch
    #batch_size = 1 # how many runs per batch
    #job_number_within_batch = 0 # counter of job within batch

    fn_array = np.array([0.1,0.2,0.4,0.8,0.9],float)
    fp_array = np.array([0.0001,0.001,0.002,0.01],float)
    tmp = 1
    for fn in fn_array:
        for fp in fp_array:
            tmp = tmp + 1
            for i in range(1,6):
                d2s = os.path.join(input_dir,'Drug_Sub')
                p2d = os.path.join(input_dir,'Protein_Domain')
                d2p = os.path.join(input_dir,'Drug_Protein_'+str(i))
                s2d_in = os.path.join(input_dir,'Sub_Domain_'+str(i))
                outname = 'Sub_Domain_Result_'+str(tmp)+'_'+str(i)
                job_name = 's2d_job'+'_'+str(tmp)+'_'+str(i)
                bsubcmd = myos.write_bsub_string_no_rm_logs_dir(logs_dir,job_name,qname=qname,mem_usage=mem_usage, ncores=ncore, time='1438')
                if os.path.exists(d2s) is False or os.path.exists(p2d) is False or os.path.exists(d2p) is False or os.path.exists(s2d_in) is False:
                    print "Cannot find some input files!"
                    return 0
                exec_cmd = execs_commands.inferDPB_fnfp(output_dir,fn,fp,threadnum,d2s,p2d,d2p,s2d_in,outname)
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
    parser = optparse.OptionParser("Input: ")
    parser.add_option('-o', '--out_dir', action = "store", help = "output directory, where to output all the results")
    parser.add_option('-l', '--logs_dir', action = "store", help = "logs directory, where it stores the sh files and the logs files") 
    parser.add_option('-i', '--input_dir', action = "store", help = "directory with all the phenotype data we want to run the code") 
    parser.add_option('-n', '--ncore', action = "store_true", default='4', help = "fullname to genotype file") 
    parser.add_option('-t', '--thread', action = "store_true", default=4, help = "fullname to genotype file") 
    parser.add_option('-x', '--execute', action = "store_true", default=False)
    (options, args) = parser.parse_args()
    write_InferDPB_jobs(options.out_dir, options.logs_dir, options.input_dir, options.ncore, options.thread, options.execute) 
    return 0

if __name__ == "__main__":
    #output_dir = '/n/home00/szu/InferDPB/CV_fnfp/output'
    #logs_dir = '/n/home00/szu/InferDPB/CV_fnfp/logs'
    #input_dir = '/n/home00/szu/InferDPB/CV_fnfp'
    #write_InferDPB_jobs(output_dir,logs_dir,input_dir)
    main()


    
