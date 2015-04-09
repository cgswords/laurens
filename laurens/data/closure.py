class Closure(object):
  def __init__(self,lambdaform,frees):
    self.lam   = lambdaform
    self.frees = frees

