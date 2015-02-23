module CC where

type Var = String

data Val  = VLam Var Expr
          | I Int

data Ctxt = Empty 
          | AppFst Ctxt Expr 
          | AppSnd Val  Ctxt
          | PlusL  Ctxt Expr
          | PlusR  Expr Ctxt 

data Expr = Done
          | Plus Expr Expr
          | Var Var
          | Val Val
          | Lam Var Expr
          | App Expr Expr
          | PCtxt Ctxt

compose :: Ctxt -> Expr -> Ctxt
compose = undefined

type Config = (Expr, Ctxt)

fill :: Ctxt -> Ctxt -> Ctxt
fill Empty          c = c
fill (AppFst c' e)  c = AppFst (fill c' c) e
fill (AppSnd v  c') c = AppSnd v (fill c' c) 
fill (PlusL c' e)   c = PlusL  (fill c' c) e
fill (PlusR v c')   c = PlusR  v (fill c' c)

transition :: Config -> Config
transition (PCtxt c, ctxt) = fill ctxt $ PCtxt c
transition (Lam v m, ctxt) = fill ctxt $ Lam v m
transition (App m n, ctxt) = (m, fill ctxt $ AppFst Empty n)
