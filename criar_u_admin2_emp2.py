from datetime import date

from app import create_app, db
from app.models import Empresa, Usuario, Permissao, LicencaSistema

app = create_app()

with app.app_context():
    db.create_all()
    # =====================================================
    # 2️⃣ USUÁRIO ADMIN_MASTER
    # =====================================================
    admin_master = Usuario(
        nome="root",
        is_master=True
    )
    admin_master.set_password("root123")
        db.session.add(admin_master)
        db.session.flush()  # garante admin.id
        print("✅ Usuário MASTER (root) criado com sucesso!")