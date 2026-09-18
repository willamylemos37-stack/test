from decimal import Decimal
from app.services.cutting import ffd, optimize_profile

def test_ffd_kerf():
    bars=ffd([1500,1500],3000,3)
    assert len(bars)==2

def test_chooses_cheaper_bar_variant():
    r=optimize_profile([1000,1000,1000],Decimal("100"),Decimal("250"),3)
    assert r["bar_length_mm"]==3000

def test_uses_6m_when_3m_is_more_expensive():
    r=optimize_profile([2000,2000,2000],Decimal("300"),Decimal("400"),3)
    assert r["bar_length_mm"]==6000
