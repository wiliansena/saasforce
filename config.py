from datetime import timedelta
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print(f"⚠️ Arquivo .env não encontrado no caminho: {dotenv_path}")

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave-secreta-padrao')

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:Wskj7byqH@localhost/saasforce'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")


    # ==========================
    # 📁 UPLOADS (MULTIEMPRESA)
    # ==========================
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # raiz única de uploads
    UPLOAD_ROOT = os.path.join(BASE_DIR, 'app', 'static', 'uploads')

    # extensões permitidas (excel, csv etc.)
    ALLOWED_EXTENSIONS = {"xls", "xlsx", "csv", "png", "jpg", "jpeg", "webp"}

    # garante que a pasta exista
    os.makedirs(UPLOAD_ROOT, exist_ok=True)

    # ==========================
    # 🔐 SEGURANÇA
    # ==========================
    WTF_CSRF_ENABLED = True

    # ==========================
    # ✉️ EMAIL
    # ==========================
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "enviiiosonlinee@gmail.com"
    MAIL_PASSWORD = "ujrn weul ockt ecsi"  # app password
    MAIL_DEFAULT_SENDER = (
        "VENDAS - ",
        "enviiiosonlinee@gmail.com"
    )

    ALERTA_RFM_EMAIL = "enviiiosonlinee@gmail.com"
