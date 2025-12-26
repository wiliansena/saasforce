from flask_login import current_user
from app import db

class EmpresaQueryMixin:
    @classmethod
    def query_empresa(cls):
        """
        Query sempre filtrada pela empresa do usuário logado
        """
        if not current_user.is_authenticated:
            # segurança extra
            return cls.query.filter(db.text("1=0"))

        return cls.query.filter_by(
            empresa_id=current_user.empresa_id
        )
