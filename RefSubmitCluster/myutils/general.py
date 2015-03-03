# This module contains general useful functions that operate over base python objects such as strings, lists, dictionaries, etc.

import os, sys

def index_in_unique_list(lst, a):
    ''' returns the index of where element a is present in lst 
        Assumption: lst is a list with ONLY unique elements
    '''
    if len(lst)!=len(set(lst)):
        print 'error: list is not unique'
        return 'error'
    else:
        tmp = [i for i, x in enumerate(lst) if x==a]
        res = tmp[0]
    return res
