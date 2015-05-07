import debug

import config
import ast.ast
import ast.cont
import op

from data.closure  import Closure
from data.config   import Config
from data.heap     import Heap
from data.argstack import ArgStack
from data.retstack import RetStack
from data.updstack import UpdStack
from data.updframe import UpdateFrame
from debug         import logMsg, debug
from parse         import parse

from rpython.rlib.jit import purefunction

EvalOp      = 0
EnterOp     = 1
ReturnConOp = 2
ReturnIntOp = 3

@purefunction
def vals(env, global_env, k):
  logMsg("Vals with ", str(k))
  if k == []:
    return []
  return [val(env, global_env, v) for v in k] # map(lambda v : val(env, global_env, v), k)

@purefunction
def val(env, global_env, k):
  logMsg("Val with ", str(k))
  res = k
  if type(k) is ast.ast.Lit:
    res = ast.ast.Value(k.value, True)
  elif type(k) is ast.ast.Var:
    var = k.variable
    if var in env:
      res = env[var]
    elif var in global_env:
      res = global_env[var]
  elif type(k) is ast.ast.Atom:
    litHuh = k.isLit
    if litHuh:
      res = ast.ast.Value(k.value, True)
    elif k.value in env:
      res = env[k.value]
    else:
      res = global_env[k.value]

  assert isinstance(res,ast.ast.ValAST)
  return res 

@purefunction
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

class Op(object):
  def __init__(self):
    raise Exception('Cannot instantiate')

class Eval(Op):
  def __init__(self,expr,env):
    self.op   = EvalOp
    self.expr = expr
    self.env  = env
  
  def __str__(self):
    return "\n\tExpr - " + str(self.expr) + "\n\tEnv - " + str(self.env)

  @jit.unroll_safe
  def step(self,config):
    code       = config.code
    arg_stack  = config.arg_stack
    ret_stack  = config.ret_stack
    upd_stack  = config.upd_stack
    global_env = config.global_env
    heap       = config.heap

    cexp       = code.expr
    cenv       = code.env
    expr_type  = type(cexp)

    if expr_type is ast.ast.App:
      debug("=> App")
      lookup   = val(cenv, global_env, cexp.rator)
      lookupTy = type(lookup)
      logMsg("Lookup", str(lookup))
      if lookupTy is ast.ast.Value:
        if lookup.isAddr:
          logMsg("Rands", str(cexp.rands))
          lookup_rands = vals(cenv, global_env, cexp.rands)

          logMsg("Looked up", str(lookup_rands))
          arg_stack.extend(lookup_rands)
          
          config.code = op.Enter(lookup.value)
          debug(str(arg_stack.peek()))
        
        elif lookup.isInt and cexp.rands == []:
          config.code = op.ReturnInt(lookup.value)
        
        else:  
          raise Exception('integer literal in application position', lookup.value)
      
      else:
          raise Exception('operator wasn not a value', cexp.rator, lookup)

    # elif expr_type is ast.ast.Let:
    #   debug("=> Let")
    #   let       = cexp
    #   local_env = cenv.copy()
    #   for var in let.bindings:
    #     lam            = cexp.bindings[var]
    #     addr           = heap.new_addr()
    #     clos           = Closure(lam, vals(cenv,  global_env,  lam.frees))
    #     local_env[var] = ast.ast.Value(addr,False)
    #     heap.set_addr(addr, clos)

    #   config.code = op.Eval(code.expr.body,local_env)

    # elif expr_type is ast.ast.Letrec:
    #   debug("=> Letrec")
    #   letrec    = cexp
    #   local_env = code.env.copy()
    #   for var in letrec.bindings: # Build the addresses for the new bindings
    #     addr           = heap.new_addr()
    #     local_env[var] = ast.ast.Value(addr,False)

    #   for var in letrec.bindings: # Build the closures using the new binding.
    #     lam  = cexp.bindings[var]
    #     addr = local_env[var].value
    #     clos = Closure(lam, vals(local_env,  global_env,  lam.frees))
    #     heap.set_addr(addr, clos)

    #   config.code = op.Eval(cexp.body,local_env)

    elif expr_type is ast.ast.Case:
      debug("=> Case")
      case      = cexp
      local_env = cenv.copy()
      config.ret_stack.push(ast.cont.CaseCont(case.alts, local_env))

      config.code = op.Eval(case.case_expr, local_env)

    elif expr_type is ast.ast.Constr:
      debug("=> Constr")
      constr = cexp
      local_env = cenv.copy()

      config.code = op.ReturnCon(constr.constructor, 
                          dict(zip(constr.rands,
                                   vals(local_env, global_env, constr.rands))))

    elif expr_type is ast.ast.Atom:
      debug("=> Atom")
      if cexp.isLit:
        config.code = op.ReturnInt(cexp.value)
      else:
        config.code = op.ReturnInt(val(cenv, global_env, cexp).value)

    elif expr_type is ast.ast.Lit:
      debug("=> Lit")
      config.code = op.ReturnInt(cexp.value)

    elif expr_type is ast.ast.Var:
      debug("=> Var")
      res = val(cenv, global_env, cexp)
      assert isinstance(res,ast.ast.ValAST)
      config.code = op.ReturnInt(res.value)

    elif expr_type is ast.ast.PrimOp:
      debug("=> PrimOp")
      debug(str(cexp.oper))
      if cexp.oper == "+": ## From the book: these must already be forced!
        debug("Plus")
        lookups = vals(code.env, global_env, cexp.atoms)
        x1      = lookups[0]
        x2      = lookups[1]
        assert isinstance(x1,ast.ast.ValAST)
        assert isinstance(x2,ast.ast.ValAST)
        res     = x1.value + x2.value
        debug("result")
        debug(str(res))
        config.code = op.ReturnInt(res) 

      elif cexp.oper == "-": ## From the book: these must already be forced!
        debug("Minus")
        lookups = vals(code.env, global_env, cexp.atoms)
        x1      = lookups[0]
        x2      = lookups[1]
        assert isinstance(x1,ast.ast.ValAST)
        assert isinstance(x2,ast.ast.ValAST)
        logMsg("x1: ",str(x1))
        logMsg("x2: ",str(x2))
        res     = x1.value - x2.value
        debug("result")
        debug(str(res))
        config.code = op.ReturnInt(res) 

      elif cexp.oper == "*": ## From the book: these must already be forced!
        lookups     = vals(code.env, global_env, cexp.atoms)
        x1          = lookups[0]
        x2          = lookups[1]
        assert isinstance(x1,ast.ast.ValAST)
        assert isinstance(x2,ast.ast.ValAST)
        res         = x1.value * x2.value
        config.code = op.ReturnInt(res)

      elif cexp.oper == "=": ## From the book: these must already be forced!
        lookups = vals(code.env, global_env, cexp.atoms)
        x1      = lookups[0]
        x2      = lookups[1]
        assert isinstance(x1,ast.ast.ValAST)
        assert isinstance(x2,ast.ast.ValAST)
        config.code = op.ReturnInt(x1 == x2) 

    else:
      logMsg("Current operator: ", str(cexp))

    return config

class Enter(Op):
  def __init__(self,addr):
    self.op     = EnterOp
    self.target = addr
  
  def __str__(self):
    return "Enter - " + str(self.target)

  @jit.unroll_safe
  def step(self, config):
    closure   = config.heap.lookup(config.code.target)
    lf        = closure.lam
    free_args = closure.free_args
    
    logMsg("Entering lambda: ", str(lf))

    if lf.update == True:
                                                  # Shouldn't need to copy here
       config.upd_stack.push(UpdateFrame(config.arg_stack,
                                         config.ret_stack,
                                         config.code.target))
       config.arg_stack = ArgStack()
       config.ret_stack = RetStack()

       # We only update thunks, so we only need to deal with the frees
       local_env = {}
       for i in range(len(lf.frees)): 
         local_env[lf.frees[i]] = free_args[i] 
      
       config.code = op.Eval(lf.expr, local_env)

       return 0
    elif lf.update == False: # For clarity; no-update
      if (len(config.arg_stack) < len(lf.args)) and config.ret_stack.empty():
        # PARTIAL APPLICATION
        # The paper does something funny here; note that the update address
        # off of the update stack is (probably) not the address we are currently
        # looking at; the closure _to be updated_ has as its value this
        # partially-applied closure. We never change the code because we are
        # going to retry application with our new arguments in just a second.
        # Moreover, the paper proposes an optimization step based on the
        # problem of generating these partially-applied specializations, since
        # they are trying to compile. We aren't tied to such a constraint since
        # we are in a JIT, and so this is (17), not (17a)

        if config.upd_stack.empty():
           raise Exception("Empty update frame when we need one.")
        saturated_args   = lf.args[:len(config.arg_stack)]
        unsat_args       = lf.args[len(config.arg_stack):]

        frame            = config.upd_stack.pop()
        config.arg_stack = config.arg_stack.combine(frame.arg_stack)
        config.ret_stack = frame.ret_stack

        new_frees        = lf.frees.copy()
        new_frees.extend(saturated_args)
        new_free_args    = free_args.copy()
        new_free_args.extend(frame.arg_stack)
        upd_clos         = Closure(ast.ast.Lambda(new_frees, unsat_args, False, lf.expr.copy()),
                                   new_free_args)
        config.heap.set_addr(frame.upd_addr,upd_clos)
      elif (len(config.arg_stack) < len(lf.args)):
        raise Exception("I have a return stack and not enough arguments for this application")
      else:
        local_env = {}
        for var in lf.args:
          local_env[var] = config.arg_stack.pop() # Pull off as many as I need, destructively
        for i in range(len(lf.frees)): 
          local_env[lf.frees[i]] = free_args[i] 
      
        config.code = op.Eval(lf.expr, local_env)

    return config

class ReturnCon(Op):
  def __init__(self,constr,args):
    self.op          = ReturnConOp
    self.constructor = constr
    self.rands       = args
  
  def __str__(self):
    return "Return Constructor - " + str(self.constructor) + str(self.rands)

  @jit.unroll_safe
  def step(self, config):
    if config.ret_stack.empty():
        if config.upd_stack.empty():
          raise Exception("Empty update frame when we need one.")
        frame = config.upd_stack.pop()
        config.arg_stack = frame.arg_stack
        config.ret_stack = frame.ret_stack
        constr           = self.constructor
        vals             = self.rands
        new_vars         = ['x' + str(n) for n in range(0, len(vals))]
        upd_clos         = Closure(ast.ast.Lambda(new_vars,[],False,
                                                              ast.ast.Constr(constr,new_vars)),
                                   vals.copy()) # I probably don't need to copy here.
        config.heap.set_addr(frame.upd_addr,upd_clos)

    else: 
      retk = config.ret_stack.pop()
      code = config.code
      if type(retk) is ast.cont.CaseCont:
        ret_env           = retk.env.copy() # Don't need to, but for safety!
        ret_alts          = retk.alts
        constr            = self.constructor
        vals              = self.rands
        default,body,vars = self.constr_case_lookup(constr, ret_alts)
        if not default:
          ret_env.update(zip(vars, vals))
        elif (vars is not None): # We're in a default case with a binder :worry:
          var          = vars
          addr         = config.heap.new_addr()
          ret_env[var] = addr
          new_vars     = ['x' + str(n) for n in range(0, len(vals))]
          new_atoms    = [ast.ast.Atom(x,True) for x in new_vars] # map((lambda x: Atom(x,True)),new_vars)
          config.heap.set_addr(addr, 
                               Closure(ast.ast.Lambda(new_vars, [], False, ast.ast.Constr(constr, new_atoms)), 
                                       vals))

        # Default Case without a binder does not need to be handled; since we bind
        # no variables, grab the env, and evaluate the body as normal
        # We should add an error if no match and no default is found, but that
        # could easily be a source tranformation.

        # Finally, set up the body evaluation and kick it off.
        code = op.Eval(body, ret_env)

    return config

  def constr_case_lookup(self,constr,ret_alts):
    for alt in ret_alts.alternates: # Assuming everything is an AlgAlt...
      if alt.constructor == constr:
        return (False, alt.rhs, alt.pat_vars)

    # This signals we need to deal with the default case.
    return (True, ret.alts.default.rhs, ret.alts.default.binder) 

class ReturnInt(Op):
  def __init__(self,val):
    self.op    = ReturnIntOp
    self.value = val

  def __str__(self):
    return "Return Int - " + str(self.value)

  @jit.unroll_safe
  def step(self,config):
    debug("Int return")

    if config.ret_stack.empty():
      raise Exception('I cannot deal with an integer literal without a return stack.')
    else: 
      retk      = config.ret_stack.pop()
      if type(retk) is ast.cont.CaseCont:
        ret_env   = retk.env.copy()
        ret_alts  = retk.alts
        value     = self.value
        # Just use the class!
        # value     = config.code.value

        default,default_var,body = self.int_case_lookup(value, ret_alts)

        if default:
          if (default_var is not None):
            var = default_var
            ret_env[var] = ast.ast.Value(value, True)
            # logMsg("New env: ", str(ret_env))

        config.code = op.Eval(body, ret_env)
  
    return config

  def int_case_lookup(self,val,ret_alts):
    for alt in ret_alts.alternates: # Assuming everything is a LitAlt
      if alt.literal == val:
        return (False, None, alt.rhs)

    return (True, ret_alts.default.binder, ret_alts.default.rhs)

