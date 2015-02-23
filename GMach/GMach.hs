module GMach where

data Const = I Int | B Bool

type Var = String

data Func = (Var, [Var], Expr)

data Prog = [Func] Expr

data Expr = V Var
          | C Const 
          | App Expr Expr 
          | Let    [(Var, Expr)] Expr
          | Letrec [(Var, Expr)] Expr
         
data Code = Nop         

functionComp :: Func -> Code

