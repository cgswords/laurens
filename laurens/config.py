"""
Laurens configuration options. Pretty bare-bones right now.
"""

import os
import sys

def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()
