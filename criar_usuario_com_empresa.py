from datetime import date

from app import create_app, db
from app.models import Empresa, Usuario, Permissao, LicencaSistema

app = create_app()

with app.app_context():
    db.create_all()

    # =====================================================
    # 1️⃣ EMPRESA
    # =====================================================
    empresa = Empresa.query.filter_by(nome="stvhd").first()

    if not empresa:
        empresa = Empresa(
            nome="stvhd",
            ativa=True
        )
        db.session.add(empresa)
        db.session.flush()  # garante empresa.id
        print("✅ Empresa criada:", empresa.nome)
    else:
        print("ℹ️ Empresa já existe:", empresa.nome)

    # =====================================================
    # 2️⃣ USUÁRIO ADMIN
    # =====================================================
    admin = Usuario.query.filter_by(
        nome="admin",
        empresa_id=empresa.id
    ).first()

    if not admin:
        admin = Usuario(
            nome="admin",
            empresa_id=empresa.id
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.flush()  # garante admin.id
        print("✅ Usuário admin criado (empresa vinculada)")
    else:
        print("ℹ️ Usuário admin já existe para esta empresa")

    # =====================================================
    # 3️⃣ LICENÇA DA EMPRESA
    # =====================================================
    licenca = LicencaSistema.query.filter_by(
        empresa_id=empresa.id
    ).first()

    if not licenca:
        licenca = LicencaSistema(
            empresa_id=empresa.id,
            data_inicio=date.today(),
            dias_acesso=30
        )
        db.session.add(licenca)
        print("✅ Licença criada (30 dias)")
    else:
        print("ℹ️ Licença já existe para esta empresa")

    # =====================================================
    # 4️⃣ PERMISSÕES DO ADMIN
    # =====================================================
    permissoes = [
        ('usuarios', 'ver'), ('usuarios', 'editar'), ('usuarios', 'excluir'), ('usuarios', 'criar'),
        ('referencias', 'ver'), ('referencias', 'editar'), ('referencias', 'excluir'), ('referencias', 'criar'),
        ('controleproducao', 'ver'), ('controleproducao', 'editar'), ('controleproducao', 'excluir'), ('controleproducao', 'criar'),
        ('desenvolvimento', 'ver'), ('desenvolvimento', 'editar'), ('desenvolvimento', 'excluir'), ('desenvolvimento', 'criar'),
        ('margens', 'ver'), ('margens', 'editar'), ('margens', 'criar'), ('margens', 'excluir'),
        ('trocar_senha', 'editar'),
        ('administracao', 'ver'), ('administracao', 'editar')
    ]

    for categoria, acao in permissoes:
        existe = Permissao.query.filter_by(
            empresa_id=empresa.id,
            usuario_id=admin.id,
            categoria=categoria,
            acao=acao
        ).first()

        if not existe:
            p = Permissao(
                empresa_id=empresa.id,
                usuario_id=admin.id,
                categoria=categoria,
                acao=acao
            )
            db.session.add(p)

    db.session.commit()
    print("✅ Permissões atribuídas ao usuário admin.")
