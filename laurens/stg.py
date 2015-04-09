"""
Laurens main loop. Pretty bare-bones right now.
"""

import os
import sys
import parse
import config
from data.stack import Stack
import ast.ast

from rpython.rlib.jit import JitDriver, purefunction

def get_location(pc, program, bracket_map):
    return "%s_%s_%s" % (
            program[:pc], program[pc], program[pc+1:]
            )

jitdriver = JitDriver(greens=['pc', 'program', 'bracket_map'], reds=['tape'],
        get_printable_location=get_location)

@purefunction
def get_matching_bracket(bracket_map, pc):
    return bracket_map[pc]

def mainloop(program, bracket_map):
    pc = 0
    tape = Tape()
    
    while pc < len(program):
        jitdriver.jit_merge_point(pc=pc, tape=tape, program=program,
                bracket_map=bracket_map)

        code = program[pc]

        if code == ">":
            tape.advance()

        elif code == "<":
            tape.devance()

        elif code == "+":
            tape.inc()

        elif code == "-":
            tape.dec()
        
        elif code == ".":
            # print
            os.write(1, chr(tape.get()))
        
        elif code == ",":
            # read from stdin
            tape.set(ord(os.read(0, 1)[0]))

        elif code == "[" and tape.get() == 0:
            # Skip forward to the matching ]
            pc = get_matching_bracket(bracket_map, pc)
            
        elif code == "]" and tape.get() != 0:
            # Skip back to the matching [
            pc = get_matching_bracket(bracket_map, pc)

        pc += 1

        ## Case Expression
        # 1. Force the value
        # 2. Dispatch cleverly (Sec. 9.4.3)

def val(env,global_env,k):
  if isinstance(k, list):
    return map(lambda v : value(env, global_env, v), k)
  if k.isLit():
   return Value(k.value, True)
  elif env.contains(k):
    return env.lookup(k)
  else:
    return global_env.lookup(k)

def loop(heap, gobal_env):
  pc = 0
  arg_stack = Stack()
  ret_stack = Stack()
  upd_stack = Stack()

  code = op.Eval(ast.ast.App(ast.ast.Var("main"), []), [])

  if code.op == op.EvalOp:
    if isinstance(code.expr, ast.ast.App):
      f = val(code.env, global_env, code.expr.rator)
      if (f.isAddr):
        code = op.Enter(f.value)
        arg_stack.extend(val(code.env, global_env, code.expr.rands))

  elif code.op == op.EnterOp:
    
  
  elif code.op == op.ReturnConOp:
  
  elif code.op == op.ReturnIntOp:
      


def run(fp):
    program_contents = ""
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        program_contents += read
    os.close(fp)
    program, bm = parse(program_contents)
    mainloop(program, bm)
