EvalOp      = 0
EnterOp     = 1
ReturnConOp = 2
ReturnIntOp = 3

class Eval(object):
  def __init__(self,expr,env):
    self.op   = EvalOp
    self.expr = expr
    self.env  = env

class Enter(object):
  def __init__(self,addr):
    self.op     = EnterOp
    self.target = addr
