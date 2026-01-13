from flask import Blueprint, request, jsonify
from decimal import Decimal
from app import db
from app.models import VendaStreaming, Conta, Tela
from app.services.pagamento.mercadopago_client import MercadoPagoClient
from app.utils_datetime import utc_now
from app import csrf
from app.services.email_service import send_email

bp_webhook = Blueprint("webhook", __name__)


@bp_webhook.route("/webhook/mercadopago", methods=["POST"])
@csrf.exempt
def webhook_mercadopago():
    print(">>> WEBHOOK MERCADO PAGO ATINGIDO <<<")

    data = request.get_json(silent=True) or {}

    if data.get("type") != "payment":
        return jsonify({"status": "ignored"}), 200

    pagamento_id = data.get("data", {}).get("id")
    if not pagamento_id:
        return jsonify({"error": "payment id missing"}), 400


    venda = (
        VendaStreaming.query
        .filter_by(pagamento_id=str(pagamento_id))
        .with_for_update()
        .first()
    )

    # 🔒 PRIMEIRO: venda existe?
    if not venda:
        return jsonify({"status": "venda not found"}), 200

    # 🔒 DEPOIS: idempotência
    if venda.status in ("ENTREGUE", "PAGO"):
        return jsonify({"status": "already processed"}), 200


    mp = MercadoPagoClient(venda.empresa_id)
    pagamento = mp.consultar_pagamento(pagamento_id)

    status_mp = pagamento.get("status")
    valor_pago = Decimal(str(pagamento.get("transaction_amount", 0)))

    if status_mp != "approved":
        venda.pagamento_status = status_mp
        db.session.commit()
        return jsonify({"status": "not approved"}), 200

    if valor_pago != venda.valor_venda:
        return jsonify({"error": "valor divergente"}), 400

    venda.pagamento_status = status_mp
    venda.valor_pago = valor_pago
    venda.pago_em = utc_now()
    venda.status = "PAGO"

    tela = (
        Tela.query
        .join(Conta)
        .filter(
            Conta.servico_id == venda.servico_id,
            Conta.ativa == True,
            Tela.vendida == False
        )
        .with_for_update()
        .first()
    )

    if not tela:
        venda.status = "CANCELADA"
        db.session.commit()
        return jsonify({"error": "sem estoque"}), 409

    tela.vendida = True
    venda.tela_id = tela.id

    venda.status = "ENTREGUE"
    venda.data_entrega = utc_now()

        # ==============================
    # ENVIO DE E-MAIL (AQUI É O LUGAR CERTO)
    # ==============================
    conta = venda.tela.conta

    send_email(
        to=venda.email_entrega,
        subject=f"Acesso liberado - {venda.servico.nome}",
        body=f"""
        Olá!

        Seu pagamento foi confirmado com sucesso.

        Serviço: {venda.servico.nome}
        Login: {conta.email}
        Senha: {conta.senha}

        Qualquer dúvida, estamos à disposição.
        """
    )

    db.session.commit()

    return jsonify({"status": "entregue"}), 200
