from decimal import Decimal
import secrets
from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Empresa, Servico, Usuario, VendaStreaming, Cliente, VendaTokenAcesso
from app.services.pagamento.mercadopago_client import MercadoPagoClient
from app.utils_datetime import utc_now

bp_public = Blueprint("public", __name__)


@bp_public.route('/checkout/teste')
def checkout_teste():
    print('chegou na rota checkout')
    return render_template('configuracoes/1.html')

from decimal import Decimal
import secrets
from werkzeug.security import generate_password_hash


@bp_public.route("/<slug>/checkout/<int:servico_id>", methods=["GET", "POST"])
def checkout_publico(slug, servico_id):

    empresa = Empresa.query.filter_by(slug=slug).first_or_404()

    servico = Servico.query.filter_by(
        id=servico_id,
        empresa_id=empresa.id,
        ativo=True
    ).first_or_404()

    if request.method == "POST":

        email = request.form.get("email")
        telefone = request.form.get("telefone")

        # =================================================
        # CLIENTE
        # =================================================
        cliente = Cliente.query.filter_by(
            telefone=telefone,
            empresa_id=empresa.id
        ).first()

        if cliente and not cliente.nome:
            cliente.nome = f"Cliente {cliente.telefone}"
            db.session.commit()

        if not cliente:
            cliente = Cliente(
                empresa_id=empresa.id,
                nome=f"Cliente {telefone}",
                email=email,
                telefone=telefone
            )
            db.session.add(cliente)
            db.session.commit()


        # =================================================
        # VENDEDOR SISTEMA
        # =================================================
        vendedor = Usuario.query.filter_by(
            empresa_id=empresa.id,
            tipo="sistema",
            nome="Mercado Pago"
        ).first()

        if not vendedor:
            senha_fake = secrets.token_urlsafe(32)

            vendedor = Usuario(
                nome="Mercado Pago",
                tipo="sistema",
                empresa_id=empresa.id,
                email=f"gateway@{empresa.slug}.local",
                senha_hash=generate_password_hash(senha_fake),
                is_master=False,
                is_admin_empresa=False
            )
            db.session.add(vendedor)
            db.session.commit()

        # =================================================
        # CRIA VENDA (ANTES DE QUALQUER PAGAMENTO)
        # =================================================
        valor_venda = servico.valor_venda_padrao
        taxa_gateway = (valor_venda * Decimal("0.01")).quantize(Decimal("0.01"))

        venda = VendaStreaming(
            empresa_id=empresa.id,
            cliente_id=cliente.id,
            servico_id=servico.id,
            vendedor_id=vendedor.id,          # 👈 AGORA SALVA
            valor_venda=valor_venda,
            valor_comissao=taxa_gateway,      # 👈 AGORA SALVA
            status="AGUARDANDO_PAGAMENTO",
            email_entrega=email
        )
        db.session.add(venda)
        db.session.commit()

        # =================================================
        # TOKEN PÚBLICO DA VENDA
        # =================================================
        token = VendaTokenAcesso(
            venda_id=venda.id,
            token=secrets.token_urlsafe(32)
        )
        db.session.add(token)
        db.session.commit()

        # =================================================
        # PAGAMENTO
        # =================================================
        mp = MercadoPagoClient(empresa.id)

        pagamento = mp.criar_pagamento(
            valor=venda.valor_venda,
            descricao=f"{servico.nome}",
            email=email
        )

        venda.pagamento_id = str(pagamento["id"])
        venda.pagamento_status = pagamento["status"]
        venda.metodo_pagamento = "pix"
        db.session.commit()

        pix = pagamento["point_of_interaction"]["transaction_data"]

        venda.pix_qr_code = pix["qr_code"]
        venda.pix_qr_code_base64 = pix["qr_code_base64"]

        db.session.commit()


        # =================================================
        # REDIRECIONA PARA PÁGINA DO PEDIDO (TOKEN)
        # =================================================
        return redirect(
            url_for(
                "public.status_venda",
                token=token.token
            )
        )

    return render_template(
        "checkout.html",
        empresa=empresa,
        servico=servico
    )



from app.models import Servico, Conta, Tela, Empresa

@bp_public.route("/<slug>")
def vendas_publicas(slug):

    empresa = Empresa.query.filter_by(slug=slug).first_or_404()

    servicos = (
        Servico.query
        .filter_by(empresa_id=empresa.id, ativo=True)
        .order_by(Servico.nome)
        .all()
    )

    dados = []

    for servico in servicos:

        livres = (
            Tela.query
            .join(Conta)
            .filter(
                Conta.servico_id == servico.id,
                Conta.ativa == True,
                Tela.vendida == False
            )
            .count()
        )

        vendidas = (
            Tela.query
            .join(Conta)
            .filter(
                Conta.servico_id == servico.id,
                Tela.vendida == True
            )
            .count()
        )

        dados.append({
            "servico": servico,
            "livres": livres,
            "vendidas": vendidas
        })

    return render_template(
        "public/vendas_servicos.html",
        empresa=empresa,
        dados=dados
    )


@bp_public.route("/pedido/<token>")
def status_venda(token):

    venda_token = (
        VendaTokenAcesso.query
        .filter_by(token=token)
        .first_or_404()
    )

    venda = VendaStreaming.query.get_or_404(venda_token.venda_id)

    return render_template(
        "public/status_venda.html",
        venda=venda
    )
