class HeapObject(object):
    def __init__(self,code,frees):
      self.data = [code] ++ frees

    def code(self):
      return self.data[0]

    def getfree(self, index):
      return frees[index]
  
    
