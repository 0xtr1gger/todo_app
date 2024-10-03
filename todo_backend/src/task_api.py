from flask import Blueprint, request, jsonify
import datetime
import jwt

from .models import User
from . import db

SECRET_KEY = 'demo'

task_blueprint = Blueprint('task_view', __name__)

