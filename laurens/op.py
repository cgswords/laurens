import debug

import config
import ast.ast
import ast.cont
import op

from debug        import logMsg
from parse        import parse
from data.closure import Closure
from data.stack   import Stack
from data.heap    import Heap
from data.config  import Config

from rpython.rlib.jit import purefunction

EvalOp      = 0
EnterOp     = 1
ReturnConOp = 2
ReturnIntOp = 3

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

def lookup_op(op):
  if (op == EvalOp):
    return "Eval"
  elif (op == EnterOp):
    return "Enter"
  elif (op == ReturnConOp):
    return "ReturnCon"
  elif (op == ReturnIntOp):
    return "ReturnInt"
  else:
      return "Unidentified operation."

class Eval(object):
  def __init__(self,expr,env):
    self.op   = EvalOp
    self.expr = expr
    self.env  = env
  
  def __str__(self):
    return "Expr - " + str(self.expr) + "\n  Env - " + str(env)


  def step(self,config):
    code       = config.code
    arg_stack  = config.arg_stack
    ret_stack  = config.ret_stack
    upd_stack  = config.upd_stack
    global_env = config.global_env

    cexp       = code.expr
    cenv       = code.env
    expr_type  = type(cexp)

    if expr_type is ast.ast.App:
      print("=> App")
      lookup   = val(cenv, global_env, cexp.rator)
      lookupTy = type(lookup)
      logMsg("Lookup",lookup)
      if lookupTy is ast.ast.Value:
        if lookup.isAddr:
          logMsg("Rands", cexp.rands)
          lookup_rands = val(cenv, global_env, cexp.rands)

          logMsg("Looked up", cexp.rands)
          arg_stack.extend(lookup_rands)
          
          config.code = op.Enter(lookup.value)
          print(arg_stack.peek())
        
        elif lookup.isInt and cexp.rands == []:
          config.code = op.ReturnInt(lookup.value)
        
        else:  
          raise Exception('integer literal in application position', lookup.value)
      
      else:
          raise Exception('operator wasn not a value', cexp.rator, lookup)

    elif expr_type is ast.ast.Let:
      print("=> Let")
      let       = cexp
      local_env = cenv.copy()
      for var in let.bindings:
        lam            = cexp.bindings[var]
        addr           = heap.new_addr()
        clos           = Closure(lam, val(cenv,  global_env,  lam.frees))
        local_env[var] = ast.ast.Value(addr,False)
        heap.set_addr(addr, clos)

      config.code = op.Eval(code.expr.body,local_env)

    elif expr_type is ast.ast.Letrec:
      print("=> Letrec")
      letrec    = ce
      local_env = code.env.copy()
      for var in letrec.bindings: # Build the addresses for the new bindings
        addr           = heap.new_addr()
        local_env[var] = ast.ast.Value(addr,False)

      for var in letrec.bindings: # Build the closures using the new binding.
        lam  = cexp.bindings[var]
        addr = local_env[var].value
        clos = Closure(lam, val(local_env,  global_env,  lam.frees))
        heap.set_addr(addr, clos)

      config.code = op.Eval(cexp.body,local_env)

    elif expr_type is ast.ast.Case:
      print("=> Case")
      case      = cexp
      local_env = code.env.copy()
      config.ret_stack.push(ast.cont.CaseCont(case.alts,code.env.copy()))

      config.code = op.Eval(code.case_expr,code.env.copy())

    elif expr_type is ast.ast.Constr:
      print("=> Constr")
      constr = cexp
      local_env = cenv.copy()

      config.code = op.ReturnCon(constr.constructor, 
                          dict(zip(constr.rands,
                                   val(local_env, global_env, constr.rands))))

    elif expr_type is ast.ast.Atom:
      print("=> Atom")
      if cexp.isLit:
        config.code = op.ReturnInt(cexp.value)

    elif expr_type is ast.ast.Lit:
      print("=> Lit")
      config.code = op.ReturnInt(cexp.value)

    elif expr_type is ast.ast.PrimOp:
      print("=> PrimOp")
      print(cexp.oper)
      if cexp.oper == "+": ## From the book: these must already be forced!
        print("Plus")
        lookups = val(code.env, global_env, cexp.atoms)
        x1      = lookups[0]
        x2      = lookups[1]
        res     = x1.value + x2.value
        print("result")
        print(res)
        config.code = op.ReturnInt(res) 

      elif cexp.oper == "-": ## From the book: these must already be forced!
        lookups = val(code.env, global_env, cexp.rator)
        x1      = lookups[0]
        x2      = lookups[1]
        config.code = op.ReturnInt(x1 - x2) 

      elif cexp.oper == "*": ## From the book: these must already be forced!
        lookups = val(code.env, global_env, cexp.rator)
        x1      = lookups[0]
        x2      = lookups[1]
        config.code = op.ReturnInt(x1 * x2) 

      elif cexp.oper == "=": ## From the book: these must already be forced!
        lookups = val(code.env, global_env, cexp.rator)
        x1      = lookups[0]
        x2      = lookups[1]
        config.code = op.ReturnInt(x1 == x2) 

    else:
      logMsg("Current operator: ", cexp)

    return config

class Enter(object):
  def __init__(self,addr):
    self.op     = EnterOp
    self.target = addr
  
  def __str__(self):
    return "Enter - " + str(self.target)

  def step(self, config):
    closure = config.heap.lookup(config.code.target)
    lf      = closure.lam
    frees   = closure.frees
    
    logMsg("Entering lambda: ",lf)

    if lf.update == True:
       return 0
    elif lf.update == False: # For clarity; no-update
      if len(config.arg_stack) >= len(lf.args):
        local_env = {}
        for var in lf.args:
          local_env[var] = config.arg_stack.pop() # Woohoo destructive!
        for (i, var) in enumerate(lf.frees):
          local_env[var] = frees[i] 
      
        config.code = op.Eval(lf.expr, local_env)

    return config

class ReturnCon(object):
  def __init__(self,constr,args):
    self.op          = ReturnConOp
    self.constructor = constr
    self.rands       = args
  
  def __str__(self):
    return "Return Constructor - " + str(self.constructor) + str(self.rands)

  def step(self, config):
    if type(config.ret_stack.peek()) is ast.cont.CaseCont:
      retk              = config.ret_stack.pop()
      ret_env           = retk.env.copy() # Don't need to, but for safety!
      ret_alts          = retk.alts
      constr            = code.constructor
      vals              = code.rands
      default,body,vars = self.constr_case_lookup(constr, ret_alts)
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


  def constr_case_lookup(self,constr,ret_alts):
    for alt in ret_alts.alternates: # Assuming everything is an AlgAlt...
      if alt.constructor == constr:
        return (False, alt.rhs, alt.pat_vars)

    # This signals we need to deal with the default case.
    return (True, ret.alts.default.rhs, ret.alts.default.binder) 

class ReturnInt(object):
  def __init__(self,val):
    self.op    = ReturnIntOp
    self.value = val

  def __str__(self):
    return "Return Int - " + str(self.value)

  def step(self,config):
    print("Int return")
    if type(config.ret_stack.peek()) is ast.cont.CaseCont:
      retk     = config.ret_stack.pop()
      ret_env  = retk.env.copy()
      ret_alts = retk.alts
      value    = code.value

      default,body = self.int_case_lookup(constr, ret_alts)

      if default:
        if (default.binder is not None):
          var = default.binder
          ret_env.update([(var,value)])

      code = op.Eval(body, ret_env)

  def int_case_lookup(self,val,ret_alts):
    for alt in ret_alts.alternates: # Assuming everything is a LitAlt
      if alt.literal == val:
        return (False, alt.rhs)

    return (True, ret.alts.default)


