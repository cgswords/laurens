"""
Laurens parser. Pretty bare-bones right now.
"""

import os
import sys
import data.heap

# prog     => <binds>
# binds    => <var> = <lf> [;<var> = <lf>]*
# lf       => <vars> <flag> <vars> -> <expr>
# flag     => u | n
# expr     => let       <binds> in <expr>
#           | letrec    <binds> in <expr>
#           | case      <expr>  of <alts>
#           | <var>     <atoms>
#           | <constr>  <atoms>
#           | <prim>    <atoms>
#           | <literal>
# alts     => [<aalt>;]* <default>
#           | [<palt>;]* <default>
# aalt     => <constr> <vars> -> <expr>
# palt     => <literal> -> <expr>
# default  => <var> -> <expr>
#           | default -> <expr>
# vars     => {} | {<var>  [,<var>]*}
# atoms    => {} | {<atom> [,<atom>]*}
# atom     := <var> | <literal>
# literal  := 0# | 1# | 2# | ...
# prim     := +# | -# | *# | ...

from rply import ParserGenerator, LexerGenerator
from rply.token import BaseBox

def parse(program):
  heap = data.heap.Heap()
  global_env = {}
  return None, heap, global_env

## def parse(program):
##     parsed = []
##     bracket_map = {}
##     leftstack = []
## 
##     pc = 0
##     for char in program:
##         if char in ('[', ']', '<', '>', '+', '-', ',', '.'):
##             parsed.append(char)
## 
##             if char == '[':
##                 leftstack.append(pc)
##             elif char == ']':
##                 left = leftstack.pop()
##                 right = pc
##                 bracket_map[left] = right
##                 bracket_map[right] = left
##             pc += 1
##     
##     return "".join(parsed), bracket_map
    

