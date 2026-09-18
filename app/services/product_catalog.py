from dataclasses import dataclass
import unicodedata

@dataclass(frozen=True)
class ProductFamily:
    code: str
    name: str
    description: str
    status: str = "ATIVO"

PRODUCT_FAMILIES = (
    ProductFamily("ESQUADRIA", "Esquadrias", "Janelas, portas e demais sistemas de esquadrias."),
    ProductFamily("PORTAO", "Portões", "Portões residenciais, comerciais e industriais.", "EM_BREVE"),
    ProductFamily("GRADE", "Grades", "Grades de proteção, fechamento e segurança.", "EM_BREVE"),
    ProductFamily("BOX", "Boxes", "Boxes para banheiro e divisórias de vidro.", "EM_BREVE"),
    ProductFamily("GUARDA_CORPO", "Guarda-corpos", "Guarda-corpos e proteções em vidro e/ou metal.", "EM_BREVE"),
    ProductFamily("FECHAMENTO", "Fechamentos", "Fechamentos e painéis para vãos e ambientes.", "EM_BREVE"),
    ProductFamily("CORRIMAO", "Corrimãos", "Corrimãos e componentes associados.", "EM_BREVE"),
    ProductFamily("OUTROS", "Outros", "Produtos customizados que não pertencem às famílias anteriores.", "EM_BREVE"),
)

_FAMILY_BY_CODE = {item.code: item for item in PRODUCT_FAMILIES}

def normalize_product_family(code: str) -> str:
    raw = (code or "").strip().upper()
    normalized = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode().replace("-", "_").replace(" ", "_")
    if normalized not in _FAMILY_BY_CODE:
        raise ValueError(f"Tipo de produto não suportado: {code}.")
    return normalized

def supported_product_families() -> tuple[ProductFamily, ...]:
    return PRODUCT_FAMILIES


def public_catalog() -> tuple[dict, ...]:
    """Catálogo seguro para uma futura vitrine pública; não expõe regras/custos internos."""
    return tuple({"code": x.code, "name": x.name, "status": x.status} for x in PRODUCT_FAMILIES)
