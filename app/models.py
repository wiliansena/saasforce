from decimal import Decimal
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from app import db
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
from datetime import datetime
from sqlalchemy.orm import backref
from app.mixins import EmpresaQueryMixin
from app.utils_datetime import utc_now

from datetime import date, timedelta

 ####   USUÁRIO    ######
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Empresa(db.Model):
    __tablename__ = "empresa"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=True)

    ativa = db.Column(db.Boolean, default=True)
    criada_em = db.Column(db.DateTime, default=utc_now)


class Usuario(UserMixin, EmpresaQueryMixin,db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey("empresa.id"),
        nullable=True   # 👈 MASTER NÃO TEM EMPRESA
    )

    empresa = db.relationship(
        "Empresa",
        backref="usuarios"
    )

    is_master = db.Column(db.Boolean, default=False)  # 👈 CHAVE DO PAINEL MASTER
    is_admin_empresa = db.Column(db.Boolean, default=False)

    nome = db.Column(db.String(100), nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    permissoes = db.relationship(
        "Permissao",
        backref="usuario",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def todas_permissoes(self):
        return {(p.categoria, p.acao) for p in self.permissoes.all()}

    def tem_permissao(self, categoria, acao):
        return (categoria, acao) in self.todas_permissoes

    def pode_trocar_senha(self):
        return self.tem_permissao("trocar_senha", "editar")


class Permissao(EmpresaQueryMixin, db.Model ):
    __tablename__ = "permissao"

    id = db.Column(db.Integer, primary_key=True)

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey("empresa.id"),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=False
    )

    categoria = db.Column(db.String(50), nullable=False)
    acao = db.Column(db.String(20), nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "empresa_id",
            "usuario_id",
            "categoria",
            "acao",
            name="unique_permissao_usuario_empresa"
        ),
    )

class LogAcao(EmpresaQueryMixin, db.Model):
    __tablename__ = "log_acao"

    id = db.Column(db.Integer, primary_key=True)

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey("empresa.id"),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=False
    )

    usuario_nome = db.Column(db.String(100), nullable=False)
    acao = db.Column(db.String(255), nullable=False)

    data_hora = db.Column(
        db.DateTime,
        default=utc_now)

    usuario = db.relationship("Usuario")


class LicencaSistema(EmpresaQueryMixin, db.Model):
    __tablename__ = "licenca_sistema"

    id = db.Column(db.Integer, primary_key=True)

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey("empresa.id"),
        nullable=False
    )
    empresa = db.relationship("Empresa")

    data_inicio = db.Column(db.Date, nullable=False, default=date.today)
    dias_acesso = db.Column(db.Integer, nullable=False, default=1)

    @property
    def data_fim(self):
        return self.data_inicio + timedelta(days=self.dias_acesso)

    @property
    def dias_restantes(self):
        hoje = utc_now().date()
        return max((self.data_fim - hoje).days, 0)

    @property
    def expirado(self):
        return self.dias_restantes <= 0



##### STVHD   ######

class Cliente(EmpresaQueryMixin, db.Model):
    __tablename__ = "cliente"

    id = db.Column(db.Integer, primary_key=True)

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey("empresa.id"),
        nullable=False
    )

    telefone = db.Column(db.String(20), nullable=False)
    nome = db.Column(db.String(120), nullable=True)

    criado_em = db.Column(db.DateTime, default=utc_now)

    vendas = db.relationship(
        "VendaStreaming",
        back_populates="cliente",
        lazy="dynamic"
    )

class Servico(EmpresaQueryMixin, db.Model):
    __tablename__ = "servico"

    id = db.Column(db.Integer, primary_key=True)

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey("empresa.id"),
        nullable=False
    )

    nome = db.Column(db.String(80), nullable=False)
    imagem = db.Column(db.String(200), nullable=True)

    tipo = db.Column(db.String(20), nullable=False)
    # compartilhado | individual

    telas_total = db.Column(db.Integer)
    valor_venda_padrao = db.Column(db.Numeric(10, 2), nullable=False)
    comissao_padrao = db.Column(db.Numeric(10, 2), nullable=False)

    ativo = db.Column(db.Boolean, default=True)

class Conta(EmpresaQueryMixin, db.Model):
    __tablename__ = "conta"

    id = db.Column(db.Integer, primary_key=True)

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey("empresa.id"),
        nullable=False
    )

    email = db.Column(db.String(120), nullable=False)
    senha = db.Column(db.String(120), nullable=True)

    servico_id = db.Column(db.Integer, db.ForeignKey("servico.id"), nullable=False)
    servico = db.relationship("Servico")

    valor_venda_override = db.Column(db.Numeric(10, 2), nullable=True)
    comissao_override = db.Column(db.Numeric(10, 2), nullable=True)
    valor_investido = db.Column(db.Numeric(10, 4), nullable=True)

    ativa = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=utc_now)

    telas = db.relationship(
        "Tela",
        back_populates="conta",
        cascade="all, delete-orphan"
    )

class Tela(EmpresaQueryMixin, db.Model):
    __tablename__ = "tela"

    id = db.Column(db.Integer, primary_key=True)

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey("empresa.id"),
        nullable=False
    )

    conta_id = db.Column(db.Integer, db.ForeignKey("conta.id"), nullable=False)
    conta = db.relationship("Conta", back_populates="telas")

    numero = db.Column(db.Integer, nullable=False)
    vendida = db.Column(db.Boolean, default=False)



class VendaStreaming(EmpresaQueryMixin, db.Model):
    __tablename__ = "venda_streaming"

    id = db.Column(db.Integer, primary_key=True)

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey("empresa.id"),
        nullable=False
    )

    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    cliente = db.relationship("Cliente", back_populates="vendas")

    servico_id = db.Column(db.Integer, db.ForeignKey("servico.id"), nullable=False)
    servico = db.relationship("Servico")

    tela_id = db.Column(db.Integer, db.ForeignKey("tela.id"), nullable=True)
    tela = db.relationship("Tela")

    vendedor_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    vendedor = db.relationship("Usuario")

    valor_venda = db.Column(db.Numeric(10, 2), nullable=False)
    valor_comissao = db.Column(db.Numeric(10, 2), nullable=False)

    status = db.Column(db.String(20), default="PENDENTE")

    data_venda = db.Column(db.DateTime, default=utc_now)
    data_entrega = db.Column(db.DateTime, nullable=True)

