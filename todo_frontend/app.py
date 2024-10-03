import flask
from flask import Flask, request, render_template
import os
from flask_cors import CORS
import requests


cors = CORS()

def create_app():

    app = Flask(__name__, template_folder='./templates')
    app.config['SECRET_KEY'] = 'demo'

    app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_ACCESS_COOKIE_NAME'] = ['sessionid']
    app.config['JWT_ENABLE_CSRF'] = False

    #app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    #app.config['JWT_CSRF_CHECK_FORM'] = True

    #app.config['JWT_ACCESS_CSRF_HEADER_NAME'] = 'X-CSRF-Token'
    #app.config['JWT_ACCESS_CSFR_FIELD_NAME'] = 'csrf_token'

    #login_manager.init_app(app)

    from views import todo_view
    app.register_blueprint(todo_view, url_prefix='/')

    cors.init_app(app, resources={
        r'/*': {"origins": ["http://localhost:5000", "http://localhost:5001"]}
    })

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'Server has started on port {port}...')
    app.run(host='0.0.0.0', port=port, debug=True)