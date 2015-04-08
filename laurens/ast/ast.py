from collections import deque

class Program(object):
  def __init__(self,binds):
    self.binds = binds

  def binds(self):
    return self.binds

class Bindings(object):
  def __init__(self,variables,lambdas):
    self.bindings = dict(zip(variables,lambdas))

  def getBinding(self,variable):
    return bindings[variable]

class Lambda(object):
  def __init__(self,varsf,varsa,update,expr):
    self.frees  = varsf
    self.args   = varsa
    self.update = update
    self.expr   = expr

class Let(object):
  def __init__(self,bindings,expr):
    self.bindings = bindings
    self.body     = expr

class Letrec(object):    
  def __init__(self,bindings,expr):
    self.bindings = bindings
    self.body     = expr

class Case(object):
  def __init__(self,expr,alts):
    self.case_expr = expr
    self.alts      = alts

class App(object):
  def __init__(self,var,atoms):
    self.rator = var
    self.rands = atoms

class Constr(object):
  def __init__(self,constr,atoms):
    self.constructor = constr
    self.rands       = atoms

class PrimOp(object):
  def __init__(self,op,atoms):
    self.oper  = op
    self.atoms = atoms

class Lit(object):
  def __init__(self,val):
    self.value = val


class AlgAlts(object):
  def __init__(self,alts,default):
    self.alternates = alts
    self.default    = default

class PrimAlts(object):
  def __init__(self,alts,default):
    self.alternates = alts
    self.default    = default

class AlgAlt(object):
  def __init__(self,constr,variables,expr):
    self.constructor = constr
    self.pat_vars    = variables
    slef.rhs         = expr

class LitAlt(object):
  def __init__(self,prim,expr):
    self.literal   = prim
    self.rhs         = expr

class DefaultAlt(object):
  def __init__(self,var,expr):
    self.binder = var
    self.rhs    = expr

class PrimOp(object):
  def __init__(self,op):
    self.primop = op

    
