"""
Laurens main loop. Pretty bare-bones right now.
"""

import os
import sys
import config
import ast.ast
import ast.cont
import op

from debug         import logMsg
from parse         import parse
from data.closure  import Closure
from data.stack    import Stack
from data.retstack import RetStack
from data.heap     import Heap
from data.config   import Config

from rpython.rlib.jit import JitDriver, purefunction

def get_location(code, arg_stack, ret_stack, upd_stack, heap):
    return "%s_%s_%s" % (
            code, arg_stack, ret_stack
            )

jitdriver = JitDriver(greens=['config'], reds=['global_env'],
        get_printable_location=get_location)

def terminateHuh(config):
  return (((config.code.op == op.ReturnConOp) or 
           (config.code.op == op.ReturnIntOp)) 
          and (not config.ret_stack.peek()[0]))

def loop(config):

  while not terminateHuh(config):
    print("-------------")
    print(str(config))
    config = config.code.step(config)

  return config

def run(fp):
    program_contents = ""
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        program_contents += read
    os.close(fp)
    heap, global_env = parse(program_contents)
    loop(heap, global_env)


def lam(args,body):
  return ast.ast.Lambda([],args,False,body)

def mtclos(args, body):
  return Closure(ast.ast.Lambda([],args,False,body),[])

def test(main,heap,test_name):
  main_addr  = heap.new_addr()
  heap.set_addr(main_addr,main)
  print("------------------------------------------------")
  print(test_name)
  code   = op.Eval(ast.ast.App(ast.ast.Var("main"), []), {})
  answer = loop(Config(code, Stack(), Stack(), Stack(), heap, {"main":ast.ast.Value(main_addr,False)}))
  print(str(answer))


