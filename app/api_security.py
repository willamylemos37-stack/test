from __future__ import annotations
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.security_entities import User
from app.security import SecurityError, decode_token
from app.security_context import ActorContext

def current_actor(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> ActorContext:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Token de autenticação obrigatório.")
    token=authorization[7:].strip()
    try:
        payload=decode_token(token)
        user_id=int(payload["sub"]); company_id=int(payload["company_id"])
    except (SecurityError, ValueError, KeyError, TypeError):
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")
    user=db.query(User).filter(User.id==user_id, User.company_id==company_id).first()
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="Usuário inativo ou inexistente.")
    return ActorContext(user.id,user.company_id,user.email)
