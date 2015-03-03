#!/usr/bin/env python

# Import modules
import glob, subprocess, sys, os, optparse
script_path = os.path.dirname(__file__)
myutils_path = os.path.join(script_path, '../myutils')
sys.path.append(myutils_path)
import myos
import general
import execs_commands 

def write_gemma_jobs(gemma_options, output_dir, logs_dir, input_dir, genotype_fn, execute):
    qname = "serial_requeue" 
    mem_usage = "1000"
    myos.check_if_directory_exists_create_it(output_dir)
    myos.check_if_directory_exists_create_it(logs_dir)
    batch_number = 1 # counter of batch
    batch_size = 1 # how many runs per batch
    job_number_within_batch = 0 # counter of job within batch
    pheno_files = os.listdir(input_dir)
    for pheno_n in pheno_files:
        pheno_fn = os.path.join(input_dir, pheno_n)
        if job_number_within_batch == 0:
            job_name = os.path.splitext(pheno_n)[0]
            bsubcmd = myos.write_bsub_string_no_rm_logs_dir(logs_dir, job_name, qname = qname, mem_usage = mem_usage, time = '1438')
            if os.path.exists(pheno_fn) is False or os.path.exists(genotype_fn) is False:
                print 'Oooops, One of these files to process does not exist!!! %s %s' %(pheno_fn, genotype_fn)
                return 0
        output_prefix = job_name
        exec_cmd = execs_commands.gemma(output_dir, gemma_options, pheno_fn, genotype_fn, output_prefix) 
        print exec_cmd
        job_script_fn = bsubcmd.split(' ')[-1]
        with open(job_script_fn, "a") as job_script_f:
            print bsubcmd 
            job_script_f.write('echo \"%s\"\n' %(exec_cmd))
            job_script_f.write(exec_cmd+'\n')
            job_number_within_batch += 1
        if job_number_within_batch == batch_size:
            if execute:
                os.system(bsubcmd)
            batch_number += 1
            job_number_within_batch = 0
    if job_number_within_batch > 0 and job_number_within_batch < batch_size:
        if execute:
            os.system(bsubcmd)
    return 0

def main():
    parser = optparse.OptionParser("Input: ")
    parser.add_option('-s', '--gemma_options', action = "store", help = "gemma options, example, --gemma_options='-bslmm 1'")
    parser.add_option('-o', '--out_dir', action = "store", help = "output directory, where to output all the results")
    parser.add_option('-l', '--logs_dir', action = "store", help = "logs directory, where it stores the sh files and the logs files") 
    parser.add_option('-i', '--input_dir', action = "store", help = "directory with all the phenotype data we want to run the code") 
    parser.add_option('-g', '--genotype_fn', action = "store", help = "fullname to genotype file") 
    parser.add_option('-x', '--execute', action = "store_true", default=False)
    (options, args) = parser.parse_args()
    write_gemma_jobs(options.gemma_options, options.out_dir, options.logs_dir, options.input_dir, options.genotype_fn, options.execute) 
    return 0

if __name__ == "__main__":
    main()
