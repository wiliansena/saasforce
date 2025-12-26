from app import create_app, db
from app.models import Usuario

app = create_app()

with app.app_context():
    db.create_all()

    # =====================================================
    # 👑 USUÁRIO MASTER (ROOT)
    # =====================================================
    master = Usuario.query.filter_by(
        nome="root",
        is_master=True
    ).first()

    if not master:
        master = Usuario(
            nome="root",
            is_master=True,
            is_admin_empresa=True,
            empresa_id=None   # 🔒 MASTER NÃO TEM EMPRESA
        )

        master.set_password("root123")

        db.session.add(master)
        db.session.commit()

        print("✅ Usuário MASTER criado com sucesso")
        print("   Login: root")
        print("   Senha: Fkj7byqH")
    else:
        print("ℹ️ Usuário MASTER já existe. Nenhuma ação necessária.")

