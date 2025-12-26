# app/utils_licenca.py
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user, logout_user
from app.models import LicencaSistema

def requer_licenca_ativa(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        licenca = LicencaSistema.query.filter_by(
            empresa_id=current_user.empresa_id
        ).first()

        if not licenca or licenca.expirado:
            logout_user()
            flash("Licença expirada. Entre em contato com o suporte.", "danger")
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)
    return decorated
