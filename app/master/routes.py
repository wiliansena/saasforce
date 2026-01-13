from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from datetime import date

from app.master import bp
from app.utils_master import requer_master
from app.master.forms import NovaEmpresaForm
from app import db
from app.models import Empresa, Usuario, LicencaSistema, Permissao



@bp.route("/empresas")
@login_required
@requer_master
def listar_empresas():

    empresas = Empresa.query.order_by(Empresa.nome).all()

    for e in empresas:
        e.licenca = LicencaSistema.query.filter_by(
            empresa_id=e.id
        ).first()

    return render_template(
        "master/empresas_listar.html",
        empresas=empresas
    )


@bp.route("/empresas/nova", methods=["GET", "POST"])
@login_required
@requer_master
def nova_empresa():

    form = NovaEmpresaForm()

    if form.validate_on_submit():

        # 🔒 evita duplicidade de empresa
        existe = Empresa.query.filter_by(nome=form.nome.data).first()
        if existe:
            flash("Já existe uma empresa com esse nome.", "danger")
            return render_template("master/empresa_nova.html", form=form)

        # 🔒 evita email duplicado (GLOBAL)
        ## EMAIL DA EMPRESA
        email_emp = form.email.data.lower()
        email_in = Usuario.query.filter_by(email_emp=email_emp).first()
        if email_in:
            flash("Já existe uma empresa com esse e-mail.", "danger")
            return render_template("master/empresa_nova.html", form=form)
        
        # EMAIL DO USUARIO ADMIN
        email_admin = form.admin_email.data.lower()
        email_existe = Usuario.query.filter_by(email=email_admin).first()
        if email_existe:
            flash("Já existe um usuário com esse e-mail.", "danger")
            return render_template("master/empresa_nova.html", form=form)

        try:
            # =====================================================
            # 1️⃣ EMPRESA
            # =====================================================
            empresa = Empresa(
                nome=form.nome.data,
                email=form.email.data,
                ativa=True
            )
            db.session.add(empresa)
            db.session.flush()  # garante empresa.id

            # =====================================================
            # 2️⃣ ADMIN DA EMPRESA
            # =====================================================
            admin = Usuario(
                nome=form.admin_nome.data,
                email=email_admin,
                empresa_id=empresa.id,
                is_master=False,
                is_admin_empresa=True
            )
            admin.set_password(form.admin_senha.data)

            db.session.add(admin)
            db.session.flush()  # garante admin.id

            # =====================================================
            # 3️⃣ PERMISSÕES PADRÃO DO ADMIN
            # =====================================================
            permissoes_admin = {
                "venda": ["criar", "ver", "editar", "excluir"],
                "administrativo": ["criar", "ver", "editar", "excluir"],
                "usuarios": ["criar", "ver", "editar", "excluir"],
                "trocar_senha": ["editar"],
            }

            for categoria, acoes in permissoes_admin.items():
                for acao in acoes:
                    db.session.add(
                        Permissao(
                            empresa_id=empresa.id,
                            usuario_id=admin.id,
                            categoria=categoria,
                            acao=acao
                        )
                    )

            # =====================================================
            # 4️⃣ LICENÇA
            # =====================================================
            licenca = LicencaSistema(
                empresa_id=empresa.id,
                data_inicio=date.today(),
                dias_acesso=form.dias_licenca.data or 30
            )
            db.session.add(licenca)

            db.session.commit()

            flash("Empresa criada com sucesso!", "success")
            return redirect(url_for("master.listar_empresas"))

        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao criar empresa: {str(e)}", "danger")

    return render_template("master/empresa_nova.html", form=form)

@bp.route("/empresas/<int:empresa_id>")
@login_required
@requer_master
def detalhe_empresa(empresa_id):

    empresa = Empresa.query.get_or_404(empresa_id)

    usuarios = Usuario.query.filter_by(
        empresa_id=empresa.id
    ).order_by(Usuario.nome).all()

    usuario_padrao = Usuario.query.filter_by(
        empresa_id=empresa.id
    ).order_by(Usuario.id.asc()).first()


    licenca = LicencaSistema.query.filter_by(
        empresa_id=empresa.id
    ).first()

    return render_template(
        "master/empresa_detalhe.html",
        empresa=empresa,
        usuarios=usuarios,
        licenca=licenca,
        usuario_padrao=usuario_padrao
    )

@bp.route("/empresas/<int:empresa_id>/desativar", methods=["POST"])
@login_required
@requer_master
def desativar_empresa(empresa_id):

    empresa = Empresa.query.get_or_404(empresa_id)

    if not empresa.ativa:
        flash("Empresa já está desativada.", "info")
        return redirect(url_for("master.listar_empresas"))

    empresa.ativa = False
    db.session.commit()

    flash("Empresa desativada com sucesso.", "warning")
    return redirect(url_for("master.listar_empresas"))

@bp.route("/empresas/<int:empresa_id>/ativar", methods=["POST"])
@login_required
@requer_master
def ativar_empresa(empresa_id):

    empresa = Empresa.query.get_or_404(empresa_id)

    if empresa.ativa:
        flash("Empresa já está ativa.", "info")
        return redirect(url_for("master.listar_empresas"))

    empresa.ativa = True
    db.session.commit()

    flash("Empresa ativada com sucesso.", "success")
    return redirect(url_for("master.listar_empresas"))


@bp.route("/empresas/<int:empresa_id>/renovar_licenca", methods=["POST"])
@login_required
@requer_master
def renovar_licenca(empresa_id):

    empresa = Empresa.query.get_or_404(empresa_id)

    licenca = LicencaSistema.query.filter_by(
        empresa_id=empresa.id
    ).first()

    if not licenca:
        licenca = LicencaSistema(
            empresa_id=empresa.id,
            data_inicio=date.today(),
            dias_acesso=30
        )
        db.session.add(licenca)
    else:
        # soma mais 30 dias
        licenca.dias_acesso += 30

    db.session.commit()

    flash("Licença renovada por mais 30 dias.", "success")
    return redirect(url_for("master.listar_empresas"))

from app.master.forms import ResetSenhaUsuarioForm

@bp.route("/empresas/<int:empresa_id>/usuarios/<int:usuario_id>/resetar_senha",
          methods=["GET", "POST"])
@login_required
@requer_master
def resetar_senha_usuario_empresa(empresa_id, usuario_id):

    empresa = Empresa.query.get_or_404(empresa_id)

    usuario = Usuario.query.filter_by(
        id=usuario_id,
        empresa_id=empresa.id
    ).first_or_404()

    form = ResetSenhaUsuarioForm()

    if form.validate_on_submit():
        usuario.set_password(form.nova_senha.data)
        db.session.commit()

        flash(
            f"Senha do usuário '{usuario.nome}' resetada com sucesso.",
            "success"
        )
        return redirect(
            url_for("master.detalhe_empresa", empresa_id=empresa.id)
        )

    return render_template(
        "master/resetar_senha_usuario.html",
        empresa=empresa,
        usuario=usuario,
        form=form
    )
