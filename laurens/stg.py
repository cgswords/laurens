"""
Laurens main loop. Pretty bare-bones right now.
"""

import os
import sys
import parse
import config
from data.stack import Stack
import ast.ast
from data.closure import Closure

from rpython.rlib.jit import JitDriver, purefunction

def get_location(pc, program, bracket_map):
    return "%s_%s_%s" % (
            program[:pc], program[pc], program[pc+1:]
            )

jitdriver = JitDriver(greens=['pc', 'program', 'bracket_map'], reds=['tape'],
        get_printable_location=get_location)

@purefunction
def get_matching_bracket(bracket_map, pc):
    return bracket_map[pc]

def mainloop(program, bracket_map):
    pc = 0
    tape = Tape()
    
    while pc < len(program):
        jitdriver.jit_merge_point(pc=pc, tape=tape, program=program,
                bracket_map=bracket_map)

        code = program[pc]

        if code == ">":
            tape.advance()

        elif code == "<":
            tape.devance()

        elif code == "+":
            tape.inc()

        elif code == "-":
            tape.dec()
        
        elif code == ".":
            # print
            os.write(1, chr(tape.get()))
        
        elif code == ",":
            # read from stdin
            tape.set(ord(os.read(0, 1)[0]))

        elif code == "[" and tape.get() == 0:
            # Skip forward to the matching ]
            pc = get_matching_bracket(bracket_map, pc)
            
        elif code == "]" and tape.get() != 0:
            # Skip back to the matching [
            pc = get_matching_bracket(bracket_map, pc)

        pc += 1

        ## Case Expression
        # 1. Force the value
        # 2. Dispatch cleverly (Sec. 9.4.3)

def val(env,global_env,k):
  if isinstance(k, list):
    return map(lambda v : val(env, global_env, v), k)
  if k.isLit:
   return Value(k.value, True)
  ## Change these to use dictionaries.
  elif env.contains(k):
    return env.lookup(k)
  else:
    return global_env.lookup(k)

def loop(heap, gobal_env):
  pc = 0
  arg_stack = Stack()
  ret_stack = Stack()
  upd_stack = Stack()

  code = op.Eval(ast.ast.App(ast.ast.Var("main"), []), [])

  if code.op == op.EvalOp:
    if type(code.expr) == ast.ast.App:
      f = val(code.env, global_env, code.expr.rator)
      if (f.isAddr):

        arg_stack.extend(val(code.env, global_env, code.expr.rands))

        code = op.Enter(f.value)

    elif type(code.expr) == ast.ast.Let:
      let       = code.expr
      local_env = code.env.copy()
      for var in let.bindings:
        lam            = code.expr.bindings[var]
        addr           = heap.new_addr()
        clos           = Closure(lam, val(code.env,  global_env,  lam.frees))
        local_env[var] = ast.ast.Value(addr,False)
        heap.set_addr(addr, clos)

      code = op.Eval(code.expr.body,local_env)

    elif type(code.expr) == ast.ast.Letrec:
      letrec    = code.expr
      local_env = code.env.copy()
      for var in letrec.bindings: # Build the addresses for the new bindings
        addr           = heap.new_addr()
        local_env[var] = ast.ast.Value(addr,False)

      for var in letrec.bindings: # Build the closures using the new binding.
        lam  = code.expr.bindings[var]
        addr = local_env[var].value
        clos = Closure(lam, val(local_env,  global_env,  lam.frees))
        heap.set_addr(addr, clos)

      code = op.Eval(code.expr.body,local_env)

    elif type(code.expr) == ast.ast.Case:
      case      = code.expr
      local_env = code.env.copy()
      ret_stack.push(AltCont(case.alts,code.env.copy()))

      code = op.Eval(code.case_expr,code.env.copy())

    elif type(code.expr) == ast.ast.Constr:
      constr = code.expr
      local_env = code.env.copy()

      code = op.ReturnCon(constr.constructor, 
                          dict(zip(constr.rands,
                                   val(local_env, global_env, constr.rands))))

    # TODO: Implement Primitive Operators for Primitive Values.

  elif code.op == op.EnterOp:
    closure = heap.lookup(code.target)
    lf      = closure.lam
    frees   = closure.frees

    if lf.update == True:
       return 0
    elif lf.update == False: # For clarity; no-update
      if len(arg_stack) >= len(lf.args):
        local_env = {}
        for var in lf.args:
          local_env[var] = arg_stack.pop() # Woohoo destructive!
        for (i, var) in enumerate(lf.frees):
          local_env[var] = frees[i] 
      
        code = op.Eval(lf.expr, local_env)
  
  elif code.op == op.ReturnConOp:
    if type(ret_stack.peek(), ast.cont.CaseCont):
      retk              = ret_stack.pop()
      ret_env           = retk.env.copy() # Don't need to, but for safety!
      ret_alts          = retk.alts
      constr            = code.constructor
      vals              = code.rands
      default,body,vars = constr_case_lookup(constr, ret_alts)
      if not default:
        ret_env.update(zip(vars, vals))
      elif not (vars == None): # We're in a default case with a binder :worry:
        bind_var     = vars
        addr         = heap.new_addr()
        ret_env[var] = addr
        new_vars     = map((lambda n: 'x'+str(n)),range(0,len(vals)))
        new_atoms    = map((lambda x: Atom(x,True)),new_vars)
        heap.set_addr(addr, 
                      Closure(ast.ast.Lambda(new_vars, [], False, ast.ast.Constr(constr, new_atoms)), 
                              vals))

      # Default Case without a binder does not need to be handled; since we bind
      # no variables, grab the env, and evaluate the body as normal
      # We should add an error if no match and no default is found, but that
      # could easily be a source tranformation.

      # Finally, set up the body evaluation and kick it off.
      code = op.Eval(body, ret.env)
    
  elif code.op == op.ReturnIntOp:
    # TODO: Implement Literal Cases
    return 0 

def constr_case_lookup(constr,ret_alts):
  for alt in ret_alts.alternates: # Assuming everything is an AlgAlt...
    if alt.constructor == constr:
      return (False, alt.rhs, alt.pat_vars)

  # This signals we need to deal with the default case.
  return (True, ret.alts.defailt.rhs, ret.alts.default.binder) 

def run(fp):
    program_contents = ""
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        program_contents += read
    os.close(fp)
    program, bm = parse(program_contents)
    mainloop(program, bm)
