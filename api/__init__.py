from flask import Blueprint
from flask_cors import CORS

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
CORS(api_bp)

from .auth import *
from .projects import *
from .users import *
from .analytics import *
from .files import *
from .notifications import *

