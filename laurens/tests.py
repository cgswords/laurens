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

from stg          import loop

from rpython.rlib.jit import JitDriver, purefunction

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
  answer = loop(Config( code
                      , Stack()
                      , RetStack()
                      , Stack()
                      , heap
                      , {"main":ast.ast.Value(main_addr,False)}))
  print(str(answer))


# __________  Entry point  __________

def entry_point(argv):
  lit3      = ast.ast.Lit(3)
  lit5      = ast.ast.Lit(5)
  plus      = ast.ast.PrimOp("+",[lit3,lit5])
  main      = Closure(ast.ast.Lambda([],[],False,plus),[])
  test(main,Heap(),"Test 1")

  main2     = mtclos([],plus)
  test(main2,Heap(),"Test 2")

  test3heap = Heap()
  idclos    = mtclos(["x"],ast.ast.App(ast.ast.Var("x"),[]))
  idaddr    = test3heap.new_addr()
  test3heap.set_addr(idaddr,idclos)
  test3     = ast.ast.App(ast.ast.Value(idaddr,False),[lit3])
  main3     = mtclos([],test3)
  test(main3,test3heap,"Test 3")

  test4heap = Heap()
  idclos    = mtclos(["x"],ast.ast.PrimOp("+",[ast.ast.Var("x"),lit5]))
  idaddr    = test4heap.new_addr()
  test4heap.set_addr(idaddr,idclos)
  test4     = ast.ast.App(ast.ast.Value(idaddr,False),[lit3])
  main4     = mtclos([],test4)
  test(main4,test4heap,"Test 4")
  
  return 0

# ___ Define and setup target ___

def target(*args):
  return entry_point



