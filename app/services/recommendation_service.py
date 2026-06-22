"""
Servicio de generación de recomendaciones automáticas para vulnerabilidades.
Mapea cada tipo OWASP detectado a una recomendación pedagógica.
"""


def obtener_recomendacion(tipo_owasp: str) -> dict:
    """
    Obtiene la recomendación asociada a un tipo OWASP detectado.
    
    Args:
        tipo_owasp: Tipo OWASP detectado (ej: "A03:2021 - Inyección (eval/exec)")
    
    Returns:
        Diccionario con:
        - titulo: Título de la recomendación
        - explicacion_riesgo: Explicación pedagógica del riesgo
        - codigo_corregido_ejemplo: Código de ejemplo corregido
    """
    
    # Mapeo de tipos OWASP a recomendaciones
    mapeo = {
        # A03 - Inyección
        "A03:2021 - Inyección (eval/exec)": {
            "titulo": "Evitar eval() y exec() - Inyección de código",
            "explicacion_riesgo": (
                "eval() y exec() ejecutan código Python arbitrario. Si este código proviene de "
                "entrada del usuario (aunque sea indirectamente), un atacante puede inyectar código "
                "malicioso que se ejecutará con los mismos permisos de tu aplicación. "
                "Esto es uno de los riesgos más graves de seguridad. "
                "Siempre que necesites evaluar expresiones, usa alternativas seguras."
            ),
            "codigo_corregido_ejemplo": (
                "# ❌ INSEGURO - Nunca hagas esto:\n"
                "entrada = input('Ingresa una expresión: ')\n"
                "resultado = eval(entrada)  # Atacante puede injectar: __import__('os').system('rm -rf /')\n"
                "\n"
                "# ✅ SEGURO - Alternativas:\n"
                "# Opción 1: Usar ast.literal_eval para solo literales seguros\n"
                "import ast\n"
                "try:\n"
                "    resultado = ast.literal_eval(entrada)\n"
                "except (ValueError, SyntaxError):\n"
                "    resultado = None\n"
                "\n"
                "# Opción 2: Usar librerías especializadas (ej: numexpr para matemáticas)\n"
                "import numexpr\n"
                "resultado = numexpr.evaluate('2 + 2 * 3')\n"
                "\n"
                "# Opción 3: Parsear y validar manualmente"
            )
        },
        "A03:2021 - Inyección (os.system)": {
            "titulo": "Evitar os.system() - Inyección de comandos del sistema",
            "explicacion_riesgo": (
                "os.system() ejecuta comandos del sistema operativo. Si pasas entrada del usuario "
                "sin validar, un atacante puede inyectar comandos adicionales usando caracteres "
                "especiales como ; | && o $() para ejecutar código arbitrario en el servidor."
            ),
            "codigo_corregido_ejemplo": (
                "import subprocess\n"
                "\n"
                "# ❌ INSEGURO:\n"
                "archivo = input('Archivo a listar: ')\n"
                "os.system(f'ls -la {archivo}')  # Atacante: '; rm -rf /' \n"
                "\n"
                "# ✅ SEGURO - Usar subprocess con lista de argumentos:\n"
                "archivo = input('Archivo a listar: ')\n"
                "resultado = subprocess.run(['ls', '-la', archivo], capture_output=True, text=True)\n"
                "print(resultado.stdout)\n"
                "\n"
                "# Ventajas:\n"
                "# - Los argumentos se pasan como lista, NO como string\n"
                "# - El shell NO interpreta caracteres especiales\n"
                "# - shell=False previene inyección de comandos"
            )
        },
        "A03:2021 - Inyección (subprocess con shell=True)": {
            "titulo": "Evitar subprocess con shell=True - Inyección de comandos",
            "explicacion_riesgo": (
                "Cuando usas shell=True en subprocess, Python abre una shell (bash, cmd, etc.) "
                "que interpreta caracteres especiales. Si pasas entrada del usuario sin validar, "
                "un atacante puede inyectar comandos usando ; | && o $(). Esto es tan peligroso como os.system()."
            ),
            "codigo_corregido_ejemplo": (
                "import subprocess\n"
                "\n"
                "# ❌ INSEGURO:\n"
                "archivo = input('Archivo: ')\n"
                "subprocess.run(f'echo {archivo}', shell=True)  # Vulnerable a inyección\n"
                "\n"
                "# ✅ SEGURO:\n"
                "archivo = input('Archivo: ')\n"
                "resultado = subprocess.run(['echo', archivo], shell=False, capture_output=True)\n"
                "print(resultado.stdout.decode())\n"
                "\n"
                "# Si REALMENTE necesitas shell (muy raro), valida la entrada:\n"
                "import shlex\n"
                "archivo = shlex.quote(archivo)  # Escapa caracteres especiales\n"
                "subprocess.run(f'echo {archivo}', shell=True)"
            )
        },
        "A03:2021 - Inyección SQL (concatenación)": {
            "titulo": "Evitar concatenación de strings en SQL - Inyección SQL",
            "explicacion_riesgo": (
                "SQL Injection es uno de los ataques más antiguos y efectivos. Cuando construyes "
                "queries SQL concatenando strings con entrada del usuario, un atacante puede cerrar "
                "la consulta con comillas y agregar código SQL arbitrario. Puede robar datos, "
                "modificar tablas o eliminar información."
            ),
            "codigo_corregido_ejemplo": (
                "import sqlite3\n"
                "conn = sqlite3.connect('base_datos.db')\n"
                "cursor = conn.cursor()\n"
                "\n"
                "# ❌ INSEGURO - Concatenación (NUNCA HAGAS ESTO):\n"
                "usuario = input('Usuario: ')\n"
                "query = f\"SELECT * FROM usuarios WHERE nombre = '{usuario}'\"\n"
                "cursor.execute(query)\n"
                "# Atacante: nombre' OR '1'='1\n"
                "# Consulta resultante: SELECT * FROM usuarios WHERE nombre = '' OR '1'='1'\n"
                "\n"
                "# ✅ SEGURO - Usar placeholders (?) y tuplas:\n"
                "usuario = input('Usuario: ')\n"
                "query = 'SELECT * FROM usuarios WHERE nombre = ?'\n"
                "cursor.execute(query, (usuario,))  # Valor separado como tupla\n"
                "# El driver se encarga de escapar correctamente\n"
                "\n"
                "# Con librerías ORM (SQLAlchemy) es aún más seguro:\n"
                "from sqlalchemy import select\n"
                "stmt = select(Usuario).where(Usuario.nombre == usuario)\n"
                "# La librería construye la query de forma segura"
            )
        },
        "A03:2021 - Inyección (importar os.system/popen)": {
            "titulo": "Evitar importar os.system/popen directamente",
            "explicacion_riesgo": (
                "Si importas directamente funciones peligrosas como os.system o os.popen, "
                "es muy fácil usarlas accidentalmente o que otro código las abuse. "
                "Es mejor no tener estas herramientas disponibles si usas subprocess."
            ),
            "codigo_corregido_ejemplo": (
                "# ❌ INSEGURO:\n"
                "from os import system\n"
                "system('ls')  # Fácil olvidar los riesgos\n"
                "\n"
                "# ✅ RECOMENDADO:\n"
                "import subprocess\n"
                "subprocess.run(['ls'], shell=False)\n"
                "\n"
                "# Si necesitas os.system en algún caso muy específico (raro):\n"
                "import os\n"
                "# Úsalo como os.system(...) para que sea más visible que es peligroso"
            )
        },
        "A03:2021 - Inyección (importar subprocess)": {
            "titulo": "Importación segura de subprocess",
            "explicacion_riesgo": (
                "Importar subprocess es seguro. El riesgo está en cómo lo uses (shell=True, concatenación). "
                "Esta detección es preventiva para recordarte que debes usarlo con cuidado."
            ),
            "codigo_corregido_ejemplo": (
                "import subprocess\n"
                "\n"
                "# ✅ USO SEGURO:\n"
                "# Siempre paso argumentos como lista, NO como string:\n"
                "resultado = subprocess.run(['comando', 'arg1', 'arg2'], shell=False)\n"
                "\n"
                "# ✅ MEJOR: Usar run() en lugar de call()\n"
                "# run() es más nuevo y flexible que call()\n"
                "resultado = subprocess.run(['ls', '-la'], capture_output=True, text=True)\n"
                "print(resultado.stdout)\n"
                "print(resultado.stderr)"
            )
        },
        
        # A01 - Path Traversal / Acceso a archivos inseguro
        "A01:2021 - Acceso a archivo inseguro (open con variable)": {
            "titulo": "Validar rutas de archivo antes de abrirlas - Path Traversal",
            "explicacion_riesgo": (
                "Path Traversal permite a un atacante acceder a archivos fuera del directorio "
                "permitido usando rutas como '../../../etc/passwd'. Si abres archivos basado en "
                "entrada del usuario sin validar, puedes exponer datos sensibles del servidor."
            ),
            "codigo_corregido_ejemplo": (
                "import os\n"
                "from pathlib import Path\n"
                "\n"
                "# ❌ INSEGURO:\n"
                "archivo_solicitado = input('¿Qué archivo quieres leer? ')\n"
                "with open(archivo_solicitado, 'r') as f:  # Atacante: ../../etc/passwd\n"
                "    contenido = f.read()\n"
                "\n"
                "# ✅ SEGURO - Opción 1: Validar que la ruta es segura\n"
                "DIRECTORIO_SEGURO = '/var/app/archivos'\n"
                "archivo_solicitado = input('¿Qué archivo? ')\n"
                "\n"
                "ruta_completa = Path(DIRECTORIO_SEGURO) / archivo_solicitado\n"
                "ruta_completa = ruta_completa.resolve()  # Resuelve .. y enlaces simbólicos\n"
                "\n"
                "# Verificar que la ruta está dentro del directorio permitido\n"
                "if not str(ruta_completa).startswith(os.path.abspath(DIRECTORIO_SEGURO)):\n"
                "    raise ValueError('Ruta fuera del directorio permitido')\n"
                "\n"
                "with open(ruta_completa, 'r') as f:\n"
                "    contenido = f.read()\n"
                "\n"
                "# ✅ SEGURO - Opción 2: Usar whitelist\n"
                "ARCHIVOS_PERMITIDOS = {'archivo1.txt', 'archivo2.txt', 'datos.json'}\n"
                "archivo_solicitado = input('Archivo: ')\n"
                "\n"
                "if archivo_solicitado not in ARCHIVOS_PERMITIDOS:\n"
                "    raise ValueError('Archivo no permitido')\n"
                "\n"
                "with open(f'/var/app/archivos/{archivo_solicitado}', 'r') as f:\n"
                "    contenido = f.read()"
            )
        },
        
        # A02 - Deserialización insegura
        "A02:2021 - Deserialización insegura": {
            "titulo": "Evitar pickle con datos no confiables - Deserialización insegura",
            "explicacion_riesgo": (
                "pickle puede ejecutar código arbitrario durante la deserialización. "
                "Si deserializas datos que vienen del usuario, internet o archivos no confiables, "
                "un atacante puede inyectar código malicioso que se ejecutará automáticamente."
            ),
            "codigo_corregido_ejemplo": (
                "import pickle\nimport json\n"
                "\n"
                "# ❌ INSEGURO - Nunca deserialices pickle de entrada no confiable:\n"
                "datos_usuario = input('Datos: ')  # Usuario sube datos\n"
                "objeto = pickle.loads(datos_usuario)  # Ejecuta código malicioso\n"
                "\n"
                "# ✅ SEGURO - Alternativas:\n"
                "\n"
                "# Opción 1: Usar JSON (seguro, solo datos estructurados)\n"
                "datos_usuario = input('Datos JSON: ')\n"
                "objeto = json.loads(datos_usuario)  # Solo interpreta JSON, no código\n"
                "\n"
                "# Opción 2: Si NECESITAS pickle (ej: datos internos solo):\n"
                "# - Usa HMAC para verificar que no fue modificado\n"
                "# - Deserializa solo en ambiente controlado\n"
                "import hmac\n"
                "import hashlib\n"
                "\n"
                "CLAVE_SECRETA = 'tu_clave_segura'\n"
                "datos_pickled = pickle.dumps(objeto)\n"
                "firma = hmac.new(CLAVE_SECRETA.encode(), datos_pickled, hashlib.sha256).digest()\n"
                "\n"
                "# Luego, al recibir:\n"
                "firma_recibida, datos_recibidos = ... # Separar\n"
                "if hmac.compare_digest(firma_recibida, hmac.new(...).digest()):\n"
                "    objeto = pickle.loads(datos_recibidos)  # Solo si firma es válida\n"
                "else:\n"
                "    raise ValueError('Datos fueron modificados')"
            )
        },
        "A02:2021 - Algoritmo criptográfico débil (md5)": {
            "titulo": "Evitar MD5 para hash seguro - Usa algoritmos modernos",
            "explicacion_riesgo": (
                "MD5 está roto desde 2004. Es muy rápido de calcular, lo que permite "
                "ataques de fuerza bruta y colisión de hashes. Nunca uses MD5 para hashear "
                "contraseñas o datos sensibles. Usa algoritmos modernos como bcrypt, scrypt o Argon2."
            ),
            "codigo_corregido_ejemplo": (
                "import hashlib\nimport bcrypt\n"
                "\n"
                "password = 'mi_contraseña'\n"
                "\n"
                "# ❌ INSEGURO - MD5 está roto:\n"
                "import md5\n"
                "hash_debil = md5.new(password.encode()).hexdigest()\n"
                "\n"
                "# ❌ INSEGURO - SHA1 también está roto:\n"
                "hash_debil2 = hashlib.sha1(password.encode()).hexdigest()\n"
                "\n"
                "# ✅ SEGURO - Usar bcrypt (incluye salt automático):\n"
                "hash_seguro = bcrypt.hashpw(password.encode(), bcrypt.gensalt())\n"
                "# Verificar:\n"
                "if bcrypt.checkpw(password.encode(), hash_seguro):\n"
                "    print('Contraseña correcta')\n"
                "\n"
                "# ✅ ALTERNATIVA - Argon2 (aún más seguro):\n"
                "from argon2 import PasswordHasher\n"
                "ph = PasswordHasher()\n"
                "hash_argon2 = ph.hash(password)\n"
                "# Verificar:\n"
                "try:\n"
                "    ph.verify(hash_argon2, password)\n"
                "except Exception:\n"
                "    print('Contraseña incorrecta')"
            )
        },
        
        # A04 - Exposición de información
        "A04:2021 - Configuración insegura (debug=True)": {
            "titulo": "Desactivar modo debug en producción",
            "explicacion_riesgo": (
                "Cuando debug=True en Flask, FastAPI o similar, la aplicación muestra "
                "stack traces completos, variables locales, configuración y rutas. "
                "Un atacante puede usar esta información para encontrar vulnerabilidades. "
                "NUNCA actives debug en producción."
            ),
            "codigo_corregido_ejemplo": (
                "# ❌ INSEGURO:\n"
                "app.run(debug=True)  # Habilita el console interactivo y stack traces\n"
                "\n"
                "# ✅ SEGURO:\n"
                "import os\n"
                "DEBUG = os.getenv('DEBUG', 'False') == 'True'\n"
                "app.run(debug=DEBUG)  # Controla con variable de entorno\n"
                "\n"
                "# Mejor aún, para FastAPI:\n"
                "from fastapi import FastAPI\n"
                "import os\n"
                "\n"
                "app = FastAPI(\n"
                "    title='Mi App',\n"
                "    docs_url='/api/docs' if os.getenv('ENV') != 'production' else None,\n"
                "    redoc_url='/api/redoc' if os.getenv('ENV') != 'production' else None,\n"
                ")\n"
                "\n"
                "# En producción, no expongas documentación automática"
            )
        },
        "A04:2021 - Exposición de información (print en except)": {
            "titulo": "No expongas excepciones al usuario - Manejo seguro de errores",
            "explicacion_riesgo": (
                "Cuando capturas una excepción y la imprimes o la devuelves al usuario, "
                "expones información interna de tu aplicación (rutas de archivos, queries SQL, librerías). "
                "Un atacante usa esto para buscar vulnerabilidades. Siempre registra errores internamente "
                "pero muestra mensajes seguros al usuario."
            ),
            "codigo_corregido_ejemplo": (
                "import logging\n"
                "\n"
                "logger = logging.getLogger(__name__)\n"
                "\n"
                "# ❌ INSEGURO:\n"
                "try:\n"
                "    resultado = int(entrada)\n"
                "except ValueError as e:\n"
                "    print(e)  # Expone: invalid literal for int() with base 10\n"
                "    return str(e)  # Usuario ve el error interno\n"
                "\n"
                "# ✅ SEGURO:\n"
                "try:\n"
                "    resultado = int(entrada)\n"
                "except ValueError as e:\n"
                "    logger.error(f'Error conversión: {e}')  # Log interno\n"
                "    return 'El valor ingresado no es válido'  # Mensaje genérico\n"
                "\n"
                "# Para APIs:\n"
                "from fastapi import HTTPException\n"
                "\n"
                "try:\n"
                "    procesar_datos()\n"
                "except Exception as e:\n"
                "    logger.exception('Error en procesar_datos')  # Stack trace en logs\n"
                "    raise HTTPException(status_code=500, detail='Error interno del servidor')"
            )
        },
        "A04:2021 - Exposición de información (return en except)": {
            "titulo": "No devuelvas excepciones como respuesta - Información sensible",
            "explicacion_riesgo": (
                "Devolver la representación de una excepción (str(e) o repr(e)) "
                "expone detalles internos al cliente. Esto es especialmente peligroso en APIs."
            ),
            "codigo_corregido_ejemplo": (
                "import logging\nfrom fastapi import HTTPException\n"
                "\n"
                "logger = logging.getLogger(__name__)\n"
                "\n"
                "# ❌ INSEGURO:\n"
                "def obtener_usuario(id: int):\n"
                "    try:\n"
                "        usuario = db.query(Usuario).filter(Usuario.id == id).first()\n"
                "        return usuario\n"
                "    except Exception as e:\n"
                "        return {'error': str(e)}  # Expone detalles de BD\n"
                "\n"
                "# ✅ SEGURO:\n"
                "def obtener_usuario(id: int):\n"
                "    try:\n"
                "        usuario = db.query(Usuario).filter(Usuario.id == id).first()\n"
                "        if not usuario:\n"
                "            raise HTTPException(status_code=404, detail='Usuario no encontrado')\n"
                "        return usuario\n"
                "    except HTTPException:\n"
                "        raise  # Repropaga excepciones HTTP\n"
                "    except Exception as e:\n"
                "        logger.exception(f'Error al obtener usuario {id}')\n"
                "        raise HTTPException(status_code=500, detail='Error interno')"
            )
        },
        
        # A05 - Configuración insegura / CORS / CSRF
        "A05:2021 - Configuración insegura (DEBUG=True)": {
            "titulo": "Desactivar DEBUG en producción",
            "explicacion_riesgo": (
                "DEBUG=True expone información sensible de la configuración. "
                "Usa variables de entorno para controlar esto según el ambiente."
            ),
            "codigo_corregido_ejemplo": (
                "import os\nfrom dotenv import load_dotenv\n"
                "\n"
                "load_dotenv()\n"
                "DEBUG = os.getenv('DEBUG', 'False') == 'True'\n"
                "ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')\n"
                "\n"
                "# .env (NUNCA commitees esto a Git):\n"
                "# DEBUG=True\n"
                "# ALLOWED_HOSTS=localhost,127.0.0.1\n"
                "\n"
                "# .env.production:\n"
                "# DEBUG=False\n"
                "# ALLOWED_HOSTS=tudominio.com,www.tudominio.com"
            )
        },
        "A05:2021 - Configuración insegura (ALLOWED_HOSTS=*)": {
            "titulo": "Restringir ALLOWED_HOSTS - Evita ataques de Host Header Injection",
            "explicacion_riesgo": (
                "Si permites cualquier host (ALLOWED_HOSTS=['*']), un atacante puede "
                "enviar un header Host falso para acceder a tu aplicación con un dominio diferente. "
                "Esto permite ataques de password reset poisoning y cache poisoning."
            ),
            "codigo_corregido_ejemplo": (
                "# ❌ INSEGURO:\n"
                "ALLOWED_HOSTS = ['*']  # Acepta cualquier Host header\n"
                "\n"
                "# ✅ SEGURO:\n"
                "ALLOWED_HOSTS = [\n"
                "    'tudominio.com',\n"
                "    'www.tudominio.com',\n"
                "    'api.tudominio.com',\n"
                "    'localhost',\n"
                "    '127.0.0.1',\n"
                "]\n"
                "\n"
                "# O con variables de entorno:\n"
                "import os\n"
                "ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')\n"
                "\n"
                "# En FastAPI/Starlette:\n"
                "from starlette.middleware import Middleware\n"
                "from starlette.middleware.trustedhost import TrustedHostMiddleware\n"
                "\n"
                "middleware = [\n"
                "    Middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)\n"
                "]\n"
                "app = FastAPI(middleware=middleware)"
            )
        },
        "A05:2021 - CORS abierto (allow_origins=[\"*\"])": {
            "titulo": "Restringir CORS - Evita ataques desde otros dominios",
            "explicacion_riesgo": (
                "CORS (Cross-Origin Resource Sharing) permite que navegadores accedan a tu "
                "API desde otros dominios. Si permites origins=['*'], CUALQUIER sitio web "
                "puede hacer solicitudes a tu API en nombre de usuarios conectados. "
                "Esto permite robo de datos y acciones no autorizadas."
            ),
            "codigo_corregido_ejemplo": (
                "from fastapi.middleware.cors import CORSMiddleware\n"
                "import os\n"
                "\n"
                "# ❌ INSEGURO:\n"
                "app.add_middleware(\n"
                "    CORSMiddleware,\n"
                "    allow_origins=['*'],  # Acepta CUALQUIER origen\n"
                "    allow_credentials=True,  # Aún PEOR con credenciales\n"
                ")\n"
                "\n"
                "# ✅ SEGURO:\n"
                "allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')\n"
                "\n"
                "app.add_middleware(\n"
                "    CORSMiddleware,\n"
                "    allow_origins=allowed_origins,  # Solo dominios específicos\n"
                "    allow_credentials=True,  # Si necesitas cookies/auth\n"
                "    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],  # Métodos específicos\n"
                "    allow_headers=['Content-Type', 'Authorization'],  # Headers específicos\n"
                "    max_age=3600,  # Cache preflight requests\n"
                ")\n"
                "\n"
                "# .env:\n"
                "# CORS_ORIGINS=https://tuapp.com,https://www.tuapp.com"
            )
        },
        
        # A07 - Información sensible
        "A07:2021 - Información sensible en el código": {
            "titulo": "No almacenes secretos en el código - Usa variables de entorno",
            "explicacion_riesgo": (
                "Contraseñas, API keys, tokens y claves criptográficas en el código fuente "
                "son expuestos cuando alguien accede al repositorio, ves un archivo de backup "
                "o si el repo es público accidentalmente. Esto permite acceso no autorizado "
                "a sistemas críticos."
            ),
            "codigo_corregido_ejemplo": (
                "import os\nfrom dotenv import load_dotenv\n"
                "\n"
                "# ❌ INSEGURO - Nunca hagas esto:\n"
                "DATABASE_URL = 'postgresql://user:password123@localhost/mydb'\n"
                "API_KEY = 'sk-1234567890abcdefghijklmnop'\n"
                "JWT_SECRET = 'mi_secreto_super_importante'\n"
                "\n"
                "# ✅ SEGURO - Usa variables de entorno:\n"
                "load_dotenv()  # Carga desde .env (NO commits a Git)\n"
                "\n"
                "DATABASE_URL = os.getenv('DATABASE_URL')\n"
                "API_KEY = os.getenv('API_KEY')\n"
                "JWT_SECRET = os.getenv('JWT_SECRET')\n"
                "\n"
                "if not DATABASE_URL:\n"
                "    raise ValueError('DATABASE_URL no configurada')\n"
                "\n"
                "# .env (en tu máquina local):\n"
                "# DATABASE_URL=postgresql://user:password123@localhost/mydb\n"
                "# API_KEY=sk-1234567890abcdefghijklmnop\n"
                "# JWT_SECRET=mi_secreto_super_importante\n"
                "\n"
                "# .gitignore (IMPORTANTE):\n"
                "# .env\n"
                "# .env.local\n"
                "# *.key\n"
                "# secrets/\n"
                "\n"
                "# En CI/CD (GitHub Actions, GitLab CI, etc.):\n"
                "# Configura secrets en la plataforma y úsalos como variables de entorno"
            )
        },
        
        # A08 - Deserialización insegura
        "A08:2021 - Deserialización insegura (yaml.load sin SafeLoader)": {
            "titulo": "Usar yaml.safe_load() en lugar de yaml.load()",
            "explicacion_riesgo": (
                "yaml.load() sin especificar Loader ejecuta código Python embebido en YAML. "
                "Un atacante puede inyectar código malicioso en un archivo YAML que se ejecutará "
                "cuando lo cargues."
            ),
            "codigo_corregido_ejemplo": (
                "import yaml\n"
                "\n"
                "# ❌ INSEGURO:\n"
                "datos_yaml = input('Ingresa YAML: ')\n"
                "config = yaml.load(datos_yaml)  # Ejecuta código Python\n"
                "# Atacante: !python/object/apply:os.system ['rm -rf /']\n"
                "\n"
                "# ✅ SEGURO - Opción 1: safe_load (recomendado)\n"
                "config = yaml.safe_load(datos_yaml)  # Solo carga estructuras YAML seguras\n"
                "\n"
                "# ✅ SEGURO - Opción 2: Especificar Loader seguro\n"
                "config = yaml.load(datos_yaml, Loader=yaml.SafeLoader)\n"
                "\n"
                "# Diferencia:\n"
                "# - yaml.safe_load(): Carga solo tipos básicos (dict, list, str, int, etc.)\n"
                "# - yaml.load(Loader=yaml.SafeLoader): Igual que safe_load\n"
                "# - yaml.load(Loader=yaml.FullLoader): Más seguro que FullLoader pero menos que SafeLoader\n"
                "# - yaml.load(): SIN Loader es peligroso (por defecto usa FullLoader, depende versión)"
            )
        },
        "A08:2021 - Deserialización insegura (jsonpickle)": {
            "titulo": "Evitar jsonpickle - Usa JSON con manejo seguro",
            "explicacion_riesgo": (
                "jsonpickle intenta ser compatible con pickle usando JSON. Sigue siendo inseguro "
                "para datos no confiables. Usa JSON puro o librerías seguras como msgpack."
            ),
            "codigo_corregido_ejemplo": (
                "import json\n"
                "\n"
                "# ❌ EVITAR:\n"
                "import jsonpickle\n"
                "datos = jsonpickle.loads(entrada_usuario)  # Riesgoso\n"
                "\n"
                "# ✅ RECOMENDADO - JSON puro:\n"
                "datos = json.loads(entrada_usuario)  # Seguro, solo estructuras JSON\n"
                "\n"
                "# Validar estructura con pydantic (si es para una API):\n"
                "from pydantic import BaseModel\n"
                "\n"
                "class MiDato(BaseModel):\n"
                "    nombre: str\n"
                "    edad: int\n"
                "\n"
                "entrada = json.loads(entrada_usuario)\n"
                "dato = MiDato(**entrada)  # Valida estructura y tipos"
            )
        },
        
        # A10 - SSRF
        "A10:2021 - SSRF (request con URL variable)": {
            "titulo": "Validar URLs antes de hacer requests - SSRF",
            "explicacion_riesgo": (
                "SSRF (Server-Side Request Forgery) permite a un atacante hacer que tu servidor "
                "acceda a URLs internas o externas no autorizadas. Si tomas una URL de entrada "
                "del usuario sin validar, un atacante puede acceder a servicios internos (localhost, "
                "IP privadas) o descargar archivos maliciosos."
            ),
            "codigo_corregido_ejemplo": (
                "import requests\nfrom urllib.parse import urlparse\n"
                "\n"
                "# ❌ INSEGURO:\n"
                "url = input('URL a descargar: ')\n"
                "respuesta = requests.get(url)  # Atacante: http://localhost:8080 o http://169.254.169.254\n"
                "\n"
                "# ✅ SEGURO - Validar URL:\n"
                "from urllib.parse import urlparse\nimport ipaddress\n"
                "\n"
                "def es_url_segura(url):\n"
                "    '''Verifica que la URL es segura para request.'''\n"
                "    parsed = urlparse(url)\n"
                "    \n"
                "    # Validar esquema\n"
                "    if parsed.scheme not in ('http', 'https'):\n"
                "        return False\n"
                "    \n"
                "    # No permitir localhost ni IPs privadas\n"
                "    if parsed.hostname in ('localhost', '127.0.0.1', '0.0.0.0'):\n"
                "        return False\n"
                "    \n"
                "    # No permitir rangos de IP privadas\n"
                "    try:\n"
                "        ip = ipaddress.ip_address(parsed.hostname)\n"
                "        if ip.is_private or ip.is_loopback:\n"
                "            return False\n"
                "    except ValueError:\n"
                "        pass  # Es un hostname, no una IP\n"
                "    \n"
                "    return True\n"
                "\n"
                "url = input('URL: ')\n"
                "if not es_url_segura(url):\n"
                "    raise ValueError('URL no permitida')\n"
                "\n"
                "respuesta = requests.get(url, timeout=5)  # También usa timeout\n"
                "\n"
                "# ✅ ALTERNATIVA - Whitelist de dominios:\n"
                "DOMINIOS_PERMITIDOS = {'example.com', 'api.example.com'}\n"
                "\n"
                "parsed = urlparse(url)\n"
                "if parsed.hostname not in DOMINIOS_PERMITIDOS:\n"
                "    raise ValueError('Dominio no permitido')\n"
                "\n"
                "respuesta = requests.get(url, timeout=5)"
            )
        },
        
        # Error de sintaxis
        "Error de sintaxis - no se pudo analizar": {
            "titulo": "Errores de sintaxis en el código",
            "explicacion_riesgo": (
                "El analizador encontró errores de sintaxis que impiden analizar el archivo. "
                "Revisa que el código Python sea válido antes de ejecutar el análisis."
            ),
            "codigo_corregido_ejemplo": (
                "# Errores comunes de sintaxis:\n"
                "# 1. Indentación inconsistente\n"
                "if True:\n"
                "print('Esto causa IndentationError')\n"
                "\n"
                "# 2. Paréntesis/comillas sin cerrar\n"
                "lista = [1, 2, 3\n"
                "# Falta ]\n"
                "\n"
                "# 3. Palabras clave mal escritas\n"
                "iff True:  # Debería ser 'if'\n"
                "    pass\n"
                "\n"
                "# Soluciones:\n"
                "# - Verifica la indentación (usa espacios, no tabs)\n"
                "# - Cierra todos los paréntesis, corchetes y llaves\n"
                "# - Usa un linter (pylint, flake8) para detectar errores\n"
                "# - Configura tu editor para mostrar errores de sintaxis"
            )
        }
    }
    
    # Buscar coincidencia exacta primero
    if tipo_owasp in mapeo:
        return mapeo[tipo_owasp]
    
    # Si no hay coincidencia exacta, buscar por prefijo (ej: A03:2021 - Inyección)
    for clave, recomendacion in mapeo.items():
        if tipo_owasp.startswith(clave.split(' - ')[0]):  # Coincidencia por código OWASP
            return recomendacion
    
    # Si no hay ninguna coincidencia, devolver una recomendación genérica
    return {
        "titulo": f"Revisar: {tipo_owasp}",
        "explicacion_riesgo": (
            "Se detectó una vulnerabilidad relacionada con seguridad. "
            "Por favor, revisa el código vulnerable indicado y aplica las mejores prácticas "
            "de seguridad para tu caso específico."
        ),
        "codigo_corregido_ejemplo": (
            "# Analiza el fragmento de código vulnerable\n"
            "# Busca alternativas seguras en:\n"
            "# - OWASP Top 10: https://owasp.org/Top10/\n"
            "# - CWE: https://cwe.mitre.org/\n"
            "# - Documentación de librerías seguras"
        )
    }
