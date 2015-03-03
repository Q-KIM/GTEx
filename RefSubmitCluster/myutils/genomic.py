# This module contain functions useful for operations with genomic files (bam, etc.)

import os, sys, subprocess
import pysam
import random
import re

def list_of_random_integers_no_repetition(x, N):
    ''' returns a list of x random integers from N total integers with no repetition '''
    answer = set()
    sampleSize = x
    answerSize = 0
    while answerSize < sampleSize:
        r = random.randint(0, N)
        if r not in answer:
            answerSize += 1
            answer.add(r)
    return answer 

def genome_Nbases(genome_length_fn, assembly):
    ''' file should be chr<i>\tnumber of bases '''
    Nbases = 0
    if assembly == 'hg19':
        chrom_set = set(['chr%s' %(i) for i in range(1,23)]+['chrX','chrY'])
    elif assembly == 'mm9' or assembly == 'mm10':
        chrom_set = set(['chr%s' %(i) for i in range(1,20)]+['chrX','chrY'])
    with open(genome_length_fn, 'r') as f:
        for line in f:
            cols = line.strip().split('\t')
            if cols[0] in chrom_set:
                Nbases += int(cols[1])
    return Nbases

def genome_sizes_dict(genome_length_fn, assembly):
    ''' file should be chr<i>\tnumber of bases '''
    if assembly == 'hg19':
        tmp1 = {'chr'+str(i):0 for i in range(1,23)}
        tmp2 = {'chrX':0, 'chrY':0}
        chrom_sizes_dict = dict(tmp1.items() + tmp2.items())
    elif assembly == 'mm9' or assembly == 'mm10':
        tmp1 = {'chr'+str(i):0 for i in range(1,20)}
        tmp2 = {'chrX':0, 'chrY':0}
        chrom_sizes_dict = dict(tmp1.items() + tmp2.items())
    with open(genome_length_fn, 'r') as f:
        for line in f:
            cols = line.strip().split('\t')
            if cols[0] in chrom_sizes_dict:
                chrom_sizes_dict[cols[0]] = int(cols[1])
    return chrom_sizes_dict


def check_if_chr(bam_in_fn):
  ''' this functions checks if a BAM header uses chr reference (true), or no chr reference (false) '''
  s = "samtools view -H %s | grep -o 'SN:c'" %(bam_in_fn)
  a = subprocess.Popen(s,stdout=subprocess.PIPE,shell=True)
  output = a.stdout.read()
  if len(output) == 0:
    return False
  else:
    return True

def create_chromosome_string(chrom_sizes_fn):
  fh = open(chrom_sizes_fn, 'r')
  chrom_list = []
  for line in fh:
    chromosome = line.strip().split('\t')[0]
    a = re.search('(\.|_)',chromosome)
    if a:
      continue
    else:
      chrom_list.append(chromosome)
  return ' '.join(chrom_list)

def create_chrom_sizes_dict(chrom_sizes_fn):
    ''' it assumes the chrom sizes fn has chr<k>\tsize format 
    and returns a dictionary with key chr<k> and value int(size) '''
    chrom_sizes_dict = {}
    f_in = open(chrom_sizes_fn, 'r')
    for line in f_in:
        cols = line.strip().split('\t')
        chrom = cols[0]
        size = int(cols[1])
        chrom_sizes_dict[chrom] = size
    f_in.close()
    return chrom_sizes_dict

def get_number_of_reads_bam_file(bam_fn):
    ''' count the number of reads in a bam file (fullname) using pysam 
        Note: the bam file needs to be sorted and indexed for this command to 
        work.
    '''
    try:
        n_reads = reduce(lambda x, y: x + y, [ eval('+'.join(l.rstrip('\n').split('\t')[2:]) ) for l in pysam.idxstats(bam_fn) ])
    except:
        n_reads = -1
    return float(n_reads)

def weighted_sample(items, n):
    ''' weighted sampling with replacement 
    http://stackoverflow.com/questions/2140787/select-random-k-elements-from-a-list-whose-elements-have-weights/2149533#2149533
    Note: it returns a generator object http://stackoverflow.com/questions/102535/what-can-you-use-python-generator-functions-for
    To cath the generator object as a list do a = list(weighted_sample(items, n))
    '''
    total = float(sum(w for w, v in items))
    i = 0
    w, v = items[0]
    while n:
        x = total * (1 - random.random() ** (1.0 / n))
        total -= x
        while x > w:
            x -= w
            i += 1
            w, v = items[i]
        w -= x
        yield v
        n -= 1

#################################################################################
############# ALL THIS IS FOR WEIGTHED SAMPLING WITHOUT REPLACEMENT #############
# http://stackoverflow.com/questions/2140787/select-random-k-elements-from-a-list-whose-elements-have-weights/2149533#2149533
# R function sample(x, size, replace = FALSE, prob = NULL)
#################################################################################
class Node:
    # Each node in the heap has a weight, value, and total weight.
    # The total weight, self.tw, is self.w plus the weight of any children.
    __slots__ = ['w', 'v', 'tw']
    def __init__(self, w, v, tw):
        self.w, self.v, self.tw = w, v, tw

def rws_heap(items):
    # h is the heap. It's like a binary tree that lives in an array.
    # It has a Node for each pair in `items`. h[1] is the root. Each
    # other Node h[i] has a parent at h[i>>1]. Each node has up to 2
    # children, h[i<<1] and h[(i<<1)+1].  To get this nice simple
    # arithmetic, we have to leave h[0] vacant.
    h = [None]                          # leave h[0] vacant
    for w, v in items:
        h.append(Node(w, v, w))
    for i in range(len(h) - 1, 1, -1):  # total up the tws
        h[i>>1].tw += h[i].tw           # add h[i]'s total to its parent
    return h

def rws_heap_pop(h):
    gas = h[1].tw * random.random()     # start with a random amount of gas

    i = 1                     # start driving at the root
    while gas > h[i].w:       # while we have enough gas to get past node i:
        gas -= h[i].w         #   drive past node i
        i <<= 1               #   move to first child
        if gas > h[i].tw:     #   if we have enough gas:
            gas -= h[i].tw    #     drive past first child and descendants
            i += 1            #     move to second child
    w = h[i].w                # out of gas! h[i] is the selected node.
    v = h[i].v

    h[i].w = 0                # make sure this node isn't chosen again
    while i:                  # fix up total weights
        h[i].tw -= w
        i >>= 1
    return v

def random_weighted_sample_no_replacement(items, n):
    heap = rws_heap(items)              # just make a heap...
    for i in range(n):
        yield rws_heap_pop(heap)        # and pop n items off it.
