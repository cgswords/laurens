"""
Laurens main loop. Pretty bare-bones right now.
"""

import os
import sys
import config
import ast.cont
import op

from ast.ast       import *
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
  return Lambda([],args,False,body)

def mtclos(args, body):
  return Closure(Lambda([],args,False,body),[])

def test(main,heap,test_name):
  main_addr  = heap.new_addr()
  heap.set_addr(main_addr,main)
  print("------------------------------------------------")
  print(test_name)
  code   = op.Eval(App(Var("main"), []), {})
  answer = loop(Config( code
                      , Stack()
                      , RetStack()
                      , Stack()
                      , heap
                      , {"main":Value(main_addr,False)}))
  print(str(answer))


# __________  Entry point  __________

def entry_point(argv):
  lit3      = Lit(3)
  lit5      = Lit(5)
  lit6      = Lit(6)
  plus      = PrimOp("+",[lit3,lit5])
  main      = Closure(Lambda([],[],False,plus),[])
  test(main,Heap(),"Test 1")

  main2     = mtclos([],plus)
  test(main2,Heap(),"Test 2")

  test3heap = Heap()
  idclos    = mtclos(["x"],App(Var("x"),[]))
  idaddr    = test3heap.new_addr()
  test3heap.set_addr(idaddr,idclos)
  test3     = App(Value(idaddr,False),[lit3])
  main3     = mtclos([],test3)
  test(main3,test3heap,"Test 3")

  test4heap = Heap()
  idclos    = mtclos(["x"],PrimOp("+",[Var("x"),lit5]))
  idaddr    = test4heap.new_addr()
  test4heap.set_addr(idaddr,idclos)
  test4     = App(Value(idaddr,False),[lit3])
  main4     = mtclos([],test4)
  test(main4,test4heap,"Test 4")
 
  threfivex = PrimAlts([ LitAlt(3, lit3)
                       , LitAlt(5, lit5)] ,
                       DefaultAlt("x", Var("x")))
  main5     = mtclos([],Case(lit5, threfivex))
  test(main5,Heap(),"Test 5")

  main6     = mtclos([],Case(lit6, threfivex))
  test(main6,Heap(),"Test 6")

  monus     = PrimAlts([ LitAlt(0, Lit(0))] ,
                       DefaultAlt("x", PrimOp("-",[Var("x"),Lit(1)])))
  main7     = mtclos([],Case(lit5, monus))
  test(main7,Heap(),"Test 7")

  main8     = mtclos([],Case(Lit(0), monus))
  test(main8,Heap(),"Test 8")

  test9heap = Heap()
  monusbody = PrimAlts([ LitAlt(0, Lit(1))] ,
                       DefaultAlt("n", PrimOp("-",[Var("n"),Lit(1)])))
  monusclos = mtclos(["n"],Case(Var("n"),monusbody))
  monusaddr = test9heap.new_addr()
  test9heap.set_addr(monusaddr,monusclos)
  test9     = App(Value(monusaddr,False),[lit3])
  main9     = mtclos([],test9)
  test(main9,test9heap,"Test 9")

  test10heap = Heap()
  factaddr   = test10heap.new_addr()
  factbody   = PrimAlts(
                 [ LitAlt(0, Lit(1))] ,
                 DefaultAlt(
                  "n", 
                  Case(
                    PrimOp("-",[Var("n"),Lit(1)]),
                    PrimAlts(
                      [],
                      DefaultAlt(
                        "nm", 
                        Case(
                          App(Value(factaddr,False),[Var("nm")]),
                          PrimAlts([],
                                   DefaultAlt("m",PrimOp("*",[Var("n"),Var("m")])))))))))
  factclos   = mtclos(["n"],Case(Var("n"),factbody))
  test10heap.set_addr(factaddr,factclos)
  test10     = App(Value(factaddr,False),[Lit(1)])
  main10     = mtclos([],test10)
  test(main10,test10heap,"Test 10")

  test11     = App(Value(factaddr,False),[Lit(2)])
  main11     = mtclos([],test11)
  test(main11,test10heap,"Test 11")

  test12     = App(Value(factaddr,False),[Lit(5)])
  main12     = mtclos([],test12)
  test(main12,test10heap,"Test 12")

  return 0

# ___ Define and setup target ___

def target(*args):
  return entry_point

entry_point([])
