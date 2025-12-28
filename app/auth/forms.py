from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):

    email = StringField(
        "E-mail",
        validators=[DataRequired(), Email()]
    )

    senha = PasswordField(
        "Senha",
        validators=[DataRequired()]
    )

    submit = SubmitField("Entrar")


from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp

class TrocarSenhaForm(FlaskForm):
    senha_atual = PasswordField("Senha Atual", validators=[DataRequired()])
    nova_senha = PasswordField("Nova Senha", validators=[
        DataRequired(),
        Length(min=6, message="A senha deve ter pelo menos 6 caracteres."),
        Regexp(r'.*[A-Z]', message="A senha deve conter pelo menos uma letra maiúscula."),
        Regexp(r'.*[a-z]', message="A senha deve conter pelo menos uma letra minúscula."),
        Regexp(r'.*\d', message="A senha deve conter pelo menos um número."),
#       Regexp(r'.*[\W_]', message="A senha deve conter pelo menos um símbolo (!@#$%^&*...).")
    ])
    confirmar_senha = PasswordField("Confirmar Nova Senha", validators=[
        DataRequired(),
        EqualTo('nova_senha', message="As senhas não coincidem.")
    ])
    submit = SubmitField("Alterar Senha")



class AdminAlterarSenhaForm(FlaskForm):
    nova_senha = PasswordField("Nova Senha", validators=[
        DataRequired(),
        Length(min=8, message="A senha deve ter pelo menos 8 caracteres."),
        Regexp(r'.*[A-Z]', message="A senha deve conter pelo menos uma letra maiúscula."),
        Regexp(r'.*[a-z]', message="A senha deve conter pelo menos uma letra minúscula."),
        Regexp(r'.*\d', message="A senha deve conter pelo menos um número."),
    #    Regexp(r'.*[\W_]', message="A senha deve conter pelo menos um símbolo.")
    ])
    confirmar_senha = PasswordField("Confirmar Nova Senha", validators=[
        DataRequired(),
        EqualTo('nova_senha', message="As senhas não coincidem.")
    ])
    submit = SubmitField("Alterar Senha")

