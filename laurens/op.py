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

class ReturnCon(object):
  def __init__(self,constr,args):
    self.op          = ReturnConOp
    self.constructor = constr
    self.rands       = args

class ReturnInt(object):
  def __init__(self,val):
    self.op    = ReturnIntOp
    self.value = val


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
