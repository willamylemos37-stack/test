from __future__ import annotations
from dataclasses import dataclass
class SecurityContextError(ValueError): pass
@dataclass(frozen=True)
class ActorContext:
    user_id:int
    company_id:int
    email:str
def require_actor(ctx:ActorContext|None)->ActorContext:
    if ctx is None: raise SecurityContextError("Usuário autenticado obrigatório.")
    if ctx.company_id <= 0 or ctx.user_id <= 0: raise SecurityContextError("Contexto de usuário inválido.")
    return ctx
def assert_company(ctx:ActorContext, resource_company_id:int)->None:
    require_actor(ctx)
    if ctx.company_id != resource_company_id:
        raise SecurityContextError("Acesso negado para esta empresa.")
