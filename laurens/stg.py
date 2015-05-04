"""
Laurens main loop. Pretty bare-bones right now.
"""

import os
import sys
import config
import ast.ast
import ast.cont
import op

from debug         import logMsg, debug
from parse         import parse
from data.closure  import Closure
from data.argstack import ArgStack
from data.retstack import RetStack
from data.updstack import UpdStack
from data.heap     import Heap
from data.config   import Config

from rpython.rlib.jit import JitDriver, purefunction

def get_location(code):
    return "%s" % ( code )

jitdriver = JitDriver(greens=['code']
                     #, reds=['config','arg_stack', 'ret_stack', 'upd_stack', 'heap', 'global_env']
                     , reds='auto'
                     , get_printable_location=get_location)

def terminateHuh(config):
  return (((config.code.op == op.ReturnConOp) or 
           (config.code.op == op.ReturnIntOp)) 
          and (not config.ret_stack.peek()[0]))

def loop(config):

  while not terminateHuh(config):
    jitdriver.jit_merge_point( code       = config.code)
                            #, config     = config
                            #, arg_stack  = config.arg_stack 
                            #, ret_stack  = config.ret_stack 
                            #, upd_stack  = config.upd_stack 
                            #, heap       = config.heap
                            #, global_env = config.global_env)
    debug("-------------")
    debug(str(config))
    config = config.code.step(config)

    #jitdriver.can_enter_jit(code=config.code)
    #                       , config     = config
    #                       , arg_stack  = config.arg_stack 
    #                       , ret_stack  = config.ret_stack 
    #                       , upd_stack  = config.upd_stack 
    #                       , heap       = config.heap
    #                       , global_env = config.global_env)   
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
  debug("------------------------------------------------")
  debug(test_name)
  code   = op.Eval(ast.ast.App(ast.ast.Var("main"), []), {})
  answer = loop(Config(code, ArgStack(), RetStack(), UpdStack(), heap, {"main":ast.ast.Value(main_addr,False)}))
  debug(str(answer))


