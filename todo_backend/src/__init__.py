from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_backend():
    backend_app = Flask(__name__)

    backend_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://yourusername:yourpassword@localhost:5432/yourdatabase'
    backend_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    backend_app.config['SECRET_KEY'] = 'secret_key'


    db.init_app(backend_app)
    migrate.init_app(backend_app, db)

    from .auth_api import auth_blueprint
    backend_app.register_blueprint(auth_blueprint, url_prefix='/api/auth/')

    from .task_api import task_blueprint
    backend_app.register_blueprint(task_blueprint, url_prefix='/api/tasks/')

    return backend_app

backend = create_backend()
