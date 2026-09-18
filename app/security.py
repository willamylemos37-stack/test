from __future__ import annotations
import base64, hashlib, hmac, json, os, secrets, time
PBKDF2_ITERATIONS=310_000
TOKEN_TTL_SECONDS=3600
class SecurityError(ValueError): pass
def hash_password(password:str)->str:
    if not isinstance(password,str) or len(password)<8: raise SecurityError("Senha deve possuir pelo menos 8 caracteres.")
    salt=secrets.token_bytes(16)
    dk=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(dk).decode()}"
def verify_password(password:str,encoded:str)->bool:
    try:
        scheme,it,s,h=encoded.split("$",3)
        if scheme!="pbkdf2_sha256": return False
        salt=base64.urlsafe_b64decode(s.encode()); expected=base64.urlsafe_b64decode(h.encode())
        return hmac.compare_digest(hashlib.pbkdf2_hmac("sha256",password.encode(),salt,int(it)),expected)
    except Exception: return False
def _b64(b:bytes)->str: return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
def _secret()->bytes:
    v=os.getenv("APP_SECRET_KEY")
    if not v: raise SecurityError("APP_SECRET_KEY não configurada.")
    return v.encode()
def create_token(subject:str,company_id:str,role:str,ttl:int=TOKEN_TTL_SECONDS)->str:
    now=int(time.time()); payload={"sub":subject,"company_id":company_id,"role":role,"iat":now,"exp":now+ttl}
    body=_b64(json.dumps(payload,separators=(",",":"),sort_keys=True).encode())
    return body+"."+_b64(hmac.new(_secret(),body.encode(),hashlib.sha256).digest())
def decode_token(token:str)->dict:
    try:
        body,sig=token.split(".",1)
        expected=_b64(hmac.new(_secret(),body.encode(),hashlib.sha256).digest())
        if not hmac.compare_digest(sig,expected): raise SecurityError("Token inválido.")
        payload=json.loads(base64.urlsafe_b64decode((body+"===").encode()))
        if int(payload["exp"])<int(time.time()): raise SecurityError("Token expirado.")
        return payload
    except SecurityError: raise
    except Exception as exc: raise SecurityError("Token inválido.") from exc
