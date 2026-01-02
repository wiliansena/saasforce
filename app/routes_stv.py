import os
from flask import current_app, jsonify, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename  # 🔹 Para salvar o nome do arquivo corretamente

from app import db
from app.models import Cliente, Usuario, Servico, Conta, Tela, VendaStreaming
from app.forms import ServicoForm, ContaForm, VendaStreamingForm
from app.utils import formatar_data, formatar_moeda, requer_permissao

from sqlalchemy.exc import IntegrityError

from app import csrf


from app.routes import bp
from app.utils_datetime import utc_now
from app.utils_licenca import requer_licenca_ativa  # ← IMPORTA O MESMO BLUEPRINT DO routes.py
from app.utils_uploads import salvar_upload

@bp.route('/teste_stv')
@login_required
@requer_permissao("administrativo", "ver")
def teste_stv():
    print('chegou na rota stv')
    return render_template('stv/teste_stv.html')

### SERVICOS  ###

@bp.route("/stv/servicos")
@login_required
@requer_licenca_ativa
@requer_permissao("administrativo", "ver")
def stv_listar_servicos():

    page = request.args.get("page", 1, type=int)
    per_page = 15

    busca = request.args.get("busca", "").strip()

    query = Servico.query_empresa()

    if busca:
        busca_ilike = f"%{busca}%"
        query = query.filter(
            db.or_(
                Servico.nome.ilike(busca_ilike),
                Servico.tipo.ilike(busca_ilike)
            )
        )

    pagination = (
        query
        .order_by(Servico.nome)
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template(
        "stv/servicos_listar.html",
        servicos=pagination.items,
        pagination=pagination,
        busca=busca
    )



@bp.route("/stv/servicos/novo", methods=["GET", "POST"])
@login_required
@requer_licenca_ativa
@requer_permissao("administrativo", "criar")
def stv_novo_servico():

    form = ServicoForm()

    if form.validate_on_submit():

        servico = Servico(
            empresa_id=current_user.empresa_id,
            nome=form.nome.data,
            tipo=form.tipo.data,
            telas_total=form.telas_total.data,
            valor_investido=form.valor_investido.data,
            valor_venda_padrao=form.valor_venda_padrao.data,
            comissao_padrao=form.comissao_padrao.data,
            ativo=form.ativo.data,
        )

        if servico.tipo == "individual":
            servico.telas_total = 1

        # Salvar imagem se houver
        if form.imagem.data:
            caminho_relativo = salvar_upload(
                form.imagem.data,
                subpasta="servicos"
            )
            servico.imagem = caminho_relativo

        db.session.add(servico)
        db.session.commit()

        flash("Serviço cadastrado com sucesso!", "success")
        return redirect(url_for("routes.stv_listar_servicos"))

    return render_template("stv/servicos_form.html", form=form)



@bp.route("/stv/servicos/<int:id>/editar", methods=["GET", "POST"])
@login_required
@requer_licenca_ativa
@requer_permissao("administrativo", "editar")
def stv_editar_servico(id):

    servico = (
        Servico.query_empresa()
        .filter_by(id=id)
        .first_or_404()
    )

    form = ServicoForm(obj=servico)

    if form.validate_on_submit():

        servico.nome = form.nome.data
        servico.tipo = form.tipo.data
        servico.telas_total = form.telas_total.data
        servico.valor_investido = form.valor_investido.data
        servico.valor_venda_padrao = form.valor_venda_padrao.data
        servico.comissao_padrao = form.comissao_padrao.data
        servico.ativo = form.ativo.data

        if servico.tipo == "individual":
            servico.telas_total = 1
        
        # Salvar imagem se houver
        if form.imagem.data:
            caminho_relativo = salvar_upload(
                form.imagem.data,
                subpasta="servicos"
            )
            servico.imagem = caminho_relativo


        db.session.commit()

        flash("Serviço atualizado com sucesso!", "success")
        return redirect(url_for("routes.stv_listar_servicos"))

    return render_template("stv/servicos_form.html", form=form)


@bp.route("/stv/servicos/excluir/<int:id>", methods=["POST"])
@login_required
@requer_permissao("administrativo", "excluir")
def stv_excluir_servico(id):
    servico = (Servico.query_empresa()
               .filter_by(id=id)
               .first_or_404())


    contas_vinculadas = (Conta.query_empresa().filter_by(servico_id=servico.id).all())
    if contas_vinculadas:
        contas_str = ", ".join([c.email for c in contas_vinculadas])
        flash(
            f"Erro: Não é possível excluir o serviço pois está vinculado às contas: {contas_str}.",
            "danger"
        )
        return redirect(url_for("routes.stv_listar_servicos"))

    try:
        db.session.delete(servico)
        db.session.commit()
        flash("Serviço excluído com sucesso!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Erro: Não foi possível excluir o serviço.", "danger")

    return redirect(url_for("routes.stv_listar_servicos"))


@bp.route("/stv/contas")
@login_required
@requer_licenca_ativa
@requer_permissao("administrativo", "ver")
def stv_listar_contas():

    page = request.args.get("page", 1, type=int)
    per_page = 15

    busca = request.args.get("busca", "").strip()

    query = (
        Conta.query_empresa()
        .join(Servico)
    )

    if busca:
        busca_ilike = f"%{busca}%"
        query = query.filter(
            db.or_(
                Conta.email.ilike(busca_ilike),
                Conta.senha.ilike(busca_ilike),
                Servico.nome.ilike(busca_ilike)
            )
        )

    pagination = (
        query
        .order_by(Servico.nome, Conta.email)
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template(
        "stv/contas_listar.html",
        contas=pagination.items,
        pagination=pagination,
        busca=busca
    )



@bp.route("/stv/contas/nova", methods=["GET", "POST"])
@login_required
@requer_licenca_ativa
@requer_permissao("administrativo", "criar")
def stv_nova_conta():

    form = ContaForm()

    # 🔒 serviços SOMENTE da empresa
    form.servico_id.choices = [
        (s.id, s.nome)
        for s in Servico.query_empresa()
        .filter_by(ativo=True)
        .order_by(Servico.nome)
        .all()
    ]

    if form.validate_on_submit():

        conta = Conta(
            empresa_id=current_user.empresa_id,
            email=form.email.data,
            senha=form.senha.data,
            servico_id=form.servico_id.data,
            valor_venda_override=form.valor_venda_override.data,
            comissao_override=form.comissao_override.data,
            ativa=form.ativa.data,
            criado_em=utc_now()
        )

        db.session.add(conta)
        db.session.flush()  # 🔴 gera conta.id

        # 🔹 cria telas automaticamente
        total_telas = conta.servico.telas_total or 0
        for i in range(1, total_telas + 1):
            db.session.add(
                Tela(
                    empresa_id=current_user.empresa_id,  # 👈 OBRIGATÓRIO
                    conta_id=conta.id,
                    numero=i,
                    vendida=False
                )
            )


        db.session.commit()

        flash(
            f"Conta cadastrada com sucesso! {total_telas} tela(s) foram criadas automaticamente.",
            "success"
        )
        return redirect(url_for("routes.stv_listar_contas"))

    return render_template("stv/contas_form.html", form=form)


@bp.route("/stv/contas/<int:id>/editar", methods=["GET", "POST"])
@login_required
@requer_licenca_ativa
@requer_permissao("administrativo", "editar")
def stv_editar_conta(id):

    conta = (
        Conta.query_empresa()
        .filter_by(id=id)
        .first_or_404()
    )

    form = ContaForm(obj=conta)

    form.servico_id.choices = [
        (s.id, s.nome)
        for s in Servico.query_empresa()
        .filter_by(ativo=True)
        .order_by(Servico.nome)
        .all()
    ]

    if form.validate_on_submit():

        conta.email = form.email.data
        conta.senha = form.senha.data
        conta.servico_id = form.servico_id.data
        conta.valor_venda_override = form.valor_venda_override.data
        conta.comissao_override = form.comissao_override.data
        conta.ativa = form.ativa.data

        db.session.commit()

        flash("Conta atualizada com sucesso.", "success")
        return redirect(url_for("routes.stv_listar_contas"))

    return render_template(
        "stv/contas_form.html",
        form=form,
        conta=conta
    )


@bp.route("/stv/contas/excluir/<int:id>", methods=["POST"])
@login_required
@requer_licenca_ativa
@requer_permissao("administrativo", "excluir")
def stv_excluir_conta(id):

    conta = (
        Conta.query_empresa()
        .filter_by(id=id)
        .first_or_404()
    )

    telas_vendidas = (
        Tela.query_empresa()
        .filter_by(conta_id=conta.id, vendida=True)
        .all()
    )

    if telas_vendidas:
        flash(
            "Erro: Não é possível excluir a conta pois existem telas já vendidas.",
            "danger"
        )
        return redirect(url_for("routes.stv_listar_contas"))

    try:
        db.session.delete(conta)
        db.session.commit()
        flash("Conta excluída com sucesso!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Erro: Não foi possível excluir a conta.", "danger")

    return redirect(url_for("routes.stv_listar_contas"))


### ===============================
### IMPORTAÇÃO DE CONTAS
### ===============================

@bp.route("/stv/contas/importar/modelo")
@login_required
@requer_permissao("administrativo", "ver")
def stv_baixar_modelo_contas():

    import pandas as pd
    import io
    from flask import send_file

    df = pd.DataFrame(columns=[
        "email",
        "senha",
        "servico",
        "ativo",
        "valor_venda_override",
        "comissao_override"
    ])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="contas")

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="modelo_importacao_contas_streaming.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@bp.route("/stv/contas/importar", methods=["GET", "POST"])
@login_required
@requer_licenca_ativa
@requer_permissao("administrativo", "criar")
def stv_importar_contas():

    if request.method == "POST":
        arquivo = request.files.get("arquivo")

        if not arquivo:
            flash("Nenhum arquivo enviado.", "danger")
            return redirect(request.url)

        import pandas as pd

        try:
            df = pd.read_excel(arquivo)
        except Exception:
            flash("Arquivo inválido.", "danger")
            return redirect(request.url)

        obrigatorias = ["email", "servico"]
        for col in obrigatorias:
            if col not in df.columns:
                flash(f"Coluna obrigatória ausente: {col}", "danger")
                return redirect(request.url)

        criadas = 0
        ignoradas = 0
        servicos_nao_encontrados = set()


        for _, row in df.iterrows():

            email = str(row.get("email")).strip()
            senha = str(row.get("senha")).strip() if not pd.isna(row.get("senha")) else None
            nome_servico = str(row.get("servico")).strip()
            ativo = str(row.get("ativo", "SIM")).upper() == "SIM"

            valor_venda_override = row.get("valor_venda_override")
            comissao_override = row.get("comissao_override")

            if not email or not nome_servico:
                ignoradas += 1
                continue

            servico = (
                Servico.query_empresa()
                .filter_by(nome=nome_servico)
                .first()
            )

            if not servico:
                ignoradas += 1
                servicos_nao_encontrados.add(nome_servico)
                continue


            existe = (
                Conta.query_empresa()
                .filter_by(email=email, servico_id=servico.id)
                .first()
            )
            if existe:
                ignoradas += 1
                continue

            conta = Conta(
                empresa_id=current_user.empresa_id,
                email=email,
                senha=senha,
                servico_id=servico.id,
                valor_venda_override=valor_venda_override if not pd.isna(valor_venda_override) else None,
                comissao_override=comissao_override if not pd.isna(comissao_override) else None,
                ativa=ativo,
                criado_em=utc_now()
            )

            db.session.add(conta)
            db.session.flush()  # gera conta.id

            # 🔒 cria telas com empresa_id
            total_telas = servico.telas_total or 0
            for i in range(1, total_telas + 1):
                db.session.add(
                    Tela(
                        empresa_id=current_user.empresa_id,
                        conta_id=conta.id,
                        numero=i,
                        vendida=False
                    )
                )

            criadas += 1

        db.session.commit()

        mensagens = []
        mensagens.append(f"Importação concluída. Criadas: {criadas} | Ignoradas: {ignoradas}.")

        if servicos_nao_encontrados:
            lista = ", ".join(sorted(servicos_nao_encontrados))
            mensagens.append(
                f"As seguintes contas não foram importadas porque o serviço não está cadastrado: {lista}."
            )

        flash(" ".join(mensagens), "warning" if ignoradas else "success")


        return redirect(url_for("routes.stv_listar_contas"))

    return render_template("stv/contas_importar.html")

### ===============================
### VENDAS STV
### ===============================

from datetime import datetime
from sqlalchemy import func, text

@bp.route("/stv/vendas/listar")
@login_required
@requer_licenca_ativa
@requer_permissao("venda", "ver")
def stv_listar_vendas():

    page = request.args.get("page", 1, type=int)
    per_page = 20

    data_ini = request.args.get("data_ini")
    data_fim = request.args.get("data_fim")
    status = request.args.get("status")
    vendedor_id = request.args.get("vendedor_id")
    busca = request.args.get("busca", "").strip()

    # 🔹 converte filtros para DATE
    d_ini = (
        datetime.strptime(data_ini, "%Y-%m-%d").date()
        if data_ini else None
    )
    d_fim = (
        datetime.strptime(data_fim, "%Y-%m-%d").date()
        if data_fim else None
    )

    # 🔹 data de negócio (BR)
    data_br = func.date(
        VendaStreaming.data_venda - text("interval '3 hours'")
    )

    q = (
        VendaStreaming.query_empresa()
        .join(Usuario, Usuario.id == VendaStreaming.vendedor_id)
        .join(Cliente, Cliente.id == VendaStreaming.cliente_id)
        .outerjoin(Tela, Tela.id == VendaStreaming.tela_id)
        .outerjoin(Conta, Conta.id == Tela.conta_id)
        .join(Servico, Servico.id == VendaStreaming.servico_id)
    )

    # 🔹 filtros
    if status:
        q = q.filter(VendaStreaming.status == status)

    if vendedor_id:
        q = q.filter(VendaStreaming.vendedor_id == vendedor_id)

    # ✅ FILTRO DE DATA CORRETO
    if d_ini:
        q = q.filter(data_br >= d_ini)

    if d_fim:
        q = q.filter(data_br <= d_fim)

    # 🔥 BUSCA GLOBAL
    if busca:
        b = f"%{busca}%"
        q = q.filter(
            db.or_(
                Usuario.nome.ilike(b),
                Cliente.nome.ilike(b),
                Conta.email.ilike(b),
                Servico.nome.ilike(b),
                VendaStreaming.status.ilike(b),
                VendaStreaming.valor_venda.cast(db.String).ilike(b)
            )
        )

    vendas = (
        q.order_by(VendaStreaming.data_venda.desc())
         .paginate(page=page, per_page=per_page, error_out=False)
    )

    vendedores = (
        Usuario.query_empresa()
        .order_by(Usuario.nome)
        .all()
    )

    return render_template(
        "stv/vendas_listar.html",
        vendas=vendas,
        vendedores=vendedores,
        data_ini=data_ini,
        data_fim=data_fim,
        status=status,
        vendedor_id=vendedor_id,
        busca=busca
    )



@bp.route("/stv/mobile/vendas")
@login_required
@requer_licenca_ativa
@requer_permissao("venda", "ver")
def stv_listar_vendas_mobile():

    page = request.args.get("page", 1, type=int)
    per_page = 10  # menor para mobile

    data_ini = request.args.get("data_ini")
    data_fim = request.args.get("data_fim")
    status = request.args.get("status")
    vendedor_id = request.args.get("vendedor_id")
    busca = request.args.get("busca", "").strip()

    q = (
        VendaStreaming.query_empresa()
        .join(Usuario, Usuario.id == VendaStreaming.vendedor_id)
        .join(Cliente, Cliente.id == VendaStreaming.cliente_id)
        .outerjoin(Tela, Tela.id == VendaStreaming.tela_id)
        .outerjoin(Conta, Conta.id == Tela.conta_id)
        .join(Servico, Servico.id == VendaStreaming.servico_id)
    )

    if status:
        q = q.filter(VendaStreaming.status == status)

    if vendedor_id:
        q = q.filter(VendaStreaming.vendedor_id == vendedor_id)

    if data_ini:
        q = q.filter(VendaStreaming.data_venda >= data_ini)

    if data_fim:
        q = q.filter(VendaStreaming.data_venda <= data_fim)

    if busca:
        b = f"%{busca}%"
        q = q.filter(
            db.or_(
                Cliente.nome.ilike(b),
                Usuario.nome.ilike(b),
                Conta.email.ilike(b),
                Servico.nome.ilike(b),
                VendaStreaming.status.ilike(b)
            )
        )

    vendas = (
        q.order_by(VendaStreaming.data_venda.desc())
         .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template(
        "stv/vendas_listar_mobile.html",
        vendas=vendas,
        data_ini=data_ini,
        data_fim=data_fim,
        status=status,
        vendedor_id=vendedor_id,
        busca=busca
    )




@bp.route("/stv/vendas/pendentes")
@login_required
@requer_licenca_ativa
@requer_permissao("venda", "ver")
def stv_listar_vendas_pendentes():

    vendas_pendentes = (
        VendaStreaming.query_empresa()
        .join(Usuario, Usuario.id == VendaStreaming.vendedor_id)
        .outerjoin(Tela, Tela.id == VendaStreaming.tela_id)
        .outerjoin(Conta, Conta.id == Tela.conta_id)
        .filter(VendaStreaming.status == "PENDENTE")
        .order_by(VendaStreaming.data_venda.desc())
        .all()
    )

    return render_template(
        "stv/vendas_pendentes_mobile.html",
        vendas_pendentes=vendas_pendentes
    )



@bp.route("/stv/vendas")
@login_required
@requer_licenca_ativa
@requer_permissao("venda", "ver")
def stv_vendas_servicos():

    dados = []

    servicos = (
        Servico.query_empresa()
        .filter_by(ativo=True)
        .all()
    )

    for s in servicos:

        telas_livres = 0
        telas_vendidas = 0

        contas = (
            Conta.query_empresa()
            .filter_by(servico_id=s.id, ativa=True)
            .all()
        )

        for c in contas:
            for t in c.telas:
                if t.vendida:
                    telas_vendidas += 1
                else:
                    telas_livres += 1

        dados.append({
            "servico": s,
            "livres": telas_livres,
            "vendidas": telas_vendidas
        })

    return render_template(
        "stv/vendas_servicos.html",
        dados=dados
    )


@bp.route("/stv/vendas/servico/<int:servico_id>", methods=["GET", "POST"])
@login_required
@requer_licenca_ativa
@requer_permissao("venda", "criar")
def stv_vender_servico(servico_id):

    servico = (
        Servico.query_empresa()
        .filter_by(id=servico_id)
        .first_or_404()
    )

    form = VendaStreamingForm()

    contas = (
        Conta.query_empresa()
        .filter_by(servico_id=servico.id, ativa=True)
        .all()
    )

    contas_com_telas = []
    for c in contas:
        livres = [t for t in c.telas if not t.vendida]
        if livres:
            contas_com_telas.append((c, len(livres)))

    if form.validate_on_submit():

        telefone = ''.join(filter(str.isdigit, form.telefone.data))
        telefone = telefone.replace("55", "", 1) if telefone.startswith("55") else telefone

        cliente = (
            Cliente.query_empresa()
            .filter_by(telefone=telefone)
            .first()
        )

        if not cliente:
            cliente = Cliente(
                empresa_id=current_user.empresa_id,
                telefone=telefone,
                nome=f"Cliente {telefone}"
            )
            db.session.add(cliente)
            db.session.flush()

        conta_id = request.form.get("conta_id")
        conta = (
            Conta.query_empresa()
            .filter_by(id=conta_id)
            .first()
            if conta_id else None
        )

        if conta:
            valor_venda = (
                conta.valor_venda_override
                if conta.valor_venda_override is not None
                else servico.valor_venda_padrao
            )
            valor_comissao = (
                conta.comissao_override
                if conta.comissao_override is not None
                else servico.comissao_padrao
            )
        else:
            valor_venda = servico.valor_venda_padrao
            valor_comissao = servico.comissao_padrao

        venda = VendaStreaming(
            empresa_id=current_user.empresa_id,
            cliente_id=cliente.id,
            servico_id=servico.id,
            vendedor_id=current_user.id,
            valor_venda=valor_venda,
            valor_comissao=valor_comissao,
            status="PENDENTE",
            data_venda=utc_now()
        )

        if conta:
            tela = (
                Tela.query_empresa()
                .filter_by(conta_id=conta.id, vendida=False)
                .order_by(Tela.numero)
                .first()
            )
            if tela:
                tela.vendida = True
                venda.tela_id = tela.id
                venda.status = "ATIVA"
                venda.data_entrega = utc_now()

        db.session.add(venda)
        db.session.commit()

        flash("Venda registrada com sucesso!", "success")

        return render_template(
            "stv/vendas_confirmar.html",
            servico=servico,
            venda=venda,
            venda_confirmada=True
        )

    return render_template(
        "stv/vendas_confirmar.html",
        servico=servico,
        contas_com_telas=contas_com_telas,
        form=form
    )


@bp.route("/stv/vendas/<int:venda_id>/finalizar", methods=["GET", "POST"])
@login_required
@requer_licenca_ativa
@requer_permissao("venda", "editar")
def stv_finalizar_venda(venda_id):

    venda = (
        VendaStreaming.query_empresa()
        .filter_by(id=venda_id)
        .first_or_404()
    )

    if venda.status != "PENDENTE":
        flash("Esta venda já foi finalizada.", "warning")
        return redirect(url_for("routes.stv_listar_vendas"))

    servico = venda.servico

    contas = (
        Conta.query_empresa()
        .filter_by(servico_id=servico.id, ativa=True)
        .all()
    )

    contas_com_telas = []
    for c in contas:
        livres = [t for t in c.telas if not t.vendida]
        if livres:
            contas_com_telas.append((c, len(livres)))

    if request.method == "POST":

        conta_id = request.form.get("conta_id")
        if not conta_id:
            flash("Selecione uma conta para finalizar a venda.", "danger")
            return redirect(request.url)

        conta = (
            Conta.query_empresa()
            .filter_by(id=conta_id)
            .first_or_404()
        )

        tela = (
            Tela.query_empresa()
            .filter_by(conta_id=conta.id, vendida=False)
            .order_by(Tela.numero)
            .first()
        )

        if not tela:
            flash("Conta sem telas disponíveis.", "danger")
            return redirect(request.url)

        tela.vendida = True
        venda.tela_id = tela.id
        venda.status = "ATIVA"
        venda.data_entrega = utc_now()

        venda.valor_venda = (
            conta.valor_venda_override
            if conta.valor_venda_override is not None
            else servico.valor_venda_padrao
        )

        venda.valor_comissao = (
            conta.comissao_override
            if conta.comissao_override is not None
            else servico.comissao_padrao
        )

        db.session.commit()

        flash("Venda finalizada e conta entregue!", "success")

        return render_template(
            "stv/vendas_finalizar.html",
            venda=venda,
            servico=servico,
            contas_com_telas=contas_com_telas,
            venda_confirmada=True
        )

    return render_template(
        "stv/vendas_finalizar.html",
        venda=venda,
        servico=servico,
        contas_com_telas=contas_com_telas,
        venda_confirmada=False
    )


@bp.route("/stv/vendas/<int:venda_id>/cancelar", methods=["POST"])
@login_required
@requer_licenca_ativa
@requer_permissao("venda", "editar")
def stv_cancelar_venda(venda_id):

    venda = (
        VendaStreaming.query_empresa()
        .filter_by(id=venda_id)
        .first_or_404()
    )

    if venda.status == "CANCELADA":
        flash("Esta venda já está cancelada.", "warning")
        return redirect(url_for("routes.stv_listar_vendas"))

    if venda.status == "ATIVA" and venda.tela:
        venda.tela.vendida = False
        venda.tela = None

    venda.status = "CANCELADA"
    db.session.commit()

    flash("Venda cancelada com sucesso.", "success")
    return redirect(url_for("routes.stv_listar_vendas"))





#### BI STV ####


##  helpers  ###
from datetime import datetime, time
from app.utils_datetime import br_to_utc

def periodo_datetime(data_ini, data_fim):
    dt_ini = None
    dt_fim = None

    if data_ini:
        dt_ini = datetime.combine(
            datetime.strptime(data_ini, "%Y-%m-%d").date(),
            time.min
        )
        dt_ini = br_to_utc(dt_ini)

    if data_fim:
        dt_fim = datetime.combine(
            datetime.strptime(data_fim, "%Y-%m-%d").date(),
            time.max
        )
        dt_fim = br_to_utc(dt_fim)

    return dt_ini, dt_fim


from datetime import date, timedelta

@bp.route("/stv/bi/dashboard", methods=["GET"])
@login_required
@requer_permissao("administrativo", "ver")
def stv_bi_dashboard():

    hoje = date.today()

    data_ini = request.args.get(
        "data_ini",
        (hoje - timedelta(days=30)).strftime("%Y-%m-%d")
    )

    data_fim = request.args.get(
        "data_fim",
        hoje.strftime("%Y-%m-%d")
    )

    return render_template(
        "stv/bi/dashboard.html",
        data_ini=data_ini,
        data_fim=data_fim
    )


@bp.route("/stv/bi/kpis")
@login_required
@requer_permissao("administrativo", "ver")
def stv_bi_kpis():

    data_ini = request.args.get("data_ini")
    data_fim = request.args.get("data_fim")

    dt_ini, dt_fim = periodo_datetime(data_ini, data_fim)

    q = (
        VendaStreaming.query_empresa()
        .filter(VendaStreaming.status.in_(["ATIVA", "PENDENTE"]))
    )

    if dt_ini:
        q = q.filter(VendaStreaming.data_venda >= dt_ini)
    if dt_fim:
        q = q.filter(VendaStreaming.data_venda <= dt_fim)

    total_vendido = q.with_entities(
        func.coalesce(func.sum(VendaStreaming.valor_venda), 0)
    ).scalar()

    total_comissao = q.with_entities(
        func.coalesce(func.sum(VendaStreaming.valor_comissao), 0)
    ).scalar()

    # 🔹 investimento SOMENTE da empresa
    total_investido = (
        db.session.query(
            func.coalesce(func.sum(Servico.valor_investido), 0)
        )
        .filter(
            Servico.empresa_id == current_user.empresa_id,
            Servico.ativo == True
        )
        .scalar()
    )

    lucro = total_vendido - total_comissao - total_investido

    return jsonify({
        "total_vendido": formatar_moeda(total_vendido),
        "total_comissao": formatar_moeda(total_comissao),
        "total_investido": formatar_moeda(total_investido),
        "lucro": formatar_moeda(lucro)
    })

@bp.route("/stv/bi/comissao_por_vendedor")
@login_required
@requer_permissao("administrativo", "ver")
def stv_bi_comissao_por_vendedor():

    data_ini = request.args.get("data_ini")
    data_fim = request.args.get("data_fim")

    dt_ini, dt_fim = periodo_datetime(data_ini, data_fim)

    q = (
        db.session.query(
            Usuario.nome.label("vendedor"),
            func.sum(VendaStreaming.valor_comissao).label("total")
        )
        .join(VendaStreaming, VendaStreaming.vendedor_id == Usuario.id)
        .filter(
            VendaStreaming.empresa_id == current_user.empresa_id,
            VendaStreaming.status.in_(["ATIVA", "PENDENTE"])
        )
    )

    if dt_ini:
        q = q.filter(VendaStreaming.data_venda >= dt_ini)
    if dt_fim:
        q = q.filter(VendaStreaming.data_venda <= dt_fim)

    q = (
        q.group_by(Usuario.nome)
         .order_by(func.sum(VendaStreaming.valor_comissao).desc())
    )

    return jsonify([
        {
            "vendedor": v,
            "total": float(t or 0),
            "total_fmt": formatar_moeda(t or 0)
        }
        for v, t in q.all()
    ])

@bp.route("/stv/bi/ranking_vendedores")
@login_required
@requer_permissao("venda", "ver")
def stv_bi_ranking_vendedores():

    hoje = date.today()

    data_ini = request.args.get(
        "data_ini",
        (hoje - timedelta(days=30)).strftime("%Y-%m-%d")
    )
    data_fim = request.args.get(
        "data_fim",
        hoje.strftime("%Y-%m-%d")
    )

    return render_template(
        "stv/bi/ranking_vendedores.html",
        data_ini=data_ini,
        data_fim=data_fim
    )


@bp.route("/stv/bi/vendido_por_dia")
@login_required
@requer_permissao("administrativo", "ver")
def stv_bi_vendido_por_dia():

    data_ini = request.args.get("data_ini")
    data_fim = request.args.get("data_fim")

    # 🔹 converte datas do filtro (BR) para date
    dt_ini = datetime.strptime(data_ini, "%Y-%m-%d").date() if data_ini else None
    dt_fim = datetime.strptime(data_fim, "%Y-%m-%d").date() if data_fim else None

    # 🔹 define o "dia de negócio" (BR)
    dia_br = func.date(
        VendaStreaming.data_venda - text("interval '3 hours'")
    )

    q = (
        db.session.query(
            dia_br.label("dia"),
            func.sum(VendaStreaming.valor_venda).label("total")
        )
        .filter(
            VendaStreaming.empresa_id == current_user.empresa_id,
            VendaStreaming.status.in_(["ATIVA", "PENDENTE"])
        )
    )

    if dt_ini:
        q = q.filter(dia_br >= dt_ini)
    if dt_fim:
        q = q.filter(dia_br <= dt_fim)

    q = q.group_by(dia_br).order_by(dia_br)

    return jsonify([
        {"dia": formatar_data(d), "total": float(t or 0)}
        for d, t in q.all()
    ])



###

from datetime import date, timedelta
@bp.route("/stv/bi/comissao_vendedores")
@login_required
@requer_permissao("venda", "ver")
def stv_bi_comissao_vendedores():

    hoje = date.today()

    data_ini = request.args.get(
        "data_ini",
        (hoje - timedelta(days=30)).strftime("%Y-%m-%d")
    )
    data_fim = request.args.get(
        "data_fim",
        hoje.strftime("%Y-%m-%d")
    )

    dt_ini, dt_fim = periodo_datetime(data_ini, data_fim)

    ranking = (
        db.session.query(
            Usuario.id.label("vendedor_id"),
            Usuario.nome.label("vendedor"),
            func.count(VendaStreaming.id).label("qtd_vendas"),
            func.sum(VendaStreaming.valor_venda).label("total_vendido"),
            func.sum(VendaStreaming.valor_comissao).label("total_comissao"),
        )
        .join(VendaStreaming, VendaStreaming.vendedor_id == Usuario.id)
        .filter(
            VendaStreaming.empresa_id == current_user.empresa_id,
            VendaStreaming.status.in_(["ATIVA", "PENDENTE"])
        )
    )

    if dt_ini:
        ranking = ranking.filter(VendaStreaming.data_venda >= dt_ini)
    if dt_fim:
        ranking = ranking.filter(VendaStreaming.data_venda <= dt_fim)

    ranking = (
        ranking.group_by(Usuario.id, Usuario.nome)
               .order_by(func.sum(VendaStreaming.valor_comissao).desc())
               .all()
    )

    vendedores = []

    for r in ranking:
        vendas_q = (
            db.session.query(
                VendaStreaming.data_venda,
                Servico.nome.label("servico"),
                Conta.email.label("conta"),
                VendaStreaming.valor_venda,
                VendaStreaming.valor_comissao,
                VendaStreaming.status
            )
            .join(Servico, Servico.id == VendaStreaming.servico_id)
            .outerjoin(Tela, Tela.id == VendaStreaming.tela_id)
            .outerjoin(Conta, Conta.id == Tela.conta_id)
            .filter(
                VendaStreaming.vendedor_id == r.vendedor_id,
                VendaStreaming.empresa_id == current_user.empresa_id,
                VendaStreaming.status.in_(["ATIVA", "PENDENTE"])
            )
        )

        if dt_ini:
            vendas_q = vendas_q.filter(VendaStreaming.data_venda >= dt_ini)
        if dt_fim:
            vendas_q = vendas_q.filter(VendaStreaming.data_venda <= dt_fim)

        vendas = vendas_q.order_by(VendaStreaming.data_venda.desc()).all()


        vendedores.append({
            "vendedor": r.vendedor,
            "qtd_vendas": r.qtd_vendas or 0,
            "total_vendido": r.total_vendido or 0,
            "total_comissao": r.total_comissao or 0,
            "vendas": [
                {
                    "data": formatar_data(v.data_venda),
                    "servico": v.servico,
                    "conta": v.conta or "-",
                    "status": v.status,
                    "valor_venda": formatar_moeda(v.valor_venda),
                    "valor_comissao": formatar_moeda(v.valor_comissao),
                }
                for v in vendas
            ]
        })

    return render_template(
        "stv/bi/comissao_vendedores.html",
        vendedores=vendedores,
        data_ini=data_ini,
        data_fim=data_fim
    )


from datetime import date, timedelta
from flask import make_response, request, render_template
from weasyprint import HTML
from sqlalchemy import func, text

@bp.route("/stv/relatorios/comissao_vendedores/pdf")
@login_required
@requer_permissao("venda", "ver")
def stv_relatorio_comissao_vendedores_pdf():

    hoje = date.today()

    data_ini = request.args.get(
        "data_ini",
        (hoje - timedelta(days=30)).strftime("%Y-%m-%d")
    )
    data_fim = request.args.get(
        "data_fim",
        hoje.strftime("%Y-%m-%d")
    )

    dt_ini, dt_fim = periodo_datetime(data_ini, data_fim)

    # ------------------------------------------------
    # COMISSÃO POR VENDEDOR (ATIVA + PENDENTE)
    # ------------------------------------------------
    q = (
        db.session.query(
            Usuario.id.label("vendedor_id"),
            Usuario.nome.label("vendedor"),
            func.coalesce(
                func.sum(VendaStreaming.valor_comissao), 0
            ).label("total_comissao")
        )
        .join(VendaStreaming, VendaStreaming.vendedor_id == Usuario.id)
        .filter(
            VendaStreaming.empresa_id == current_user.empresa_id,
            VendaStreaming.status.in_(["ATIVA", "PENDENTE"])
        )
    )

    if dt_ini:
        q = q.filter(VendaStreaming.data_venda >= dt_ini)
    if dt_fim:
        q = q.filter(VendaStreaming.data_venda <= dt_fim)

    resultados = (
        q.group_by(Usuario.id, Usuario.nome)
         .order_by(func.sum(VendaStreaming.valor_comissao).desc())
         .all()
    )

    # ------------------------------------------------
    # MONTA DADOS + OBSERVAÇÃO DE PENDÊNCIA
    # ------------------------------------------------
    dados = []
    total_geral = 0

    for r in resultados:

        q_pendentes = (
            db.session.query(func.count(VendaStreaming.id))
            .filter(
                VendaStreaming.empresa_id == current_user.empresa_id,
                VendaStreaming.vendedor_id == r.vendedor_id,
                VendaStreaming.status == "PENDENTE"
            )
        )

        if dt_ini:
            q_pendentes = q_pendentes.filter(VendaStreaming.data_venda >= dt_ini)
        if dt_fim:
            q_pendentes = q_pendentes.filter(VendaStreaming.data_venda <= dt_fim)

        tem_pendentes = q_pendentes.scalar() > 0

        dados.append({
            "vendedor": r.vendedor,
            "total_comissao": r.total_comissao or 0,
            "observacao": (
                "Possui vendas pendentes no período"
                if tem_pendentes else ""
            )
        })

        total_geral += r.total_comissao or 0

    html = render_template(
        "stv/relatorios/comissao_vendedores_pdf.html",
        dados=dados,
        total_geral=total_geral,
        data_ini=data_ini,
        data_fim=data_fim
    )

    pdf = HTML(string=html, base_url=request.url_root).write_pdf()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f"inline; filename=comissao_vendedores_{data_ini}_a_{data_fim}.pdf"
    )

    return response



from datetime import date, timedelta
from flask import request, make_response, render_template
from weasyprint import HTML
from sqlalchemy import func

@bp.route("/stv/relatorios/vendas/pdf")
@login_required
@requer_permissao("venda", "ver")
def stv_relatorio_vendas_pdf():

    hoje = date.today()

    data_ini = request.args.get(
        "data_ini",
        (hoje - timedelta(days=30)).strftime("%Y-%m-%d")
    )
    data_fim = request.args.get(
        "data_fim",
        hoje.strftime("%Y-%m-%d")
    )
    status = request.args.get("status")
    vendedor_id = request.args.get("vendedor_id")

    dt_ini, dt_fim = periodo_datetime(data_ini, data_fim)

    # -------------------------
    # BASE DE VENDAS (POR EMPRESA)
    # -------------------------
    q = (
        db.session.query(
            VendaStreaming.data_venda,
            Usuario.nome.label("vendedor"),
            Cliente.nome.label("cliente"),
            Servico.nome.label("servico"),
            Tela.numero.label("tela"),
            VendaStreaming.valor_venda,
            VendaStreaming.valor_comissao,
            VendaStreaming.status
        )
        .join(Usuario, Usuario.id == VendaStreaming.vendedor_id)
        .join(Cliente, Cliente.id == VendaStreaming.cliente_id)
        .join(Servico, Servico.id == VendaStreaming.servico_id)
        .outerjoin(Tela, Tela.id == VendaStreaming.tela_id)
        .filter(VendaStreaming.empresa_id == current_user.empresa_id)
    )

    if status:
        q = q.filter(VendaStreaming.status == status)

    if vendedor_id:
        q = q.filter(VendaStreaming.vendedor_id == vendedor_id)

    if dt_ini:
        q = q.filter(VendaStreaming.data_venda >= dt_ini)

    if dt_fim:
        q = q.filter(VendaStreaming.data_venda <= dt_fim)

    vendas = q.order_by(VendaStreaming.data_venda.desc()).all()

    # -------------------------
    # TOTAIS
    # -------------------------
    total_vendas = sum(
        v.valor_venda or 0 for v in vendas if v.status == "ATIVA"
    )

    total_comissao = sum(
        v.valor_comissao or 0 for v in vendas if v.status == "ATIVA"
    )

    total_vendas_pendente = sum(
        v.valor_venda or 0 for v in vendas if v.status == "PENDENTE"
    )

    total_comissao_pendente = sum(
        v.valor_comissao or 0 for v in vendas if v.status == "PENDENTE"
    )

    total_vendas_cancelada = sum(
        v.valor_venda or 0 for v in vendas if v.status == "CANCELADA"
    )

    total_comissao_cancelada = sum(
        v.valor_comissao or 0 for v in vendas if v.status == "CANCELADA"
    )

    total_vendas_geral = sum(v.valor_venda or 0 for v in vendas)
    total_comissao_geral = sum(v.valor_comissao or 0 for v in vendas)

    html = render_template(
        "stv/relatorios/vendas_pdf.html",
        vendas=vendas,
        total_vendas=total_vendas,
        total_comissao=total_comissao,
        total_vendas_pendente=total_vendas_pendente,
        total_comissao_pendente=total_comissao_pendente,
        total_vendas_cancelada=total_vendas_cancelada,
        total_comissao_cancelada=total_comissao_cancelada,
        total_vendas_geral=total_vendas_geral,
        total_comissao_geral=total_comissao_geral,
        data_ini=data_ini,
        data_fim=data_fim,
        status=status
    )

    pdf = HTML(string=html, base_url=request.url_root).write_pdf()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f"inline; filename=vendas_{data_ini}_a_{data_fim}.pdf"
    )

    return response

