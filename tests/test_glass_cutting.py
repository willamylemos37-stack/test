import pytest
from app.services.glass_cutting import GlassPiece,GlassSheet,greedy_sheets,optimize_glass,choose_by_cost

def test_single_piece():
    r=greedy_sheets([GlassPiece(900,800)],GlassSheet(3210,2200))
    assert r["sheet_count"]==1

def test_multiple_pieces():
    r=greedy_sheets([GlassPiece(1000,500,2),GlassPiece(800,400,2)],GlassSheet(2000,1000))
    assert r["scrap_area_mm2"]>=0

def test_compare_formats():
    r=optimize_glass([GlassPiece(1200,800,4)],[GlassSheet(2000,1500),GlassSheet(3210,2200)])
    assert len(r)==2

def test_no_price_no_choice():
    r=optimize_glass([GlassPiece(1000,500,2)],[GlassSheet(2000,1000),GlassSheet(3000,1500)])
    assert choose_by_cost(r,None) is None

def test_price_choice():
    r=optimize_glass([GlassPiece(1000,500,4)],[GlassSheet(2000,1000),GlassSheet(3000,1500)])
    assert choose_by_cost(r,{(2000,1000):100,(3000,1500):80})["sheet_width_mm"]==3000

def test_too_large():
    with pytest.raises(ValueError):
        greedy_sheets([GlassPiece(2500,1000)],GlassSheet(2000,1500))
