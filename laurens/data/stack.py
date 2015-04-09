from collections import deque

class Stack(object):
  def __init__(self):
    self.dq   = deque()

  def push(self,value):
    return self.dq.append(value)

  def extend(self,values):
    values = values.reverse()
    for v in values:
      self.push(v)

  def pop(self):
    return self.dq.pop()

  def peek(self):
    return self.dq[0]

  def __len__(self):
    return len(self.dq)
