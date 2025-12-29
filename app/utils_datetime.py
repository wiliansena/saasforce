# app/utils_datetime.py
from datetime import datetime
import pytz

UTC = pytz.utc
TZ_BR = pytz.timezone("America/Sao_Paulo")

def utc_now():
    """Datetime UTC (timezone-aware)"""
    return datetime.now(UTC).replace(microsecond=0)

def utc_to_br(dt):
    """
    Converte datetime UTC para horário do Brasil.
    Aceita datetime naive (assume UTC).
    """
    if not dt:
        return None

    if dt.tzinfo is None:
        dt = UTC.localize(dt)

    return dt.astimezone(TZ_BR)

def br_to_utc(dt):
    """
    Converte datetime Brasil → UTC.
    Aceita naive assumindo Brasil.
    """
    if not dt:
        return None

    if dt.tzinfo is None:
        dt = TZ_BR.localize(dt)

    return dt.astimezone(UTC)
