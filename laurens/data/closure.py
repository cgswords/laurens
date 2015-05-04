class Closure(object):
  def __init__(self,lambdaform,args):
    self.lam        = lambdaform
    self.free_args  = args

