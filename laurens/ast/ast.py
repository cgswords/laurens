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

