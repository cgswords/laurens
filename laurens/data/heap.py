class Heap(object):
  def __init__(self):
    self.dic = {}

  def new_addr(self):
    return len(self.dic)

  def set_addr(self,addr,value):
    self.dic[addr] = value

  def lookup(self,addr):
    return self.dic[addr]

  def __len__(self):
    return len(self.dic)
