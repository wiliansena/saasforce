from app import db
from app.models import LogAcao
from flask import current_app
from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user
from flask import request
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def formatar_moeda(valor):
    try:
        return locale.currency(valor, grouping=True, symbol=False)
    except Exception:
        return "0,00"

def formatar_numero(valor):
    try:
        numero = int(round(valor))
        return f"{numero:,}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0"

from datetime import date, datetime
from app.utils_datetime import utc_to_br

def formatar_data(valor):
    """
    Formata date, datetime ou string ISO (YYYY-MM-DD) para data BR (dd/mm/yyyy)
    """
    if not valor:
        return ""

    try:
        # datetime
        if isinstance(valor, datetime):
            valor = utc_to_br(valor)
            return valor.strftime("%d/%m/%Y")

        # date
        if isinstance(valor, date):
            return valor.strftime("%d/%m/%Y")

        # string YYYY-MM-DD
        if isinstance(valor, str):
            try:
                valor = datetime.strptime(valor, "%Y-%m-%d").date()
                return valor.strftime("%d/%m/%Y")
            except ValueError:
                return valor  # se não for data, devolve como veio

        return str(valor)

    except Exception:
        return ""


def formatar_data_hora(valor):
    """
    Formata datetime UTC para data/hora BR
    """
    if not valor:
        return ""

    try:
        valor = utc_to_br(valor)
        return valor.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return ""


def registrar_filtros_jinja(app):
    app.jinja_env.filters['br_moeda'] = formatar_moeda
    app.jinja_env.filters['br_numero'] = formatar_numero
    app.jinja_env.filters['br_data'] = formatar_data
    app.jinja_env.filters['br_data_hora'] = formatar_data_hora



def requer_permissao(categoria, acao):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Faça login para acessar esta página.", "warning")
                return redirect(url_for('auth.login', next=request.url))  # use request.url

            if not current_user.tem_permissao(categoria, acao):
                flash("Você não tem permissão!.", "danger")
                return redirect(request.referrer or url_for('routes.home'))

            return f(*args, **kwargs)
        return wrapped
    return decorator

def somente_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Faça login para acessar esta página.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        
        if current_user.nome.lower() != "admin":
            flash("Acesso restrito ao administrador do sistema.", "danger")
            return redirect(url_for('routes.home'))
        
        return f(*args, **kwargs)
    return decorated_function

def registrar_log(acao):
    """
    Registra uma ação no log com o usuário autenticado.
    """
    if current_user.is_authenticated:
        novo_log = LogAcao(
            usuario_id=current_user.id,
            usuario_nome=current_user.nome,
            acao=acao
        )
        db.session.add(novo_log)
        db.session.commit()

def allowed_file(filename):
    """ Verifica se o arquivo possui uma extensão permitida. """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

UF_PARA_REGIAO = {
    # Norte
    "AC":"NORTE","AP":"NORTE","AM":"NORTE","PA":"NORTE","RO":"NORTE","RR":"NORTE","TO":"NORTE",
    # Nordeste
    "AL":"NORDESTE","BA":"NORDESTE","CE":"NORDESTE","MA":"NORDESTE","PB":"NORDESTE",
    "PE":"NORDESTE","PI":"NORDESTE","RN":"NORDESTE","SE":"NORDESTE",
    # Centro-Oeste
    "DF":"CENTRO-OESTE","GO":"CENTRO-OESTE","MT":"CENTRO-OESTE","MS":"CENTRO-OESTE",
    # Sudeste
    "ES":"SUDESTE","MG":"SUDESTE","RJ":"SUDESTE","SP":"SUDESTE",
    # Sul
    "PR":"SUL","RS":"SUL","SC":"SUL",
}

def uf_para_regiao(uf: str) -> str:
    if not uf: return None
    return UF_PARA_REGIAO.get(uf.strip().upper(), None)



