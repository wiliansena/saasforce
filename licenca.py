from app import create_app, db
from app.models.licenca_sistema import LicencaSistema
from datetime import date

app = create_app()

with app.app_context():
    licenca = LicencaSistema(data_inicio=date.today(), dias_acesso=1)
    db.session.add(licenca)
    db.session.commit()
    print("✅ Licença criada com sucesso!")
