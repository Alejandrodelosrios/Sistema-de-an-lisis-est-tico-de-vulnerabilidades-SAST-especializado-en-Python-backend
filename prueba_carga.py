# ============================================================
# ARCHIVO DE PRUEBA - Vulnerabilidades para motor_ast.py
# Cubre todas las detecciones implementadas en MotorAST
# ============================================================

import os
import pickle
import subprocess
from hashlib import md5, sha1
from os import system
import marshal
import shelve


# ─── A07:2021 - Información sensible en el código ───────────
password = "super_secreto_123"
api_key = "sk-abc123xyz456"
secret = "mi_clave_privada"
jwt = "eyJhbGciOiJIUzI1NiJ9.payload.signature"
token = "ghp_token_ejemplo"
private_key = "-----BEGIN RSA PRIVATE KEY-----"
passwd = "admin1234"
pwd = "contraseña_db"


# ─── A02:2021 - Algoritmos criptográficos débiles ───────────
# ya detectado por los imports de arriba:
# from hashlib import md5, sha1
# import pickle / marshal / shelve


# ─── A03:2021 - Inyección ───────────────────────────────────

def ejecutar_comando_usuario(comando):
    # os.system con variable
    os.system(comando)

    # subprocess con shell=True
    subprocess.call(["ls", "-la"], shell=True)
    subprocess.run(comando, shell=True)
    subprocess.Popen(comando, shell=True)


def evaluar_expresion(expresion):
    # eval y exec — inyección crítica
    resultado = eval(expresion)
    exec(expresion)
    return resultado


def consulta_sql(cursor, user_input):
    # cursor.execute con concatenación de strings
    cursor.execute("SELECT * FROM users WHERE name = '" + user_input + "'")


# ─── A01:2021 - Acceso a archivo inseguro ───────────────────

def leer_archivo_usuario(user_path, input_file, request_file, param, url, file):
    # open() con variables que contienen palabras clave sospechosas
    with open(user_path, "r") as f:
        contenido = f.read()

    with open(input_file, "r") as f:
        data = f.read()

    with open(request_file, "rb") as f:
        raw = f.read()


# ─── A04:2021 - Configuración insegura ──────────────────────

def iniciar_app():
    app = object()  # simulado
    app.run(debug=True)


def modo_desarrollo():
    from flask import Flask
    application = Flask(__name__)
    application.run(debug=True)


# ─── A04:2021 - Exposición de información en except ─────────

def operacion_riesgosa():
    try:
        resultado = 10 / 0
    except Exception as e:
        print(e)  # expone info del error


def otra_operacion():
    try:
        x = int("no_es_numero")
    except ValueError as e:
        return str(e)  # expone info del error en la respuesta


def tercera_operacion():
    try:
        datos = pickle.loads(b"datos_no_confiables")
    except Exception as e:
        return repr(e)