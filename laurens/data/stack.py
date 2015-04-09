from collections import deque

class Stack(object):
  def __init__(self):
    self.dq = deque() 

  def push(self,value):
    return self.dq.append(value)

  def pop(self):
    return self.dq.pop()

  def peek(self):
    return self.dq[0]

  
