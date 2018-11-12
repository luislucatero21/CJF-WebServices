#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, send_from_directory, make_response, send_file, abort
import os, datetime, jwt, welcome_consultas, zipfile
import base64
from flask_cors import CORS
from functools import wraps

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, instance_path=APP_ROOT)
CORS(app)
app.config['SECRET_KEY'] =\
    '\x89\xfb\xb8\xd7\x00\x9ao\xbf\x1f\xd8r\xeb\x8ebJ\x01\x01\xbb\xd4\xab\x1e\x85V\x10\xf3\xcb\x80\xe48\xcf\x03\x92'
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

#COS = welcome_consultas.CosObj()


"""method must stay in this file since we use the request library inorder to check for the token"""


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = None
            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']

            if not token:
                print('no token sent')
                return jsonify(result={'error': 'Token is missing!'}), 401
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithm='RS256')
                # print(data)
                current_user = {'user': data['user'], 'user_type': data['user_type']}
            except:
                print('invalid')
                return jsonify(result={'error': 'Token is invalid!'}), 401
            return f(current_user, *args, **kwargs)
        except Exception as e:
            print('no token')
            return jsonify(result={'error': 'Token Er:'+repr(e)}), 401
    return decorated


# Main route -- Web app is a SPA built with react
@app.route('/')
def Welcome():
    return app.send_static_file('index.html')


@app.route('/login', methods=['POST'])
def login():
    """will only return token if user is valid, else it show two different error messages"""
    # Request paramaters
    email = request.form.get("email")
    password = request.form.get("password")
    de_donde = request.form.get("deDonde")
    # Values must not be empty

    if email is not None and password is not None:
        # function must return value in json otherwise it will be false
        tipo = welcome_consultas.login(email, password, de_donde)
        print("tipo")
        print(tipo)
        if tipo:
            if 'Error' in tipo:
                message = tipo
            else:
                # function returns jwt
                token = welcome_consultas.create_token(email, tipo, app.config['SECRET_KEY'])
                print("token")
                print(token)
                # tipo has a value
                return jsonify(result={'token': token, 'tipo_usuario': tipo[0]['usuario_tipo'], 'cuenta_id': tipo[0]['cuenta_id'], 'nombre': tipo[0]['nombre'], 'region': tipo[0]['region'], 'ciudad': tipo[0]['ciudad']})
        else:
            # tipo is False
            message = 'Correo o contraseña no es correcto'
    else:
        # this will only work for android, since web validates fields before sending
        message = 'No se ingreso correo o contraseña, intenta de nuevo'

    return jsonify(result={'error': message})


@app.route('/get_search', methods=['GET'])
@token_required
def searchables(current_user):

    print(current_user)
    data_set = welcome_consultas.get_searchables(current_user)
    # [{'ID': integer,'TIP' : string,'DETALLE' : string,'RUTA' : string(\TIPS_APP_VER\name_of_file.pdf),
    # 'VERSION_MANUAL': string}]
    if 'Error' in data_set:
        return jsonify(result={'error': data_set})
    else:
        print(data_set)
        return jsonify(result={'data': data_set})

@app.route('/get_request_by_city', methods=['GET'])
@token_required
def get_requests_by_city(current_user):

    print(current_user)
    data_set = welcome_consultas.get_request_by_city(current_user)
    # [{'ID': integer,'TIP' : string,'DETALLE' : string,'RUTA' : string(\TIPS_APP_VER\name_of_file.pdf),
    # 'VERSION_MANUAL': string}]
    if 'Error' in data_set:
        return jsonify(result={'error': data_set})
    else:
        print(data_set)
        return jsonify(result={'data': data_set})

@app.route('/get_news', methods=['GET'])
@token_required
def get_news(current_user):

    data_set = welcome_consultas.get_news()
    # [{'ID': integer,'TIP' : string,'DETALLE' : string,'RUTA' : string(\TIPS_APP_VER\name_of_file.pdf),
    # 'VERSION_MANUAL': string}]
    if 'Error' in data_set:
        return jsonify(result={'error': data_set})
    else:
        print(data_set)
        return jsonify(result={'data': data_set})

@app.route('/get_contacts', methods=['GET'])
@token_required
def get_contacts(current_user):

    data_set = welcome_consultas.get_contacts(current_user)
    # [{'ID': integer,'TIP' : string,'DETALLE' : string,'RUTA' : string(\TIPS_APP_VER\name_of_file.pdf),
    # 'VERSION_MANUAL': string}]
    if 'Error' in data_set:
        return jsonify(result={'error': data_set})
    else:
        print(data_set)
        return jsonify(result={'data': data_set})


@app.route('/get_requests_by_user', methods=['GET'])
@token_required
def getRequestsByUser(current_user):

    data_set = welcome_consultas.get_requests_by_user(current_user['user'])
    if 'Error' in data_set:
        return jsonify(result={'error': data_set})
    else:
        print(data_set)
        return jsonify(result={'data': data_set})

@app.route('/get_requests_by_region', methods=['GET'])
@token_required
def getRequestsByRegion(current_user):

    print('current_user:')
    print(current_user)
    data_set = welcome_consultas.get_request_by_region(current_user)
    if 'Error' in data_set:
        return jsonify(result={'error': data_set})
    else:
        print(data_set)
        return jsonify(result={'data': data_set})

@app.route('/get_all_requests', methods=['GET'])
@token_required
def get_all_requests(current_user):

    data_set = welcome_consultas.get_all_requests()
    if 'Error' in data_set:
        return jsonify(result={'error': data_set})
    else:
        print(data_set)
        return jsonify(result={'data': data_set})

@app.route('/register_request', methods=['POST'])
@token_required
def requests(current_user):
    # parameters from request
    now = datetime.datetime.now()
    asunto = request.form.get("asunto")
    descripcion = request.form.get("descripcion")
    urgencia = request.form.get("urgencia")
    status = "En Espera"
    tipo = request.form.get("tipo")

    # checks variables and makes sure all parameters were sent, empty string ('') will not cause this condition to fail
    if asunto is not None and descripcion is not None \
            and urgencia is not None and tipo is not None:
        full_response = welcome_consultas.register_request(current_user['user'], asunto, now.strftime("%Y-%m-%d %H:%M:%S"),descripcion, urgencia, status, tipo)
        if 'Error' in full_response:
            return jsonify(result={'error': full_response})
        else:
            return jsonify(result=full_response)


@app.route('/change_status', methods=['PUT'])
@token_required
def change_status(current_user):
    # parameters from request
    id = request.form.get("id")
    to = request.form.get("to")
    comment = request.form.get("comment")

    # checks variables and makes sure all parameters were sent, empty string ('') will not cause this condition to fail
    if id is not None and to is not None:
        full_response = welcome_consultas.update_status(id, to, comment)
        if 'Error' in full_response:
            return jsonify(result={'error': full_response})
        else:
            return jsonify(result=full_response)

@app.route('/change_score', methods=['PUT'])
@token_required
def change_score(current_user):
    # parameters from request
    id = request.form.get("id")
    to = request.form.get("to")

    # checks variables and makes sure all parameters were sent, empty string ('') will not cause this condition to fail
    if id is not None and to is not None:
        full_response = welcome_consultas.update_score(id, to)
        if 'Error' in full_response:
            return jsonify(result={'error': full_response})
        else:
            return jsonify(result=full_response)

@app.route('/insert_new', methods=['POST'])
@token_required
def insert_new(current_user):
    # parameters from request
    titulo = request.form.get("titulo")
    noticia = request.form.get("noticia")

    # checks variables and makes sure all parameters were sent, empty string ('') will not cause this condition to fail
    if titulo is not None and noticia is not None:
        full_response = welcome_consultas.insert_news(titulo, noticia)
        if 'Error' in full_response:
            return jsonify(result={'error': full_response})
        else:
            return jsonify(result=full_response)

@app.route('/delete_news', methods=['DELETE'])
@token_required
def delete_news(current_user):
    # parameters from request
    id = request.form.get("id")
    # checks variables and makes sure all parameters were sent, empty string ('') will not cause this condition to fail
    if id is not None:
        full_response = welcome_consultas.delete_news(id)
        if 'Error' in full_response:
            return jsonify(result={'error': full_response})
        else:
            return jsonify(result=full_response)

@app.route('/delete_manuals', methods=['DELETE'])
@token_required
def delete_manual(current_user):
    # parameters from request
    id = request.form.get("id")
    # checks variables and makes sure all parameters were sent, empty string ('') will not cause this condition to fail
    if id is not None:
        full_response = welcome_consultas.delete_manual(id)
        if 'Error' in full_response:
            return jsonify(result={'error': full_response})
        else:
            return jsonify(result=full_response)



@app.route('/secret/<path:path>', methods=['GET'])
@token_required
def get_hidden(current_user, path):
    try:

        # print(path)
        a = open(os.path.join(APP_ROOT, 'protected/' + path), "rb").read()
        # print(a)
        # a = base64.urlsafe_b64encode(a);
        a = base64.b64encode(a).decode('utf-8')
        # print(a)
        a = a.replace('\n', '')
        return jsonify(result=a)

    except Exception as e:
        return jsonify(result={'error': 'Archivo no pudo ser encontrado'})


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
