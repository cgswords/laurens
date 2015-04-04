"""
Laurens entry point exporter. Pretty bare-bones right now.
"""

import os
import sys
import stg
import config
import stg

def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print "You must supply a filename"
        return 1
    
    run(os.open(filename, os.O_RDONLY, 0777))
    return 0

def target(*args):
    return entry_point, None
