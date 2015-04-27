class Config(object):
  def __init__(self,code,args,ret,upd,heap,genv):
    self.code       = code
    self.arg_stack  = args
    self.ret_stack  = ret
    self.upd_stack  = upd
    self.heap       = heap
    self.global_env = genv

  def __str__(self):
    res  = ""
    res += "Code: "
    res += str(self.code)
    res += "\nArg Stack: "
    res += str(self.arg_stack)
    res += "\nReturn Stack: "
    res += str(self.ret_stack)
    res += "\nUpdate Stack: "
    res += str(self.upd_stack)
    res += "\nHeap: "
    res += str(self.heap)
    return res
