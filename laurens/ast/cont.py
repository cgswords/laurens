class Cont():
  def __init__(self):
    raise NotImplementedError('Should never instantiate this class')

class EmptyCont(Cont):
  def __init__(self):
    pass

class CaseCont(Cont):
  def __init__(self, alts, env):
    self.alts = alts
    self.env  = env
