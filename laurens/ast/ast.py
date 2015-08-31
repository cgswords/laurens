from collections import deque

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

class AST(object):
  _attrs_ = []
  def __init__(self):
    raise Exception('Cannot instantiate')

class ValAST(AST):
  _attrs_ = ['value']
  _immutable_fields_ = ['value']
  def __init__(self):
    raise Exception('Cannot instantiate')

class Program(object):
  _immutable_fields_ = ['binds']
  def __init__(self, binds):
    self.binds = binds

  def binds(self):
    return self.binds

class Bindings(object):
  def __init__(self, variables, lambdas):
    new_dict = {}
    for (i,v) in enumerate(variables):
      new_dict[v] = lambdas[i]

    self.bindings = new_dict

  def getBinding(self, variable):
    return bindings[variable]

class Lambda(AST):
  def __init__(self, varsf, varsa, update, expr):
    self.frees  = varsf
    self.args   = varsa
    self.update = update
    self.expr   = expr

  def __str__(self):
    res  = "\tLambda"
    res += "\n\t - free: "
    res += str(self.frees)
    res += " | updt: "
    res += str(self.update)
    res += "\n\t - args: "
    res += str(self.args)
    res += "\n\t - expr: "
    res += str(self.expr)
    return res

class Let(AST):
  def __init__(self, bindings, expr):
    self.bindings = bindings
    self.body     = expr

class Letrec(AST):    
  def __init__(self, bindings, expr):
    self.bindings = bindings
    self.body     = expr

class Case(AST):
  _attrs_ = ['case_expr', 'alts']
  def __init__(self, expr, alts):
    self.case_expr = expr
    self.alts      = alts

  def eval(self, config):
    ret_stack  = config.ret_stack
    cenv       = config.code.env
    
    debug("=> Case")
    case      = self
    local_env = cenv.copy()
    config.ret_stack.push(ast.cont.CaseCont(case.alts, local_env))

    config.code = op.Eval(case.case_expr, local_env)
    return config

class App(AST):
  def __init__(self, var, atoms):
    self.rator = var
    self.rands = atoms

  def eval(self, config):
    cenv       = config.code.env
    arg_stack  = config.arg_stack
    global_env = config.global_env
    
    debug("=> App")
    lookup   = val(cenv, global_env, self.rator)
    lookupTy = type(lookup)
    logMsg("Lookup", str(lookup))
    if lookupTy is ast.ast.Value:
      if lookup.isAddr:
        logMsg("Rands", str(self.rands))
        lookup_rands = vals(cenv, global_env, self.rands)

        logMsg("Looked up", str(lookup_rands))
        arg_stack.extend(lookup_rands)
        
        config.code = op.Enter(lookup.value)
        debug(str(arg_stack.peek()))
        return config
      
      elif lookup.isInt and self.rands == []:
        config.code = op.ReturnInt(lookup.value)
        return config
      
      else:  
        raise Exception('integer literal in application position', lookup.value)
    
    else:
        raise Exception('operator wasn not a value', self.rator, lookup)

  def __str__(self):
    res  = "App"
    res += "\n - rator: "
    res += str(self.rator)
    res += " | rands: "
    res += str(self.rands)
    return res

class Constr(AST):
  _attrs_ = ['constructor', 'rands']
  def __init__(self, constr, atoms):
    self.constructor = constr
    self.rands       = atoms

  def eval(self, config):
    debug("=> Constr")
    constr = config.code.expr
    local_env = cenv.copy()

    config.code = op.ReturnCon(constr.constructor, 
                               dict(zip(constr.rands,
                                        vals(local_env, global_env, constr.rands))))
    return config

class PrimOp(AST):
  def __init__(self, op, atoms):
    self.oper  = op
    self.atoms = atoms

  def eval(self, config):
    code       = config.code
    arg_stack  = config.arg_stack
    ret_stack  = config.ret_stack
    upd_stack  = config.upd_stack
    global_env = config.global_env
    heap       = config.heap
    cenv       = code.env
    
    debug("=> PrimOp")
    debug(str(self.oper))
    if self.oper == "+": ## From the book: these must already be forced!
      debug("Plus")
      lookups = vals(code.env, global_env, self.atoms)
      x1      = lookups[0]
      x2      = lookups[1]
      assert isinstance(x1,ast.ast.ValAST)
      assert isinstance(x2,ast.ast.ValAST)
      res     = x1.value + x2.value
      debug("result")
      debug(str(res))
      config.code = op.ReturnInt(res) 
      return config

    elif self.oper == "-": ## From the book: these must already be forced!
      debug("Minus")
      lookups = vals(code.env, global_env, self.atoms)
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
      return config

    elif self.oper == "*": ## From the book: these must already be forced!
      lookups     = vals(code.env, global_env, self.atoms)
      x1          = lookups[0]
      x2          = lookups[1]
      assert isinstance(x1,ast.ast.ValAST)
      assert isinstance(x2,ast.ast.ValAST)
      res         = x1.value * x2.value
      config.code = op.ReturnInt(res)
      return config

    elif self.oper == "=": ## From the book: these must already be forced!
      lookups = vals(code.env, global_env, self.atoms)
      x1      = lookups[0]
      x2      = lookups[1]
      assert isinstance(x1,ast.ast.ValAST)
      assert isinstance(x2,ast.ast.ValAST)
      config.code = op.ReturnInt(x1 == x2) 
      return config

    else:
      raise Exception('invalid primop', str(self))

## I must use these instead of lists to preserve the default case
class AlgAlts(AST):
  def __init__(self, alts, default):
    self.alternates = alts
    self.default    = default

class PrimAlts(AST):
  def __init__(self, alts, default):
    self.alternates = alts
    self.default    = default

class AlgAlt(AST):
  def __init__(self, constr, variables, expr):
    self.constructor = constr
    self.pat_vars    = variables
    self.rhs         = expr

class LitAlt(AST):
  def __init__(self, prim, expr):
    self.literal   = prim
    self.rhs       = expr

class DefaultAlt(AST):
  def __init__(self, var, expr):
    self.binder = var
    self.rhs    = expr

# class PrimOp(object):
#   def __init__(self, op):
#     self.primop = op

#
## I'm using Python built-in lists for this so I don't need these.
# class VarList(object):
#   def __init__(self, variables):
#     self.variables = variables
#    
# class AtomList(object):
#   def __init__(self, atoms):
#     self.atoms = atoms

class Atom(ValAST):
  _attrs_ = ['value', 'isVar', 'isLit']

  def __init__(self, value, varHuh):
    self.value = value
    self.isVar = varHuh
    self.isLit = not varHuh

  def eval(self, config):
    if self.isLit:
      config.code = op.ReturnInt(self.value)
    else:
      config.code = op.ReturnInt(val(config.code.cenv, global_env, self).value)
    return config

  def __str__(self):
    res  = "Atom"
    res += "\n - value: "
    res += str(self.value)
    res += " | Lit?: "
    res += str(self.isLit)
    return res

class Lit(ValAST):
  def __init__(self, val):
    self.value  = val
    self.isLit = True

  def eval(self, config):
    config.code = op.ReturnInt(self.value)
    return config

  def __str__(self):
    res  = "Lit> "
    res += " - value: "
    res += str(self.value)
    return res

class Var(AST):
  def __init__(self, name):
    self.variable = name
    self.isVar = True

  def eval(config):
    global_env = config.global_env
    cenv       = config.code.env

    debug("=> Var")
    res = val(cenv, global_env, self)
    assert isinstance(res,ast.ast.ValAST)
    config.code = op.ReturnInt(res.value)

  def __str__(self):
    res  = "Var"
    res += " - variable: "
    res += str(self.variable)
    return res

class Value(ValAST):
  def __init__(self, val, intHuh):
    self.value  = val
    self.isInt  = intHuh
    self.isAddr = not intHuh

  def __str__(self):
    res  = "Value> "
    res += " - value: "
    res += str(self.value)
    res += " | Int?: "
    res += str(self.isInt)
    return res
