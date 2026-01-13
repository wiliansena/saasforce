from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import EmpresaPagamentoConfig
from app.forms import EmpresaPagamentoConfigForm
from app.utils_licenca import requer_licenca_ativa
from app.utils import requer_permissao
from app.utils_datetime import utc_now

from flask import Blueprint

bp_pagamento = Blueprint("pagamento", __name__)


@bp_pagamento.route("/configuracoes/pagamento", methods=["GET", "POST"])
@login_required
@requer_licenca_ativa
@requer_permissao("administrativo", "editar")
def configurar_pagamento():

    empresa_id = current_user.empresa_id

    config = (
        EmpresaPagamentoConfig.query
        .filter_by(empresa_id=empresa_id)
        .first()
    )

    form = EmpresaPagamentoConfigForm(obj=config)

    if form.validate_on_submit():

        if not config:
            config = EmpresaPagamentoConfig(
                empresa_id=empresa_id,
                criado_em=utc_now()
            )
            db.session.add(config)

        config.gateway = form.gateway.data
        config.access_token = form.access_token.data
        config.public_key = form.public_key.data
        config.ativo = form.ativo.data

        db.session.commit()

        flash("Configuração de pagamento salva com sucesso!", "success")
        return redirect(url_for("pagamento.configurar_pagamento"))

    return render_template(
        "configuracoes/pagamento.html",
        form=form
    )

