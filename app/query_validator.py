# app/query_validator.py

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum


class QueryStatus(str, Enum):
    VALID = "valid"
    AMBIGUOUS = "ambiguous"
    OUT_OF_DOMAIN = "out_of_domain"


@dataclass(frozen=True)
class QueryValidation:
    status: QueryStatus
    message: str | None = None


DOMAIN_KEYWORDS = {
    "pedido",
    "compra",
    "producto",
    "envio",
    "entrega",
    "paquete",
    "rastreo",
    "pago",
    "tarjeta",
    "transferencia",
    "paypal",
    "garantia",
    "devolucion",
    "reembolso",
    "dinero",
    "afiliado",
    "afiliados",
    "comision",
}

SPECIFIC_KEYWORDS = {
    "envio",
    "entrega",
    "paquete",
    "rastreo",
    "pago",
    "tarjeta",
    "transferencia",
    "paypal",
    "garantia",
    "devolucion",
    "reembolso",
    "afiliado",
    "afiliados",
    "comision",
}

AMBIGUOUS_PATTERNS = {
    "necesito ayuda",
    "ayudame con mi compra",
    "tengo un problema",
    "tengo un problema con mi compra",
    "tengo un problema con mi pedido",
    "que opciones tengo",
    "quiero recuperar mi dinero",
}


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower().strip())
    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )

    return re.sub(r"[^\w\s]", "", normalized)


def validate_query(question: str) -> QueryValidation:
    normalized = normalize_text(question)
    words = set(normalized.split())

    if not normalized:
        return QueryValidation(
            status=QueryStatus.AMBIGUOUS,
            message="Escribe una pregunta para que pueda ayudarte.",
        )

    if normalized in AMBIGUOUS_PATTERNS:
        return QueryValidation(
            status=QueryStatus.AMBIGUOUS,
            message=(
                "Necesito un poco más de información. "
                "¿Tu consulta está relacionada con envíos, pagos, garantías, "
                "devoluciones, reembolsos o el programa de afiliados?"
            ),
        )

    contains_domain_term = bool(words.intersection(DOMAIN_KEYWORDS))
    contains_specific_term = bool(words.intersection(SPECIFIC_KEYWORDS))

    if contains_domain_term and not contains_specific_term:
        return QueryValidation(
            status=QueryStatus.AMBIGUOUS,
            message=(
                "Entiendo que necesitas ayuda con una compra, pero necesito "
                "saber qué ocurrió. ¿Se trata del envío, el pago, la garantía "
                "o una devolución?"
            ),
        )

    if not contains_domain_term:
        return QueryValidation(
            status=QueryStatus.OUT_OF_DOMAIN,
            message=(
                "Solo puedo ayudarte con consultas de BimBam Buy relacionadas "
                "con envíos, pagos, garantías, devoluciones, reembolsos y el "
                "programa de afiliados."
            ),
        )

    return QueryValidation(status=QueryStatus.VALID)