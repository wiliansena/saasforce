import requests
import uuid

from app.models import EmpresaPagamentoConfig
from app.services.pagamento.exceptions import (
    PagamentoConfigNotFound,
    PagamentoRequestError
)

MP_BASE_URL = "https://api.mercadopago.com"


class MercadoPagoClient:
    """
    Mercado Pago Client
    TESTE      -> Cartão de teste
    PRODUÇÃO   -> PIX
    """

    def __init__(self, empresa_id: int):
        self.config = self._carregar_config(empresa_id)
        self.token = self.config.access_token

        self.is_teste = self.token.startswith("TEST-")

    # =====================================================
    # CONFIG
    # =====================================================
    def _carregar_config(self, empresa_id):
        config = (
            EmpresaPagamentoConfig.query
            .filter_by(
                empresa_id=empresa_id,
                ativo=True,
                gateway="mercadopago"
            )
            .first()
        )

        if not config:
            raise PagamentoConfigNotFound(
                "Empresa sem configuração ativa do Mercado Pago."
            )

        return config

    # =====================================================
    # HEADERS (SEMPRE NOVOS)
    # =====================================================
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": str(uuid.uuid4())
        }

    # =====================================================
    # API PÚBLICA
    # =====================================================
    def criar_pagamento(self, *, valor, descricao, email):
        if self.is_teste:
            return self._criar_pagamento_cartao_teste(
                valor=valor,
                descricao=descricao,
                email=email
            )

        return self._criar_pagamento_pix(
            valor=valor,
            descricao=descricao,
            email=email
        )

    def consultar_pagamento(self, pagamento_id):
        response = requests.get(
            f"{MP_BASE_URL}/v1/payments/{pagamento_id}",
            headers=self._headers(),
            timeout=20
        )

        if response.status_code != 200:
            raise PagamentoRequestError(
                f"Erro consulta Mercado Pago: {response.text}"
            )

        return response.json()

    # =====================================================
    # TESTE → CARTÃO
    # =====================================================
    def _criar_pagamento_cartao_teste(self, *, valor, descricao, email):

        token_cartao = self._gerar_token_cartao_teste()

        payload = {
            "transaction_amount": float(valor),
            "token": token_cartao,
            "description": descricao,
            "installments": 1,
            "payment_method_id": "visa",
            "payer": {
                "email": email
            },
            "statement_descriptor": "SAASFX TESTE"
        }

        response = requests.post(
            f"{MP_BASE_URL}/v1/payments",
            json=payload,
            headers=self._headers(),
            timeout=20
        )

        if response.status_code not in (200, 201):
            raise PagamentoRequestError(
                f"Erro pagamento cartão (teste): {response.text}"
            )

        return response.json()

    def _gerar_token_cartao_teste(self):

        payload = {
            "card_number": "4235647728025682",
            "expiration_month": 11,
            "expiration_year": 2030,
            "security_code": "123",
            "cardholder": {
                "name": "APRO"
            }
        }

        response = requests.post(
            f"{MP_BASE_URL}/v1/card_tokens",
            json=payload,
            headers=self._headers(),
            timeout=20
        )

        if response.status_code != 201:
            raise PagamentoRequestError(
                f"Erro token cartão: {response.text}"
            )

        return response.json()["id"]

    # =====================================================
    # PRODUÇÃO → PIX
    # =====================================================
    def _criar_pagamento_pix(self, *, valor, descricao, email):

        payload = {
            "transaction_amount": float(valor),
            "description": descricao,
            "payment_method_id": "pix",
            "payer": {
                "email": email
            }
        }

        response = requests.post(
            f"{MP_BASE_URL}/v1/payments",
            json=payload,
            headers=self._headers(),
            timeout=20
        )

        if response.status_code not in (200, 201):
            raise PagamentoRequestError(
                f"Erro pagamento PIX: {response.text}"
            )

        return response.json()
