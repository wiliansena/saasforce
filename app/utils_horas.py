# app/hora_utils.py

from datetime import datetime
import pytz

def hora_brasilia():
    return datetime.now(pytz.timezone('America/Sao_Paulo')).replace(microsecond=0)
