from flask import Blueprint

analytics = Blueprint('analytics', __name__)

from . import controller