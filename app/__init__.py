from datetime import timedelta
import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, logout_user, current_user
from config import Config
from flask_mail import Mail   # <-- NOVO

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()
mail = Mail()                 # <-- NOVO

def create_app():

    app = Flask(__name__)
    # Torna o getattr disponível nos templates Jinja2
    app.jinja_env.globals.update(getattr=getattr)

    #regitro de filtros no utils.py
    # ✅ Registro dos filtros personalizados
    from app.utils import registrar_filtros_jinja
    registrar_filtros_jinja(app)
    

    app.config.from_object(Config)  # Carrega as configurações do config.py

    # 🔹 Configuração do tempo de sessão
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

    # 🔹 Inicialização do banco de dados
    db.init_app(app)
    migrate.init_app(app, db)
    # 🔹 INICIALIZAÇÃO DO E-MAIL
    mail.init_app(app)   # <-- NOVO

    # 🔹 Injeta a licença em todos os templates (para usar {{ licenca... }} no Jinja)
    @app.context_processor
    def inject_licenca_sistema():
        try:
            # import local para evitar import circular
            from app.models import LicencaSistema
            licenca = LicencaSistema.query.order_by(LicencaSistema.id.desc()).first()
        except Exception:
            # Se a tabela ainda não existe (antes de rodar as migrações), não quebra o template
            licenca = None
        return dict(licenca=licenca)


    # 🔹 Proteção CSRF
    csrf.init_app(app)

    # 🔹 Garante existência da raiz de uploads (multiempresa)
    upload_root = app.config.get("UPLOAD_ROOT")

    if upload_root and not os.path.exists(upload_root):
        os.makedirs(upload_root)


    # 🔹 Configuração do Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Você precisa estar logado para acessar esta página."

    @login_manager.user_loader
    def load_user(user_id):
        """Carrega o usuário ao fazer login e garante que as permissões são carregadas corretamente."""
        from app.models import Usuario  # Importação dentro da função para evitar problemas de importação circular
        usuario = Usuario.query.get(int(user_id))
        
        if usuario:
            _ = usuario.todas_permissoes  # 🔹 Garante que as permissões são carregadas corretamente
        
        return usuario

    # 🔹 Antes de cada requisição, manter a sessão ativa e garantir permissões
    @app.before_request
    def verificar_sessao():
        if current_user.is_authenticated:
            session.permanent = True
            session.modified = True
            
            # 🔹 Garante que as permissões estão carregadas corretamente no usuário
            _ = current_user.todas_permissoes
        else:
            logout_user()

    # 🔹 Importação de Blueprints (módulos de rotas)
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    from app.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.master.routes import bp as master_bp
    app.register_blueprint(master_bp, url_prefix='/master')


    return app
