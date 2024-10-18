from flask import Blueprint

book = Blueprint('book', __name__)

from . import controller