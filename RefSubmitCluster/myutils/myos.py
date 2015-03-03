# This module is used by:
# homer_pipeline_run.py, ...
import os, sys, subprocess
import glob
import re

# Define constants
#HEP = "/seq/epigenome01/Rusty/Homer/homer/bin/" # Homer executables path 
#PEP = "/seq/software/picard/current/bin/" # Picard executables path
#ITEN = "/xchip/igv/tools/./igvtools" # IGV tools executable fullname
#TSEP='/seq/epiprod/de/software/tuxsim/src/'

# Define functions

def basename_no_ext(fullname):
  ''' returns the basename with no extension 
  i.e.. input: /foo/bar/basename.ext output: basename'''
  return os.path.splitext(os.path.basename(fullname))[0]

def bufcount(fullname):
    ''' count number of lines in a file, slower than wccount 
    No good for v large files, too much mem requirement
    https://gist.github.com/zed/0ac760859e614cd03652
    '''
    f = open(fullname)                  
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization
    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)
    f.close()
    return lines

def wccount(fullname):
    ''' count number of lines in a file using wc -l 
    https://gist.github.com/zed/0ac760859e614cd03652
    '''
    out = subprocess.Popen(['wc', '-l', fullname],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT
                         ).communicate()[0]
    return int(out.partition(b' ')[0])

def exit(self, status=0, message=None):
  if message:
    self._print_message(message, _sys.stderr)
  sys.exit(status)

def check_if_directory_exists_create_it(dir):
  ''' Creates a directory ONLY IF one level up directory of dir 
  already exists - to prevent creating a whole new directory who knows where 
  '''
  if dir[-1] == '/':
    dir = dir[0:-1]
  if os.path.exists(os.path.dirname(dir)):
    if not os.path.exists(dir):
      try:
        os.makedirs(dir)
      except:
        print 'Could not create the dir %s' %(dir)
  else:
    print 'Could not create the dir %s, %s does not exists' %(dir, os.path.dirname(dir))
  return 0

def erase_file_if_exists(fullname):
  try:
    os.remove(fullname)
  except OSError:
    pass
  return 0

def remove_all_files_given_dir(dir):
  ''' remove all the files in a given dir, but  keep the directory '''
  dir_plus_star = os.path.join(dir, '*')
  try:
    files = glob.glob(dir_plus_star)
    for f in files:
      os.remove(f)
  except:
    pass
  return 0

def which_server():
  if os.popen('echo $USER').read().strip() == 'dfernand':
    return 'broad'
  elif os.popen('echo $USER').read().strip() == 'szu':
    p = subprocess.Popen(["bjobs"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
    if re.search(" ERROR ", p) is None:
        return 'legacy'
    else:
        return 'slurm'

def create_bsub_string_rm_logs_dir(logs_dir, job_name, out_log_fn='', err_log_fn='', qname = 'week', mem_usage = 'default'):
    ''' create a bsub/sbatch string command, creates the directory for logs if it doesn't exist, and 
    erase the out_log_fn, and err_log_fn.  Note: it REMOVES all the file in the directory even if they are other logs '''
    if out_log_fn == '':
        out_log_fn = os.path.join(logs_dir, job_name+'.out')
    if err_log_fn == '':
        err_log_fn = os.path.join(logs_dir, job_name+'.err')
    server = which_server()
    if server == 'broad' or server == 'legacy':
        if mem_usage == 'default':
            s = 'bsub -P epigenome -q %s -J %s -o %s -e %s ' %(qname, job_name, out_log_fn, err_log_fn)
        else:
            s = 'bsub -P epigenome -R "rusage[mem=%s]" -q %s -J %s -o %s -e %s ' %(mem_usage, qname, job_name, out_log_fn, err_log_fn)
    elif server == 'slurm':
        if mem_usage == 'default':
          s = 'sbatch -J %s -o %s -e %s -p general --reservation=liu --wrap=' %(job_name, out_log_fn, err_log_fn)
        else:
          s = 'sbatch -J %s -o %s -e %s -p general --reservation=liu --mem=%s --wrap=' %(job_name, out_log_fn, err_log_fn, mem_usage)
    check_if_directory_exists_create_it(logs_dir)
    remove_all_files_given_dir(logs_dir)
    erase_file_if_exists(out_log_fn)
    erase_file_if_exists(err_log_fn)
    return s

def create_bsub_string_no_rm_logs_dir(logs_dir, job_name, out_log_fn='', err_log_fn='', qname = 'week', mem_usage = 'default'):
    ''' create a bsub/sbatch string command, creates the directory for logs if it doesn't exist, and 
    erase the out_log_fn, and err_log_fn.  Note: it does not remove all the files in the directory '''
    if out_log_fn == '':
        out_log_fn = os.path.join(logs_dir, job_name+'.out')
    if err_log_fn == '':
        err_log_fn = os.path.join(logs_dir, job_name+'.err')
    server = which_server()
    if server == 'broad' or server == 'legacy':
      if mem_usage == 'default':
        s = 'bsub -P epigenome -q %s -J %s -o %s -e %s ' %(qname, job_name, out_log_fn, err_log_fn)
      else:
        s = 'bsub -P epigenome -R "rusage[mem=%s]" -q %s -J %s -o %s -e %s ' %(mem_usage, qname, job_name, out_log_fn, err_log_fn)
    elif server == 'odyssey':
      if mem_usage == 'default':
        #s = 'sbatch -J %s -o %s -e %s -p general --reservation=liu --wrap=' %(job_name, out_log_fn, err_log_fn)
        s = 'sbatch -J %s -o %s -e %s -p general --wrap=' %(job_name, out_log_fn, err_log_fn)
      else:
        #s = 'sbatch -J %s -o %s -e %s -p general --reservation=liu --mem=%s --wrap=' %(job_name, out_log_fn, err_log_fn, mem_usage)
        s = 'sbatch -J %s -o %s -e %s -p general --mem=%s --wrap=' %(job_name, out_log_fn, err_log_fn, mem_usage)
    check_if_directory_exists_create_it(logs_dir)
    erase_file_if_exists(out_log_fn)
    erase_file_if_exists(err_log_fn)
    return s

def write_bsub_string_no_rm_logs_dir(logs_dir, job_name, job_script_fn = '', out_log_fn='', err_log_fn='', qname = 'week', mem_usage = '2000', ncores = '1', time = '6-5:10:2'):
    ''' writes a bsub/sbatch submission file, creates the directory for logs if it doesn't exist, and 
    erase the out_log_fn, err_log_fn and job_script_fn.  Note: it does not remove all the files in the directory '''
    if job_script_fn == '':
        job_script_fn = os.path.join(logs_dir, job_name+'.sh')
    if out_log_fn == '':
        out_log_fn = os.path.join(logs_dir, job_name+'.out')
    if err_log_fn == '':
        err_log_fn = os.path.join(logs_dir, job_name+'.err')
    server = which_server()
    check_if_directory_exists_create_it(logs_dir)
    erase_file_if_exists(out_log_fn)
    erase_file_if_exists(err_log_fn)
    if server == 'broad':
      job_f = open(job_script_fn, 'w')
      job_f.write('#!/bin/bash\n')
      job_f.write('#BSUB -J %s\n' %(job_name))
      job_f.write('#BSUB -o %s\n' %(out_log_fn))
      job_f.write('#BSUB -e %s\n' %(err_log_fn))
      job_f.write('#BSUB -q %s\n' %(qname))
      job_f.write('#BSUB -P %s\n' %('epigenome'))
      job_f.write('#BSUB -R \'rusage[mem=%s]\'\n\n' %(mem_usage))
      s = 'bsub < %s' %(job_script_fn)
    elif server == 'slurm':
      job_f = open(job_script_fn, 'w')
      job_f.write('#!/bin/bash\n')
      job_f.write('#SBATCH -J %s    #Job name\n' %(job_name))
      job_f.write('#SBATCH -o %s    #fullname outlog\n' %(out_log_fn))
      job_f.write('#SBATCH -e %s    #fullname errlog\n' %(err_log_fn))
      job_f.write('#SBATCH -n %s    #number of cores\n' %(ncores)) # number of cores
      job_f.write('#SBATCH -t %s    #Runtime in minutes\n' %(time)) # runtime in minutes
      job_f.write('#SBATCH -p %s    #partition to submit to (general or serial_requeue)\n' %(qname)) # partition
      #job_f.write('#SBATCH --reservation=%s\n' %('liu')) # mem per node in MB
      job_f.write('#SBATCH --mem=%s    #Memory per node in MB (see also --mem-per-cpu)\n' %(mem_usage)) # mem per node in MB
      s = 'sbatch %s' %(job_script_fn)
    elif server == 'legacy':
      job_f = open(job_script_fn, 'w')
      job_f.write('#!/bin/bash\n')
      job_f.write('#BSUB -J %s\n' %(job_name))
      job_f.write('#BSUB -o %s\n' %(out_log_fn))
      job_f.write('#BSUB -e %s\n' %(err_log_fn))
      job_f.write('#BSUB -q %s\n' %('normal_serial'))
      job_f.write('#BSUB -P %s\n' %('epigenome'))
      job_f.write('#BSUB -R \'rusage[mem=%s]\'\n\n' %(mem_usage))
      s = 'bsub < %s' %(job_script_fn)
    job_f.close()
    return s

def create_bsub_string_no_remove_matlab(logs_dir, job_name, out_log_fn, err_log_fn, qname = 'week', mem_usage = 'default'):
  if mem_usage == 'default':
    s = 'bsub -P epigenome -R "rusage[matlab=1:duration=1]" -q %s -J %s -o %s -e %s' %(qname, job_name, out_log_fn, err_log_fn)
  else:
    s = 'bsub -P epigenome -R "rusage[matlab=1:duration=1]" -R "rusage[mem=%s]" -q %s -J %s -o %s -e %s' %(mem_usage, qname, job_name, out_log_fn, err_log_fn)
  check_if_directory_exists_create_it(logs_dir)
  erase_file_if_exists(out_log_fn)
  erase_file_if_exists(err_log_fn)
  return s

def create_wstring_from_wlist(wlist):
  by = 'job_id' # or by = 'job_name'
  wstring = '"done('
  for el in wlist:
    if by == 'job_name':
      wstring += '\'%s\') && done(' %(el)
    elif by == 'job_id':
      wstring += '%s) && done(' %(el)
  wstring = wstring[0:-9]+'"'
  return wstring
    
def create_bsub_string_with_dependencies(wstring, logs_dir, job_name, out_log_fn, err_log_fn, qname='week', mem_usage='default'):
  if mem_usage == 'default':
    s = 'bsub -P epigenome -q %s -J %s -o %s -e %s -w %s' %(qname, job_name, out_log_fn, err_log_fn, wstring)
  else:
    s = 'bsub -P epigenome -R rusage[mem=%s] -q %s -J %s -o %s -e %s -w %s' %(mem_usage, qname, job_name, out_log_fn, err_log_fn, wstring)
  check_if_directory_exists_create_it(logs_dir)
  remove_all_files_given_dir(logs_dir)
  erase_file_if_exists(out_log_fn)
  erase_file_if_exists(err_log_fn)
  return s

def create_bsub_string_with_dependencies_matlab(wstring, logs_dir, job_name, out_log_fn, err_log_fn, qname='week', mem_usage='default'):
  if mem_usage == 'default':
    s = 'bsub -P epigenome -R "rusage[matlab=1:duration=1]" -q %s -J %s -o %s -e %s -w %s' %(qname, job_name, out_log_fn, err_log_fn, wstring)
  else:
    s = 'bsub -P epigenome -R "rusage[matlab=1:duration=1]" -R rusage[mem=%s] -q %s -J %s -o %s -e %s -w %s' %(mem_usage, qname, job_name, out_log_fn, err_log_fn, wstring)
  check_if_directory_exists_create_it(logs_dir)
  remove_all_files_given_dir(logs_dir)
  erase_file_if_exists(out_log_fn)
  erase_file_if_exists(err_log_fn)
  return s

def load_dependencies_cmd(dependencies_list):
    server = which_server()
    if server == 'broad':
      dotkit_cmd = ("export DK_ROOT=/broad/software/dotkit;"
                  "source /broad/software/dotkit/ksh/.dk_init;")
      use_cmd = ""
      for dep in dependencies_list:
          use_cmd += 'use %s;' %(dep)
      cmd = dotkit_cmd+use_cmd
    elif server == 'odyssey':
      cmd = ""
      for dep in dependencies_list:
          cmd += 'module load %s;' %(dep)
    return cmd

def write_fullcmd(fullcmd, logs_dir, job_name):
    f = open(os.path.join(logs_dir, job_name+'.fullcmd'), 'w')
    f.write(fullcmd)
    f.close()
    return 0
