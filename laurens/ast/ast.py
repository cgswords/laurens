from collections import deque

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

class Lambda(object):
  def __init__(self, varsf, varsa, update, expr):
    self.frees  = varsf
    self.args   = varsa
    self.update = update
    self.expr   = expr

class Let(object):
  def __init__(self, bindings, expr):
    self.bindings = bindings
    self.body     = expr

class Letrec(object):    
  def __init__(self, bindings, expr):
    self.bindings = bindings
    self.body     = expr

class Case(object):
  def __init__(self, expr, alts):
    self.case_expr = expr
    self.alts      = alts

class App(object):
  def __init__(self, var, atoms):
    self.rator = var
    self.rands = atoms

class Constr(object):
  def __init__(self, constr, atoms):
    self.constructor = constr
    self.rands       = atoms

class PrimOp(object):
  def __init__(self, op, atoms):
    self.oper  = op
    self.atoms = atoms

class AlgAlts(object):
  def __init__(self, alts, default):
    self.alternates = alts
    self.default    = default

class PrimAlts(object):
  def __init__(self, alts, default):
    self.alternates = alts
    self.default    = default

class AlgAlt(object):
  def __init__(self, constr, variables, expr):
    self.constructor = constr
    self.pat_vars    = variables
    slef.rhs         = expr

class LitAlt(object):
  def __init__(self, prim, expr):
    self.literal   = prim
    self.rhs       = expr

class DefaultAlt(object):
  def __init__(self, var, expr):
    self.binder = var
    self.rhs    = expr

class PrimOp(object):
  def __init__(self, op):
    self.primop = op

## I'm using Python built-in lists for this so I don't need these.
# class VarList(object):
#   def __init__(self, variables):
#     self.variables = variables
#    
# class AtomList(object):
#   def __init__(self, atoms):
#     self.atoms = atoms

class Atom(object):
  def __init__(self, value, varHuh):
    self.value = value
    slef.isVar = varHuh
    self.isLit = not varHuh

class Lit(object):
  def __init__(self, val):
    self.value  = val
    self.isLit = True

class Var(object):
  def __init__(self, name):
    self.variable = name
    self.isVar = True

class Value(object):
  def __init__(self, val, intHuh):
    self.value  = val
    self.isInt  = intHuh
    self.isAddr = not intHuh
