from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Length


class NovaEmpresaForm(FlaskForm):
    nome = StringField(
        "Nome da Empresa",
        validators=[DataRequired(), Length(max=120)]
    )

    admin_nome = StringField(
        "Usuário Admin",
        validators=[DataRequired(), Length(max=50)]
    )

    admin_senha = PasswordField(
        "Senha do Admin",
        validators=[DataRequired(), Length(min=6)]
    )

    dias_licenca = IntegerField(
        "Dias de Licença",
        default=30
    )
