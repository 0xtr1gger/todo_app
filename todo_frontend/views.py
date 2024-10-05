import cgitb


from flask import Blueprint, request, flash, render_template, redirect, jsonify
import requests
import json

from forms import RegistrationForm, LoginForm, TaskForm

import base64

todo_view = Blueprint('todo_view', __name__)


def check_if_authorized(request_object):
    print('check_if_authorized() function is invoked')
    is_authorized = False
    user_id = None
    try:
        # get the JWT from the cookie
        access_token = request_object.cookies.get('sessionid')
        components = access_token.split('.')
        print('token is retrieved:\n')
        for component in components:
            print(base64.b64decode(component).decode("utf-8"))

        # check if token is present. if not, the user is not authorized
        if not access_token:
            result = {'message': 'No access token is provided.', 'is_authorized': is_authorized, 'user_id': user_id}
            return json.dumps(result)

        # send the JWT to the backend for verification
        response = requests.post('http://localhost:5001/api/auth/verify_jwt', json={'JWT': access_token})

        # if response is 201, this means the token is valid, and the user_id is returned
        if response.ok:
            is_authorized = True
            user_id = response.json().get('user_id')
            result = {'message': 'User is successfully authorized.', 'is_authorized': is_authorized, 'user_id': user_id}
            return json.dumps(result)

        # otherwise, the error message is issued
        else:
            result = {'message': 'Invalid authentication token.', 'is_authorized': is_authorized, 'user_id': user_id}
            return json.dumps(result)

    # if something goes wrong, such that a cookie is not present, return an error message
    except Exception as e:
        print(f'Error: {e}')
        return json.dumps({'message': f'Error: {e}'})



@todo_view.route('/', methods=['GET'])
@todo_view.route('/tasks', methods=['GET', 'POST'])
def home():
    task_form = TaskForm()
    # get the JWT
    access_token = request.cookies.get('sessionid')
    print(access_token)
    # if not authorized, redirect to the /login page
    if not access_token:
        return redirect('/login')

    tasks_response = requests.get('http://localhost:5001/api/tasks/get_tasks', json={'access_token': access_token})

    if tasks_response.ok:
        tasks = tasks_response.json()
        print(tasks)
        return render_template(
            'tasks.html',
            form=task_form,
            tasks=tasks
        )

    # the add_task form is submitted
    if request.method == 'POST':
        if task_form.validate_on_submit():

            # obtain task data form the form sent by the user
            form_data = {
                'title': task_form.title.data
            }
            description = task_form.description.data
            if description:
                form_data['description'] = description
            deadline = task_form.deadline.data
            if deadline:
                form_data['deadline'] = json.dumps(deadline.isoformat())
            print(form_data)

            # append the JWT for validation and to extract the User ID
            form_data['access_token'] = access_token

            add_task_api_response = requests.post('http://localhost:5001/api/tasks/add_task', json=form_data)
            if add_task_api_response.ok:
                print('Task created successfully.')
                flash('Task created successfully!')
                redirect('/')
            else:
                print(add_task_api_response.json().get('message'))
                flash('Error creating a task.')

    return render_template(
        'tasks.html',
        form=task_form
    )

@todo_view.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):

    pass

"""context = {}
result = json.loads(check_if_authorized(request))
context = {
    'is_authorized': result.get('is_authorized'),
    'user_id': result.get('user_id')
}"""

@todo_view.route('/register', methods=['GET', 'POST'])
def register():
    registration_form = RegistrationForm()
    if request.method == 'POST':
        if registration_form.validate_on_submit():
            registration_data = {
                'username': registration_form.username.data,
                'email': registration_form.email.data,
                'password': registration_form.password.data
            }

            response = requests.post('http://localhost:5001/api/auth/register', json=registration_data)
            if response.ok:
                print(registration_data)
                flash('Registration successful!', 'success')
            elif response.status_code == 409:
                error_message = response.json().get('message')
                flash(error_message, 'error')
            else:
                print('something went wrong')
    return render_template(
        'register.html',
        form=registration_form
    )

@todo_view.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if request.method == 'POST':
        if login_form.validate_on_submit():
            login_data = {
                'email': login_form.email.data,
                'password': login_form.password.data
            }

            login_response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
            if login_response.ok:
                # if /api/auth/login responds with 201, it returns: 1. authentication token (JWT)
                flash('Login successful!', 'success')

                # extract the JWT from response
                auth_token = login_response.json().get('auth_token')
                # redirect to home
                response = redirect('/')
                # set the sessionid cookie that will hold the JWT
                response.set_cookie('sessionid', auth_token, max_age=24 * 60 * 60)  # 1 day

                #user_id = login_response.json().get('user_id')
                #login_user(user_object)
                print(f'Login successful!')
                print(login_data)

                return response

            #elif response.status_code == 404 or 401:
            #    error_message = response.json().get('message')
            #    flash(error_message, 'error')
            else:
                error_message = login_response.json().get('message')
                flash(error_message, 'error')
                print('Something went wrong')
    return render_template(
        'login.html',
        form=login_form
    )

@todo_view.route('/logout')
def logout():
    access_token = request.cookies.get('sessionid')
    # if token does not exist or is empty, this means the user is not logged in
    if not access_token:
        return redirect('/login')
    # otherwise, send the token to backend for invalidation
    print(access_token)
    invalidate_jwt_response = requests.post('http://localhost:5001/api/auth/invalidate_jwt', json={'access_token': access_token})
    if invalidate_jwt_response.ok:
        response = redirect('/')
        response.set_cookie('sessionid', '', expires=0)
        return response
    else:
        print(invalidate_jwt_response.json().get('message'))
        return redirect('/login')