from flask import render_template, redirect, session, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Empresa, Usuario, LicencaSistema
from app.auth.forms import LoginForm
from app.auth import bp
from urllib.parse import urlparse, urljoin


# 🔒 segurança de redirect
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ('http', 'https')
        and ref_url.netloc == test_url.netloc
    )

@bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))

    form = LoginForm()

    if form.validate_on_submit():

        user = Usuario.query.filter_by(
            email=form.email.data.lower()
        ).first()


        if not user or not user.check_password(form.senha.data):
            flash("E-mail ou senha inválida.", "danger")
            return render_template("auth/login.html", form=form)

        # =====================================================
        # 👑 MASTER NÃO TEM RESTRIÇÕES
        # =====================================================
        if not user.is_master:

            # 🔒 BLOQUEIA EMPRESA DESATIVADA
            if not user.empresa_id:
                flash("Usuário sem empresa vinculada.", "danger")
                return render_template("auth/login.html", form=form)

            empresa = Empresa.query.filter_by(id=user.empresa_id).first()
            if not empresa or not empresa.ativa:
                flash(
                    "Empresa desativada. Entre em contato com o suporte.",
                    "danger"
                )
                return render_template("auth/login.html", form=form)

            # 🔒 BLOQUEIA LICENÇA
            licenca = (
                db.session.query(LicencaSistema)
                .filter(LicencaSistema.empresa_id == user.empresa_id)
                .first()
            )

            if not licenca or licenca.expirado:
                flash(
                    "Licença expirada ou inválida. Entre em contato com o suporte.",
                    "danger"
                )
                return render_template("auth/login.html", form=form)


        # =====================================================
        # ✅ LOGIN PERMITIDO
        # =====================================================
        login_user(user)

        session["permissoes"] = list(user.todas_permissoes)
        session.permanent = True
        session.modified = True

        flash("Login realizado com sucesso!", "success")

        next_page = request.form.get("next") or request.args.get("next")
        if next_page and next_page.lower() != "none" and is_safe_url(next_page):
            return redirect(next_page)

        if user.is_master:
            return redirect(url_for("master.listar_empresas"))

        return redirect(url_for("routes.home"))

    return render_template("auth/login.html", form=form)




@bp.route('/logout')
@login_required
def logout():
    logout_user()  # 🔹 Remove a sessão do usuário
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('auth.login'))  # 🔹 Redireciona para a tela de login


from app.auth.forms import TrocarSenhaForm  # Precisamos criar esse formulário
@bp.route('/trocar_senha', methods=['GET', 'POST'])
@login_required
def trocar_senha():
    """Permite que o usuário troque a senha, se tiver permissão."""
    if not current_user.pode_trocar_senha():
        flash("Você não tem permissão para alterar sua senha.", "danger")
        return redirect(url_for('routes.home'))  # Redireciona para a home

    form = TrocarSenhaForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.senha_atual.data):
            flash("Senha atual incorreta.", "danger")
        elif form.nova_senha.data != form.confirmar_senha.data:
            flash("As senhas não coincidem.", "danger")
        else:
            try:
                current_user.set_password(form.nova_senha.data)
                db.session.commit()
                flash("Senha alterada com sucesso!", "success")
                return redirect(url_for('routes.home'))
            except Exception as e:
                flash(f"Ocorreu um erro ao salvar a senha: {str(e)}", "danger")

    # 🔹 Exibe os erros do formulário caso existam
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Erro no campo {getattr(form, field).label.text}: {error}", "danger")

    return render_template('auth/trocar_senha.html', form=form)
