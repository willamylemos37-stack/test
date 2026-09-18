import pytest
from app.security_context import *
def test_actor_required():
    with pytest.raises(SecurityContextError): require_actor(None)
def test_company_isolation():
    c=ActorContext(1,10,"a@empresa")
    assert require_actor(c)==c
    assert_company(c,10)
    with pytest.raises(SecurityContextError): assert_company(c,11)
