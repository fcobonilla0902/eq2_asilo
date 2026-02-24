"""Funciones auxiliares compartidas por todos los módulos."""
from datetime import date


def fecha_hoy() -> str:
    """Retorna la fecha de hoy en formato ISO: 'YYYY-MM-DD'."""
    return date.today().isoformat()


def validar_curp(curp: str) -> bool:
    """Validación básica de formato CURP (18 caracteres alfanuméricos)."""
    return isinstance(curp, str) and len(curp) == 18 and curp.isalnum()
