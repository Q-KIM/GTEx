# This module contains functions that output a cmd string for calling executables, should be broad/odyssey compatible

import os, sys, subprocess
script_path = os.path.dirname(__file__)
sys.path.append(script_path)
import myos

def start_java_cmd(mem_usage, additional_option):
    return 'java -Xmx%sm %s -jar' %(mem_usage, additional_option)

def fastx_trimmer(options, input_fn, output_fn):
    ''' writes command for running fastx_trimmer 
    options should be a string -Q 33 -f 16'''
    en = 'fastx_trimmer'
    cmd = '%s %s -i %s -o %s;' %(en, options, input_fn, output_fn)
    return cmd

def casava_quality_filter(input_fn, output_fn):
    ''' writes command for running fastx_trimmer 
    options should be a string -Q 33'''
    en = 'perl /seq/epiprod/de/Cerebellum/code/casava_filter.pl'
    cmd = '%s -i %s -o %s;' %(en, input_fn, output_fn)
    return cmd

def fastx_adaptor_filter(adaptor_seq, options, input_fn, output_fn):
    ''' writes command for running fastx_clipper
    options should be a string -Q 33'''
    en = 'fastx_clipper'
    cmd = '%s -a %s %s -i %s -o %s;' %(en, adaptor_seq, options, input_fn, output_fn)
    return cmd

def fastq_quality_filter(options, input_fn, output_fn):
    ''' writes command for running fastx_trimmer 
    options should be a string -Q 33'''
    en = 'fastq_quality_filter'
    cmd = '%s %s -i %s -o %s;' %(en, options, input_fn, output_fn)
    return cmd

def fastx_artifacts_filter(options, input_fn, output_fn):
    ''' writes command for running fastx_trimmer 
    options should be a string -Q 33'''
    en = 'fastx_artifacts_filter'
    cmd = '%s %s -i %s -o %s;' %(en, options, input_fn, output_fn)
    return cmd

def fastqc(input_fns, output_dir):
    ''' writes command for running fastx_trimmer 
    options should be a string -Q 33'''
    server = myos.which_server()
    if server == 'broad':
      en = 'perl /broad/software/free/Linux/redhat_5_x86_64/pkgs/fastqc_0.10.1/FastQC/fastqc'
    elif server == 'slurm' or server == 'legacy':
      en = 'perl /n/dulacfs2/Users/dfernand/de/software/FastQC/fastqc'
    cmd = '%s -o %s %s' %(en, output_dir, input_fns)
    return cmd

def fastq_dump(in_fn, out_dir, options):
    ''' writes command for running fastq-dump
    options should be a string --split-3 for paired-end data'''
    server = myos.which_server()
    if server == 'broad':
      en = 'fastq-dump'
      cmd = '%s %s --outdir %s %s' %(en, options, out_dir, in_fn)
    elif server == 'slurm' or server == 'legacy':
      en = 'fastq-dump'
      cmd = 'module load bio/sratoolkit.2.3.3-4; %s %s --outdir %s %s' %(en, options, out_dir, in_fn)
    return cmd

def trim_galore_filter(options, input_fn, output_dir, adapter_seq = None):
    ''' writes command for running fastx_trimmer 
    options should be a string -Q 33'''
    server = myos.which_server()
    if server == 'broad':
      en = '/home/unix/dfernand/bin/trim_galore/trim_galore'
      if adapter_seq is not None:
        cmd = '%s -o %s -a %s %s %s' %(en, output_dir, adapter_seq, options, input_fn)
      else:
        cmd = '%s -o %s %s %s' %(en, output_dir, options, input_fn)
    elif server == 'slurm':
      en = '/n/dulacfs2/Users/dfernand/de/software/trim_galore_v0.3.3/trim_galore'
      if adapter_seq is not None:
        cmd = 'module load centos6/python-2.7.3; module load centos6/cutadapt-1.2.1_python-2.7.3;%s -o %s -a %s %s %s' %(en, output_dir, adapter_seq, options, input_fn)
      else:
        cmd = 'module load centos6/cutadapt-1.2.1_python-2.7.3;%s -o %s %s %s' %(en, output_dir, options, input_fn)
    elif server == 'legacy':
      en = '/n/dulacfs2/Users/dfernand/de/software/trim_galore_v0.3.3/trim_galore'
      if adapter_seq is not None:
        cmd = 'module load hpc/python-2.7.3; module load bio/cutadapt-1.2.1;%s -o %s -a %s %s %s' %(en, output_dir, adapter_seq, options, input_fn)
      else:
        cmd = 'module load hpc/python-2.7.3; module load bio/cutadapt-1.2.1;%s -o %s %s %s' %(en, output_dir, options, input_fn)
    return cmd

def shapeit2(options):
    ''' options must contains all arguments for shapeit2 after the executable fullname'''
    server = myos.which_server()
    if server == 'slurm' or server == 'legacy':
      en = '/n/junliufs1/software/shapeit2/shapeit.v2.r727.linux.x64'
      cmd = '%s %s' %(en, options)
    return cmd

def bowtie_1_run(options, index_fn, input_fn, output_fn):
    ''' writes command for running bowtie mapper 
        NOTE: output_fn always needs to be a basefullname with .sorted, it will add the .bam
    '''
    en = "/home/unix/dfernand/bin/bowtie-1.0.0/bowtie"
    cmd = "%s %s %s %s | samtools view -bS - | samtools sort -n - %s" %(en, options, index_fn, input_fn, output_fn)
    return cmd

def phasedBam2bed(bam_in_fn, bed_p_fn, bed_m_fn):
    ''' command for nimrod executable phasedBam2bed 
    '''
    en = "/seq/epiprod/de/scripts/nimrod/samtoolsUtils/phasedBam2bed"
    cmd = "%s -b %s -p %s -m %s" %(en, bam_in_fn, bed_p_fn, bed_m_fn)
    return cmd

def gemma(output_dir, options, phenotype_fullname, genotype_fullname, output_prefix):
    ''' command for executing gemma 
    '''
    en = "/n/home00/szu/KR_eQTL/mousedata_140405/gemma"
    cmd = "cd %s;%s %s -p %s -g %s -o %s -w 100000 -s 2100000" %(output_dir, en, options, phenotype_fullname, genotype_fullname, output_prefix)
    return cmd

def gemma_ulmm(output_dir, options, phenotype_fullname, genotype_fullname, output_prefix):
    ''' command for executing univariate linear mixed model from BSLMM 
    '''
    en = "/n/home00/szu/KR_eQTL/mousedata_140405/ulmm/gemma"
    cmd = "cd %s;%s -p %s -g %s -gk -o  ;%s %s -p %s -g %s -o %s -w 100000 -s 2100000" %(output_dir, en, options, phenotype_fullname, genotype_fullname, output_prefix)
    return cmd
def gemma_predict(output_dir, options, phenotype_fullname, genotype_fullname, output_prefix, parameter, mean):
    ''' command for executing gemma 
    '''
    en = "/n/home00/szu/KR_eQTL/mousedata_140405/gemma"
    cmd = "cd %s;%s %s -p %s -g %s -o %s -predict -epm %s -emu %s" %(output_dir, en, options, phenotype_fullname, genotype_fullname, output_prefix, parameter, mean)
    return cmd

def inferDPB_fnfp(output_dir,fn,fp,thread,d2s,p2d,d2p,s2d_in,outname):
    ''' generate the commands for fn and fp compare.
    '''
    InferDPBcommand = "/n/home00/szu/InferDPB/Code/bin/InferDPB"
    cmd = "cd %s;%s -f %f -p %f -t %d -s %s -d %s -i %s -n %s -o %s" %(output_dir,InferDPBcommand,fn,fp,thread,d2s,p2d,d2p,s2d_in,outname)
    return cmd

class bedops:
    def __init__(self):
        self.server = myos.which_server()
        if self.server == 'broad':
           self.dep_cmd = myos.load_dependencies_cmd(['.bedops-2.0.0b'])
        elif self.server == 'slurm' or self.server == 'legacy':
            self.dep_cmd = myos.load_dependencies_cmd(['centos6/bedops-2.3.0'])
    def sortbed(self, bed_in_fn, bed_out_fn, options=''):
        if options == '':
            en = 'sort-bed %s > %s' %(bed_in_fn, bed_out_fn)
        else:
            en = 'sort-bed %s %s > %s' %(options, bed_in_fn, bed_out_fn)
        return self.dep_cmd+en
    def vcf2bed(self, vcf_in_fn, vcf_out_fn):
        en = 'vcf2bed < %s > %s' %(vcf_in_fn, vcf_out_fn)
        return self.dep_cmd+en
    def bedmap(self, bedmap_options, reference_in_fn, map_fn, out_fn):
        en = 'bedmap %s %s %s > %s' %(bedmap_options, reference_in_fn, map_fn, out_fn)
        return self.dep_cmd+en
            
class igvtools:
    def __init__(self):
        self.server = myos.which_server()
        if self.server == 'broad':
           self.igv_fn = '/home/unix/dfernand/bin/IGVTools/igvtools.jar'
        elif self.server == 'slurm' or self.server == 'legacy':
            self.dep_cmd = myos.load_dependencies_cmd(['bio/igvtools-2.2.2'])
            self.igv_fn = '/n/sw/igvtools-2.2.2/igvtools.jar'
    def index(self, in_fn):
        java_cmd = start_java_cmd('3000', '-Djava.awt.headless=true')
        en = '%s %s index %s' %(java_cmd, self.igv_fn, in_fn)
        if self.server == 'slurm' or self.server == 'legacy':
            return self.dep_cmd+en
        elif self.server == 'broad':
            return en
    def sort(self, in_fn, sort_fn):
        java_cmd = start_java_cmd('3000', '-Djava.awt.headless=true')
        en = '%s %s sort %s %s' %(java_cmd, self.igv_fn, in_fn, sort_fn)
        if self.server == 'slurm' or self.server == 'legacy':
            return self.dep_cmd+en
        elif self.server == 'broad':
            return en
