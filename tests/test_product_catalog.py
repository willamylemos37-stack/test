from app.services.product_catalog import normalize_product_family, supported_product_families, public_catalog


def test_product_families_cover_future_domains():
    codes = {item.code for item in supported_product_families()}
    assert {"ESQUADRIA", "PORTAO", "GRADE", "BOX", "GUARDA_CORPO", "FECHAMENTO", "CORRIMAO"}.issubset(codes)


def test_product_family_normalization():
    assert normalize_product_family("portão") == "PORTAO"
    assert normalize_product_family("portaO") == "PORTAO"
    assert normalize_product_family("guarda-corpo") == "GUARDA_CORPO"


def test_future_product_families_are_empty_catalog_sections():
    by_code = {item["code"]: item for item in public_catalog()}
    assert by_code["PORTAO"]["status"] == "EM_BREVE"
    assert by_code["GRADE"]["status"] == "EM_BREVE"
    assert by_code["BOX"]["status"] == "EM_BREVE"


def test_public_catalog_does_not_expose_internal_rules_or_prices():
    assert all(set(item) == {"code", "name", "status"} for item in public_catalog())
