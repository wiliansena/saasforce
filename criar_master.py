from app import create_app, db
from app.models import Usuario

app = create_app()

with app.app_context():
    db.create_all()

    # =====================================================
    # 👑 USUÁRIO MASTER (ROOT)
    # =====================================================
    master_email = "wilian.sennah@gmail.com"

    master = Usuario.query.filter_by(
        is_master=True
    ).first()

    if not master:
        master = Usuario(
            nome="wilian",
            email=master_email,
            is_master=True,
            is_admin_empresa=True,
            empresa_id=None   # 🔒 MASTER NÃO TEM EMPRESA
        )
        master.set_password("Fkj7byqH")

        db.session.add(master)
        db.session.commit()

        print("✅ Usuário MASTER criado com sucesso")
        print("   Login:", master_email)
        print("   Senha: Fkj7byqH")

    else:
        # 🔧 garante que o master tenha email
        if not master.email:
            master.email = master_email
            db.session.commit()
            print("⚠️ Usuário MASTER já existia, email foi ajustado")

        print("ℹ️ Usuário MASTER já existe. Nenhuma ação necessária.")
