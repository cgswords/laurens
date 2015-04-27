
debugPrint = False

def logMsg(msg, obj):
  if debugPrint:
    msg += obj
    print(msg)

def debug(msg):
  if debugPrint:
    print(msg)

