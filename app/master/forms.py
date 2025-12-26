from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, Length

class NovaEmpresaForm(FlaskForm):
    nome = StringField(
        "Nome da Empresa",
        validators=[DataRequired(), Length(max=120)]
    )

    admin_nome = StringField(
        "Nome do Administrador",
        validators=[DataRequired(), Length(max=120)]
    )

    admin_email = StringField(
        "E-mail do Administrador",
        validators=[DataRequired(), Email(), Length(max=120)]
    )

    admin_senha = PasswordField(
        "Senha do Administrador",
        validators=[DataRequired(), Length(min=6)]
    )

    dias_licenca = IntegerField("Dias de Licença")