"""
Laurens main loop. Pretty bare-bones right now.
"""

import os
import sys
import config
import ast.ast
import ast.cont
import op

from parse        import parse
from data.closure import Closure
from data.stack   import Stack
from data.heap    import Heap
from data.config  import Config

from rpython.rlib.jit import JitDriver, purefunction

def get_location(code, arg_stack, ret_stack, upd_stack, heap):
    return "%s_%s_%s" % (
            code, arg_stack, ret_stack
            )

jitdriver = JitDriver(greens=['code', 'arg_stack', 'ret_stack', 'upd_stack', 'heap'], reds=['global_env'],
        get_printable_location=get_location)

@purefunction
def val(env, global_env, k):
  logMsg("Val with ", k)
  if isinstance(k, list):
    if k == []:
      return []
    return [val(env, global_env, v) for v in k] # map(lambda v : val(env, global_env, v), k)
  elif type(k) is ast.ast.Atom:
    if k.isLit:
     return ast.ast.Value(k.value, True)
    elif k.value in env:
      return env[k.value]
    else:
      return global_env[k.value]
  elif type(k) is ast.ast.Lit:
    return ast.ast.Value(k.value, True)
  elif type(k) is ast.ast.Var:
    var = k.variable
    if var in env:
      return env[var]
    elif var in global_env:
      return global_env[var]
  else:
    return k

def logMsg(msg, obj):
  msg += str(obj)
  print(msg)

def loop(init_heap, init_global_env):
  arg_stack = Stack()
  ret_stack = Stack()
  upd_stack = Stack()

  code   = op.Eval(ast.ast.App(ast.ast.Var("main"), []), {})
  config = Config(code, Stack(), Stack(), Stack(), init_heap, init_global_env)

  while not (((code.op == op.ReturnConOp) or (code.op == op.ReturnIntOp)) and (ret_stack.peek() == "Empty")):
    print("-----------")
    logMsg("Loop with oper: ", op.lookup_op(code.op))
    logMsg(">> Return Stack: ", ret_stack.peek())

    if code.op == op.EvalOp:
      print("EvalOp")
      ce = code.expr
      expr_type = type(ce)

      if expr_type is ast.ast.App:
        print("=> App")
        cenv     = code.env
        lookup   = val(cenv, global_env, ce.rator)
        lookupTy = type(lookup)
        logMsg("Lookup",lookup)
        if lookupTy is ast.ast.Value:
          if lookup.isAddr:
            logMsg("Rands", ce.rands)
            lookup_rands = val(cenv, global_env, ce.rands)
            logMsg("Looked up", ce.rands)
            arg_stack.extend(lookup_rands)
            code = op.Enter(lookup.value)
            print(arg_stack.peek())
          elif lookup.isInt and ce.rands == []:
            code = op.ReturnInt(lookup.value)
          else:  
            raise Exception('integer literal in application position', lookup.value)
        else:
            raise Exception('operator wasn not a value', ce.rator, lookup)

      elif expr_type is ast.ast.Let:
        print("=> Let")
        let       = ce
        local_env = code.env.copy()
        for var in let.bindings:
          lam            = ce.bindings[var]
          addr           = heap.new_addr()
          clos           = Closure(lam, val(code.env,  global_env,  lam.frees))
          local_env[var] = ast.ast.Value(addr,False)
          heap.set_addr(addr, clos)

        code = op.Eval(code.expr.body,local_env)

      elif expr_type is ast.ast.Letrec:
        print("=> Letrec")
        letrec    = ce
        local_env = code.env.copy()
        for var in letrec.bindings: # Build the addresses for the new bindings
          addr           = heap.new_addr()
          local_env[var] = ast.ast.Value(addr,False)

        for var in letrec.bindings: # Build the closures using the new binding.
          lam  = ce.bindings[var]
          addr = local_env[var].value
          clos = Closure(lam, val(local_env,  global_env,  lam.frees))
          heap.set_addr(addr, clos)

        code = op.Eval(ce.body,local_env)

      elif expr_type is ast.ast.Case:
        print("=> Case")
        case      = ce
        local_env = code.env.copy()
        ret_stack.push(ast.cont.CaseCont(case.alts,code.env.copy()))

        code = op.Eval(code.case_expr,code.env.copy())

      elif expr_type is ast.ast.Constr:
        print("=> Constr")
        constr = ce
        local_env = code.env.copy()

        code = op.ReturnCon(constr.constructor, 
                            dict(zip(constr.rands,
                                     val(local_env, global_env, constr.rands))))

      elif expr_type is ast.ast.Atom:
        print("=> Atom")
        if ce.isLit:
          code = op.ReturnInt(ce.value)

      elif expr_type is ast.ast.Lit:
        print("=> Lit")
        code = op.ReturnInt(ce.value)

      elif expr_type is ast.ast.PrimOp:
        print("=> PrimOp")
        print(ce.oper)
        if ce.oper == "+": ## From the book: these must already be forced!
          print("Plus")
          lookups = val(code.env, global_env, ce.atoms)
          x1      = lookups[0]
          x2      = lookups[1]
          res     = x1.value + x2.value
          print("result")
          print(res)
          code = op.ReturnInt(res) 

        elif ce.oper == "-": ## From the book: these must already be forced!
          lookups = val(code.env, global_env, ce.rator)
          x1      = lookups[0]
          x2      = lookups[1]
          code = op.ReturnInt(x1 - x2) 

        elif ce.oper == "*": ## From the book: these must already be forced!
          lookups = val(code.env, global_env, ce.rator)
          x1      = lookups[0]
          x2      = lookups[1]
          code = op.ReturnInt(x1 * x2) 

        elif ce.oper == "=": ## From the book: these must already be forced!
          lookups = val(code.env, global_env, ce.rator)
          x1      = lookups[0]
          x2      = lookups[1]
          code = op.ReturnInt(x1 == x2) 

      else:
        logMsg("Current operator: ", ce)

    elif code.op == op.EnterOp:
      closure = heap.lookup(code.target)
      lf      = closure.lam
      frees   = closure.frees
     
      logMsg("Entering lambda: ",lf)

      if lf.update == True:
         return 0
      elif lf.update == False: # For clarity; no-update
        if len(arg_stack) >= len(lf.args):
          local_env = {}
          for var in lf.args:
            local_env[var] = arg_stack.pop() # Woohoo destructive!
          for (i, var) in enumerate(lf.frees):
            local_env[var] = frees[i] 
        
          code = op.Eval(lf.expr, local_env)
    
    elif code.op == op.ReturnConOp:
      if type(ret_stack.peek()) is ast.cont.CaseCont:
        retk              = ret_stack.pop()
        ret_env           = retk.env.copy() # Don't need to, but for safety!
        ret_alts          = retk.alts
        constr            = code.constructor
        vals              = code.rands
        default,body,vars = constr_case_lookup(constr, ret_alts)
        if not default:
          ret_env.update(zip(vars, vals))
        elif (vars is not None): # We're in a default case with a binder :worry:
          var          = vars
          addr         = heap.new_addr()
          ret_env[var] = addr
          new_vars     = ['x' + str(n) for n in range(0, len(vals))]
          new_atoms    = [ast.ast.Atom(x,True) for x in new_vars] # map((lambda x: Atom(x,True)),new_vars)
          heap.set_addr(addr, 
                        Closure(ast.ast.Lambda(new_vars, [], False, ast.ast.Constr(constr, new_atoms)), 
                                vals))

        # Default Case without a binder does not need to be handled; since we bind
        # no variables, grab the env, and evaluate the body as normal
        # We should add an error if no match and no default is found, but that
        # could easily be a source tranformation.

        # Finally, set up the body evaluation and kick it off.
        code = op.Eval(body, ret_env)
      
    elif code.op == op.ReturnIntOp:
      print("Int return")
      if type(ret_stack.peek()) is ast.cont.CaseCont:
        retk     = ret_stack.pop()
        ret_env  = retk.env.copy()
        ret_alts = retk.alts
        value    = code.value

        default,body = constr_case_lookup(constr, ret_alts)

        if default:
          if (default.binder is not None):
            var = default.binder
            ret_env.update([(var,value)])

        code = op.Eval(body, ret_env)
     
  return code

def int_case_lookup(val,ret_alts):
  for alt in ret_alts.alternates: # Assuming everything is a LitAlt
    if alt.literal == val:
      return (False, alt.rhs)

  return (True, ret.alts.default)

def constr_case_lookup(constr,ret_alts):
  for alt in ret_alts.alternates: # Assuming everything is an AlgAlt...
    if alt.constructor == constr:
      return (False, alt.rhs, alt.pat_vars)

  # This signals we need to deal with the default case.
  return (True, ret.alts.default.rhs, ret.alts.default.binder) 

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
  print(loop(heap,{"main":ast.ast.Value(main_addr,False)}))

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



