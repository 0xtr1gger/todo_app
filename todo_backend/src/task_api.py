import crypt

from flask import Blueprint, request, jsonify
from datetime import datetime
import jwt

from .auth_api import decode_jwt

from .models import User, Task
from . import db

SECRET_KEY = 'demo'

task_blueprint = Blueprint('task_view', __name__)

@task_blueprint.route('get_tasks')
def get_tasks():
    task_list = []
    form_data = request.get_json()
    access_token = form_data.get('access_token') # get the access token from the dictionary
    user_id = decode_jwt(access_token)

    print(f'JWT decoded; user_id = {user_id}')
    if isinstance(user_id, int):
        try:
            tasks = db.session.query(Task).filter_by(user_id=user_id).all()

            task_list = [
                {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'deadline':  task.deadline.strftime("%d.%m.%Y") if task.deadline else None, #task.deadline.isoformat() if task.deadline else None,
                    'completed': task.completed
                } for task in tasks
            ]
            print(task_list)
            return jsonify(task_list), 201
        except Exception as e:
            print(f'Error: {e}')
        return jsonify({'message': 'Error retrieving tasks.'}), 404
    else:
        print('Invalid access token.')
        return jsonify({'message': 'Invalid access token.'}), 403


@task_blueprint.route('add_task', methods=['POST'])
def add_task():
    form_data = request.get_json()
    access_token = form_data.get('access_token') # get the access token from the dictionary

    user_id = decode_jwt(access_token)

    if isinstance(user_id, int):
        try:
            new_task = Task(
                title = form_data.get('title'),
                description = form_data.get('description'),
                deadline = form_data.get('deadline'),
                user_id  = user_id
            )
            db.session.add(new_task)
            db.session.commit()
            print(f'Successfully created a task: {new_task.title}')
            return jsonify({'message': 'Task added successfully!'}), 201 #, 'task_id': new_task.id}), 201
        except Exception as e:
            print(f'Error: {e}')
    else:
        return jsonify({'message': 'Invalid access token.'}), 403

