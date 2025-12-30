from datetime import date
import io
import os
from sqlite3 import IntegrityError
from app.utils import requer_permissao, somente_admin
from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request, g
from flask_login import current_user, login_required
import pytz
from datetime import datetime, time
from app import db, csrf

from app.models import LicencaSistema, LogAcao, Usuario, Permissao 
from app.forms import UsuarioForm
from app.utils_licenca import requer_licenca_ativa




bp = Blueprint('routes', __name__)


from app import routes_stv


UPLOAD_FOLDER = 'app/static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@bp.before_request
def carregar_permissoes():
    """Garante que as permissões do usuário estejam disponíveis em todas as páginas."""
    if current_user.is_authenticated:
        g.permissoes = current_user.todas_permissoes
    else:
        g.permissoes = set()  # Usuário sem permissões


    
@bp.route('/usuarios')
@login_required
@requer_licenca_ativa
@requer_permissao('usuarios', 'ver')
def listar_usuarios():

    usuarios = (
        Usuario.query_empresa()
        .order_by(Usuario.nome)
        .all()
    )

    return render_template(
        'usuarios.html',
        usuarios=usuarios
    )


@bp.route('/usuario/novo', methods=['GET', 'POST'])
@login_required
@requer_licenca_ativa
@requer_permissao('usuarios', 'criar')
def novo_usuario():

    form = UsuarioForm()

    if form.validate_on_submit():

        # =====================================================
        # 🔒 valida NOME (unicidade por empresa)
        # =====================================================
        existe_nome = (
            Usuario.query_empresa()
            .filter(Usuario.nome.ilike(form.nome.data))
            .first()
        )

        if existe_nome:
            flash(
                "Já existe um usuário com esse nome nesta empresa.",
                "danger"
            )
            return render_template('novo_usuario.html', form=form)

        # =====================================================
        # 🔒 valida EMAIL (unicidade por empresa)
        # =====================================================
        existe_email = (
            Usuario.query_empresa()
            .filter(Usuario.email.ilike(form.email.data))
            .first()
        )

        if existe_email:
            flash(
                "Já existe um usuário com esse e-mail nesta empresa.",
                "danger"
            )
            return render_template('novo_usuario.html', form=form)

        # =====================================================
        # ✅ cria usuário
        # =====================================================
        usuario = Usuario(
            nome=form.nome.data,
            email=form.email.data,
            empresa_id=current_user.empresa_id
        )
        usuario.set_password(form.senha.data)

        try:
            db.session.add(usuario)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(
                f"Erro ao criar usuário: {str(e)}",
                "danger"
            )
            return render_template('novo_usuario.html', form=form)

        flash("Usuário criado com sucesso!", "success")
        return redirect(url_for('routes.listar_usuarios'))

    return render_template('novo_usuario.html', form=form)

@bp.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@requer_licenca_ativa
@requer_permissao('usuarios', 'editar')
def editar_usuario(id):

    usuario = (
        Usuario.query_empresa()
        .filter_by(id=id)
        .first_or_404()
    )

    # 🔒 impede editar a si mesmo sem permissão
    if usuario.id == current_user.id and not current_user.tem_permissao('usuarios', 'editar'):
        flash("Você não pode editar seu próprio usuário.", "danger")
        return redirect(url_for('routes.listar_usuarios'))

    form = UsuarioForm(obj=usuario)

    if form.validate_on_submit():

        # 🔒 valida email único GLOBAL
        existe_email = (
            Usuario.query
            .filter(Usuario.email.ilike(form.email.data))
            .filter(Usuario.id != usuario.id)
            .first()
        )

        if existe_email:
            flash("Este e-mail já está em uso.", "danger")
            return render_template(
                'usuarios/editar_usuario.html',
                form=form,
                usuario=usuario
            )

        usuario.nome = form.nome.data
        usuario.email = form.email.data.lower()

        if form.senha.data:
            usuario.set_password(form.senha.data)

        db.session.commit()
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for('routes.listar_usuarios'))

    return render_template(
        'usuarios/editar_usuario.html',
        form=form,
        usuario=usuario
    )


from app.auth.forms import AdminAlterarSenhaForm

@bp.route('/usuarios/alterar_senha/<int:id>', methods=['GET', 'POST'])
@login_required
@requer_licenca_ativa
@requer_permissao('usuarios', 'editar')
def alterar_senha_usuario(id):

    usuario = (
        Usuario.query_empresa()
        .filter_by(id=id)
        .first_or_404()
    )

    # 🔒 não permitir alterar a própria senha por esta rota
    if usuario.id == current_user.id:
        flash(
            "Para alterar sua própria senha, use a opção 'Trocar Senha'.",
            "info"
        )
        return redirect(url_for('routes.listar_usuarios'))

    form = AdminAlterarSenhaForm()

    if form.validate_on_submit():
        usuario.set_password(form.nova_senha.data)
        db.session.commit()

        flash(
            f"Senha do usuário '{usuario.nome}' alterada com sucesso!",
            "success"
        )
        return redirect(url_for('routes.listar_usuarios'))

    # 👇 AQUI entra o feedback quando NÃO valida
    elif form.is_submitted():
        for campo, erros in form.errors.items():
            for erro in erros:
                flash(erro, "danger")

    return render_template(
        "usuarios/alterar_senha.html",
        form=form,
        usuario=usuario
    )

@bp.route('/usuarios/permissoes/<int:id>', methods=['GET', 'POST'])
@login_required
@requer_licenca_ativa
@requer_permissao('usuarios', 'ver')
def gerenciar_permissoes(id):

    usuario = (
        Usuario.query_empresa()
        .filter_by(id=id)
        .first_or_404()
    )

    # =====================================================
    # 🔒 GOVERNANÇA
    # =====================================================
    if usuario.id == current_user.id and not current_user.is_admin_empresa:
        flash(
            "Você não pode alterar suas próprias permissões.",
            "danger"
        )
        return redirect(url_for('routes.listar_usuarios'))

    # =====================================================
    # 🧠 MAPA REAL DE PERMISSÕES
    # =====================================================
    mapa_permissoes = {
        "venda": ["criar", "ver", "editar", "excluir"],
        "administrativo": ["criar", "ver", "editar", "excluir"],
        "usuarios": ["criar", "ver", "editar", "excluir"],
        "trocar_senha": ["editar"],
    }

    if request.method == "POST":

        empresa_id = current_user.empresa_id

        # =====================================================
        # 📥 PERMISSÕES MARCADAS NO FORMULÁRIO (verdade final)
        # =====================================================
        selecionadas = set()

        for categoria, acoes in mapa_permissoes.items():
            for acao in acoes:
                if request.form.get(f"{categoria}_{acao}"):
                    selecionadas.add((categoria, acao))

        # =====================================================
        # 🛡️ PROTEÇÃO DO ADMIN PRINCIPAL
        # =====================================================
        if usuario.id == current_user.id and current_user.is_admin_empresa:
            selecionadas.update({
                ("usuarios", "ver"),
                ("usuarios", "editar"),
            })

        # =====================================================
        # 🔎 PERMISSÕES ATUAIS NO BANCO (empresa)
        # =====================================================
        atuais = {
            (p.categoria, p.acao)
            for p in Permissao.query_empresa()
            .filter_by(usuario_id=usuario.id)
            .all()
        }

        # =====================================================
        # ➕ INSERIR O QUE FALTA
        # =====================================================
        for categoria, acao in selecionadas - atuais:
            db.session.add(
                Permissao(
                    empresa_id=empresa_id,
                    usuario_id=usuario.id,
                    categoria=categoria,
                    acao=acao
                )
            )

        # =====================================================
        # ➖ REMOVER O QUE NÃO FOI MARCADO
        # =====================================================
        for categoria, acao in atuais - selecionadas:
            Permissao.query_empresa().filter_by(
                usuario_id=usuario.id,
                categoria=categoria,
                acao=acao
            ).delete()

        db.session.commit()

        flash("Permissões atualizadas com sucesso!", "success")
        return redirect(url_for('routes.listar_usuarios'))

    # =====================================================
    # 🔎 PERMISSÕES ATUAIS (GET)
    # =====================================================
    permissoes_existentes = {
        f"{p.categoria}_{p.acao}"
        for p in usuario.permissoes
        if p.empresa_id == current_user.empresa_id
    }

    categorias = list(mapa_permissoes.keys())
    acoes = ["criar", "ver", "editar", "excluir"]

    return render_template(
        'usuarios/gerenciar_permissoes.html',
        usuario=usuario,
        categorias=categorias,
        acoes=acoes,
        permissoes_existentes=permissoes_existentes
    )



@bp.route('/logs')
@login_required
@requer_permissao('usuarios', 'ver')
def listar_logs():

    logs = (
        LogAcao.query
        .filter_by(empresa_id=current_user.empresa_id)
        .order_by(LogAcao.data_hora.desc())
        .all()
    )

    return render_template('logs.html', logs=logs)


@bp.route('/')
@login_required
def home():
    user_agent = request.headers.get('User-Agent', '').lower()
    if any(mobile in user_agent for mobile in ['iphone', 'android', 'mobile']):
        return redirect(url_for('routes.home_mobile'))
    return render_template('home.html')

@bp.route('/home')
@login_required
def home_desktop():
    return render_template('home.html')


@bp.route('/home_mobile')
@login_required
def home_mobile():
    return render_template('home_mobile.html')


#### LICENÇA SISTEMA ####

@bp.route('/licencas')
@login_required
@somente_admin
def listar_licencas():
    licencas = LicencaSistema.query.order_by(LicencaSistema.id.desc()).all()
    return render_template('licencas.html', licencas=licencas)


@bp.route('/licenca/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@somente_admin
def editar_licenca(id):
    licenca = LicencaSistema.query.get_or_404(id)
    licenca.data_inicio = date.today()
    licenca.dias_acesso = 30
    db.session.commit()
    flash('Licença atualizada com sucesso!', 'success')
    return redirect(url_for('routes.listar_licencas'))


@bp.route('/licenca/excluir/<int:id>', methods=['POST'])
@login_required
@somente_admin
def excluir_licenca(id):
    licenca = LicencaSistema.query.get_or_404(id)
    db.session.delete(licenca)
    db.session.commit()
    flash("Licença excluída com sucesso!", "success")
    return redirect(url_for('routes.listar_licencas'))
