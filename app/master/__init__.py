from flask import Blueprint

bp = Blueprint(
    "master",
    __name__,
    template_folder="templates"
)

from app.master import routes

