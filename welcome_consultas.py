#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import jwt
import ibm_boto3
import json
import pymysql
import requests
import base64
from PIL import Image
from ibm_botocore.client import Config


# Connection string

# --- SQL FUNCTIONS START ---
def login(expediente, password, deDonde):
    """
    Create and execute query to validate if user record exist. When user is found it inserts a record to the
    table that holds a log of everyone that has logged in
    """
    # holds query string
    query = "SELECT usuario_tipo, cuenta_id, estado, ciudad, nombre, region FROM usuarios WHERE expediente='"+expediente+"' AND password='"+password+"';"
    # holds a dataset of the users returns (should only be one if email is part of a primary key) # TODO
    res_query = row_set(query)

    # validate if empty
    if res_query is not False:
        # validate if an error
        if 'Error' in res_query:
            # return error string
            return res_query
        else:
            # validate if an empty variable
            #if res_query is not None:
             #   now = datetime.datetime.now()
                # holds query string
              #  query = "INSERT INTO registro_usuarios(email ,fecha, donde ) " \
               #         "values('"+email+"', '"+now.strftime('%Y-%m-%d %H:%M:%S')+"','"+deDonde+"' ); "
                # excutes
                #res_insert = row_insert(query)
                #print("res insert")
                #print(res_insert)
                # validate if an error
                #if 'Error' in res_insert:
                    # return error string
                    #return res_insert
                #else:
                    # return user type -- returns first index in case forsome reason it finds more
            return res_query
    else:
        # was not able to find any record
        return False
    # This function will (should) only return one result


def get_searchables(current_user):
    """Creates and executes two queries (we have 'errores' and 'tips' in separate tables)
    then combines both results into one array"""
    # holds string query
    query = "SELECT * FROM manuales;"
    # holds dataset
    tips = row_set(query)
    if 'Error' in tips:
        # return error string
        return tips
    else:
        return tips

def get_request_by_city(current_user):
    """Creates and executes two queries (we have 'errores' and 'tips' in separate tables)
    then combines both results into one array"""
    # holds string query
    city = current_user['user_type'][0]['ciudad']
    query = "select usuarios.nombre, peticiones.* from usuarios inner join peticiones on peticiones.usuario = usuarios.expediente where usuarios.ciudad = '"+city+"';"
    #query = "SELECT nombre FROM usuarios where email = '"+email+"';"
    # holds dataset
    res = row_set(query)
    if 'Error' in res:
        # return error string
        return res
    else:
        return res
        # holds dataset

def get_request_by_region(current_user):
    """Creates and executes two queries (we have 'errores' and 'tips' in separate tables)
    then combines both results into one array"""
    # holds string query
    print(current_user)
    region = current_user['user_type'][0]['region']
    query = "select usuarios.nombre, usuarios.ciudad, peticiones.* from usuarios inner join peticiones on peticiones.usuario = usuarios.expediente where usuarios.region = '"+region+"';"
    #query = "SELECT nombre FROM usuarios where email = '"+email+"';"
    # holds dataset
    res = row_set(query)
    if 'Error' in res:
        # return error string
        return res
    else:
        return res

def get_requests_by_user(usuario):
    """Creates and executes two queries (we have 'errores' and 'tips' in separate tables)
    then combines both results into one array"""
    # holds string query
    query = "select usuarios.nombre,  peticiones.* from usuarios inner join peticiones on peticiones.usuario = usuarios.expediente where usuarios.expediente = '"+usuario+"';"
    # holds dataset
    tips = row_set(query)
    if 'Error' in tips:
        # return error string
        return tips
    else:
        return tips
        # holds dataset

def update_status(id, to, comment):
    print("to")
    print(to)
    print("id")
    print(id)
    #query = "UPDATE peticiones SET status = '"+to+"' WHERE id='"+id+"';"
    query = "UPDATE peticiones SET status = '"+to+"', comentario = '"+comment+"'  WHERE id= "+id+";"
    # holds dataset
    res_insert = row_insert(query)
    if 'Error' in res_insert:
        # return error string
        return res_insert
    else:
        return res_insert

def update_score(id, to):
    print("to")
    print(to)
    print("id")
    print(id)
    #query = "UPDATE peticiones SET status = '"+to+"' WHERE id='"+id+"';"
    query = "UPDATE peticiones SET calificacion = '"+to+"'WHERE id= "+id+";"
    # holds dataset
    res_insert = row_insert(query)
    if 'Error' in res_insert:
        # return error string
        return res_insert
    else:
        return res_insert


def insert_news(titulo, noticia):

    query = "INSERT INTO noticias(titulo ,noticia) " \
                     "values('"+titulo+"', '"+noticia+"' ); "
    # holds dataset
    res_insert = row_insert(query)
    if 'Error' in res_insert:
        # return error string
        return res_insert
    else:
        return res_insert

def delete_news(id):

    query = "delete from noticias where id = '"+id+"'; "
    # holds dataset
    res_insert = row_insert(query)
    if 'Error' in res_insert:
        # return error string
        return res_insert
    else:
        return res_insert

def delete_manual(id):

    query = "delete from manuales where id = '"+id+"'; "
    # holds dataset
    res_insert = row_insert(query)
    if 'Error' in res_insert:
        # return error string
        return res_insert
    else:
        return res_insert


def get_all_requests():
    # holds string query
    query = "select usuarios.nombre, usuarios.ciudad, peticiones.* from usuarios inner join peticiones on peticiones.usuario = usuarios.expediente;"
    # holds dataset
    tips = row_set(query)
    if 'Error' in tips:
        # return error string
        return tips
    else:
        return tips
        # holds dataset

def register_request(usuario, asunto, fecha, descripcion, urgencia, status, tipo):
    """Creates a new record in the feedback table
    validates if empty where this method was called """
    query = "insert into peticiones (usuario, asunto, fecha, descripcion, urgencia, status, tipo) " \
            "Values ('" + usuario + "','" + asunto + "','" + fecha + "','" + descripcion + "','" + urgencia + "','" + status + "','" + tipo + "');"
    return row_insert(query)

def get_news():
    query = "SELECT * FROM noticias;"
    news = row_set(query)
    if 'Error' in news:
        return news
    else:
        return news

def get_contacts(current_user):

    estado = current_user['user_type'][0]['region']
    query = "SELECT nombre, telefono FROM usuarios where (region='"+estado+"' and cuenta_id != 1) or cuenta_id = 4;"
    contacts = row_set(query)
    if 'Error' in contacts:
        return contacts
    else:
        return contacts

def row_set(query):
    """function returns a list of records selected depending on the query ** only for select"""
    try:
        # Connection to db
        connection = pymysql.connect(host='localhost', user='root', passwd='IRV0304', db='cjf')
        try:
            # query execution
            print(query)
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query)
            # returns one dictionary (first row)
            row_dict = cursor.fetchall()
            return row_dict

        except:
            # if we could not execute the query
            # return "Error: " +  ibm_db.stmt_errormsg()
            return "Error al procesar la consulta"
    except:
        # cannot connect to db
        # print( "Error: " + ibm_db.conn_errormsg())
        return "Error al intentar conectar a la base de datos"


def row_insert(query):
    """function wil insert records to tables"""
    try:
        # connect to db
        connection = pymysql.connect(host='localhost', user='root', passwd='IRV0304', db='cjf')
        try:
            # execute query
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query)
            connection.commit()
        except:
            # could not execute query
            return "Error al procesar la consulta"
    except:
        # could not connect to db
        return "Error al intentar conectar a la base de datos"
    else:
        # if everything is ok then we return
        return {'status': 200}

# --- SQL FUNCTIONS END ---


# --- SERVER SIDE FUNCTIONS ---
# documented
def create_token(email, type_user, key):
    # generates jwt token
    # print(1)
    # print(2)
    token = jwt.encode({'user': email, 'user_type': type_user}, key)
    # print(3)
    return token.decode('UTF-8')


def decode_image(data):
    try:
        img_data = base64.b64decode(data)
        # use temporary file in root dir -- will always overwrite
        fh = open("img.png", "wb")
        fh.write(img_data)
        fh.close()
        # uses pillow library to reduce the size of image
        fh = Image.open("img.png")
        fh.save("img.png", quality=20, optimize=True)
    except IOError as e:
        return 'An IOError occurred. {}'.format(e.args[-1])
# --- SERVER SIDE FUNCTIONS ---
# --- COS Connection object ---



