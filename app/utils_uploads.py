import os
from flask import current_app
from werkzeug.utils import secure_filename
from flask_login import current_user

def salvar_upload(
    arquivo,
    subpasta: str,
    nome_forcado: str | None = None
):
    """
    Salva upload isolado por empresa.

    Ex:
    salvar_upload(file, "servicos")
    salvar_upload(file, "logos", "logo.png")
    """

    if not arquivo:
        return None

    empresa_id = current_user.empresa_id

    # caminho: uploads/empresas/<empresa_id>/<subpasta>
    base_path = os.path.join(
        current_app.config["UPLOAD_ROOT"],
        "empresas",
        str(empresa_id),
        subpasta
    )

    os.makedirs(base_path, exist_ok=True)

    filename = (
        secure_filename(nome_forcado)
        if nome_forcado
        else secure_filename(arquivo.filename)
    )

    caminho_final = os.path.join(base_path, filename)
    arquivo.save(caminho_final)

    # caminho relativo salvo no banco
    return f"uploads/empresas/{empresa_id}/{subpasta}/{filename}"
