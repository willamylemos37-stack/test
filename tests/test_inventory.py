from decimal import Decimal
import pytest
from app.services.inventory import InventoryItem, InventoryError, validate_item, compatible_scrap

def test_linear_item_requires_length():
    with pytest.raises(InventoryError): validate_item(InventoryItem("MP-357","BARRA_6000","BARRA",None,Decimal("1")))
def test_negative_quantity_rejected():
    with pytest.raises(InventoryError): validate_item(InventoryItem("MP-357","BARRA_6000","BARRA",6000,Decimal("-1")))
def test_scrap_compatibility():
    xs=[InventoryItem("MP-357","PADRAO","RETALHO",2500,Decimal("1")),
        InventoryItem("MP-358","PADRAO","RETALHO",4000,Decimal("1")),
        InventoryItem("MP-357","PADRAO","RETALHO",1500,Decimal("1"))]
    got=compatible_scrap("MP-357",2000,xs)
    assert len(got)==1 and got[0].length_mm==2500
