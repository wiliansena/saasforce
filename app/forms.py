
from decimal import Decimal
from typing import Optional
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, DateTimeField, DecimalField, HiddenField, SelectMultipleField, StringField, SubmitField, FloatField, FileField, TextAreaField
from wtforms.validators import DataRequired
from wtforms import SelectField
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, FileField, FieldList, FormField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Email
from datetime import date
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, InputRequired, Length, EqualTo

from flask_wtf import FlaskForm

##### STV #####

class LicencaSistemaForm(FlaskForm):
    dias_acesso = IntegerField("Dias_De_Acesso", validators=[DataRequired()])
    submit = SubmitField("Salvar")

class UsuarioForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=3, max=100)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max=100)])
    email = StringField("E-mail",  validators=[DataRequired(), Email(), Length(max=120)])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha', message='As senhas devem coincidir.')])
    submit = SubmitField('Salvar')


class ServicoForm(FlaskForm):
    nome = StringField("Nome do Serviço", validators=[DataRequired()])
    tipo = SelectField(
        "Tipo",
        choices=[
            ("compartilhado", "Compartilhado"),
            ("individual", "Individual"),
        ],validators=[DataRequired()])
    telas_total = IntegerField("Total de Telas", validators=[Optional(), NumberRange(min=1)])
    valor_venda_padrao = DecimalField("Valor Venda Padrão", places=2, validators=[InputRequired()])
    comissao_padrao = DecimalField("Comissão padrão", places=2, validators=[InputRequired()])
    ativo = BooleanField("Ativo")
    imagem = FileField("Imagem do Serviço")

class ContaForm(FlaskForm):
    email = StringField("Email da Conta", validators=[DataRequired(), Email()])
    senha = StringField("Senha", validators=[Optional()]) 
    servico_id = SelectField("Serviço", coerce=int, validators=[DataRequired()])
    valor_venda_override = DecimalField("Venda personalizada (Opcional)", places=2, validators=[Optional()])
    comissao_override = DecimalField("Comissão personalizada (Opcional)", places=2, validators=[Optional()])
    valor_investido = DecimalField("Valor Investido", places=4, validators=[InputRequired()])
    ativa = BooleanField("Conta Ativa")

class VendaStreamingForm(FlaskForm):
    telefone = StringField("Telefone do Cliente", validators=[DataRequired()])
