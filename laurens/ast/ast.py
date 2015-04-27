from collections import deque

class AST(object):
  _attrs_ = []
  def __init__(self):
    raise Exception('Cannot instantiate')

class ValAST(AST):
  _attrs_ = ['value']
  def __init__(self):
    raise Exception('Cannot instantiate')

class Program(object):
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

class App(AST):
  def __init__(self, var, atoms):
    self.rator = var
    self.rands = atoms
 
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

class PrimOp(AST):
  def __init__(self, op, atoms):
    self.oper  = op
    self.atoms = atoms

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

  def __str__(self):
    res  = "Lit> "
    res += " - value: "
    res += str(self.value)
    return res

class Var(AST):
  def __init__(self, name):
    self.variable = name
    self.isVar = True

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
