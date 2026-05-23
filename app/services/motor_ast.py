import ast
from dataclasses import dataclass


@dataclass
class VulnerabilidadDetectada:
    tipo_owasp: str
    severidad: str
    score_cvss: float
    codigo_vulnerable: str
    linea_codigo: int
    fragmento_codigo: str


class MotorAST(ast.NodeVisitor):
    """Motor de análisis estático para detectar vulnerabilidades OWASP."""
    
    def __init__(self, lineas_codigo: list[str]):
        self.vulnerabilidades: list[VulnerabilidadDetectada] = []
        self.lineas = lineas_codigo

    def _fragmento(self, linea: int) -> str:
        """Obtiene un fragmento de código alrededor de la línea especificada."""
        inicio = max(0, linea - 3)
        fin = min(len(self.lineas), linea + 2)
        return "\n".join(self.lineas[inicio:fin])

    def _agregar(self, nodo, tipo_owasp, severidad, score_cvss, codigo):
        """Agrega una vulnerabilidad detectada a la lista."""
        self.vulnerabilidades.append(VulnerabilidadDetectada(
            tipo_owasp=tipo_owasp,
            severidad=severidad,
            score_cvss=score_cvss,
            codigo_vulnerable=codigo,
            linea_codigo=nodo.lineno,
            fragmento_codigo=self._fragmento(nodo.lineno)
        ))

    def visit_Call(self, nodo):
        """Detecta A03:2021, A04:2021 y A01:2021 en llamadas de función."""
        
        # A03:2021 - Inyección: eval() y exec()
        if isinstance(nodo.func, ast.Name):
            if nodo.func.id in ('eval', 'exec'):
                self._agregar(nodo, 'A03:2021 - Inyección (eval/exec)', 
                             'critica', 9.8, f'{nodo.func.id}(...)')
            
            # A04:2021 - Configuración insegura: debug=True
            if nodo.func.id in ('run',):
                for keyword in nodo.keywords:
                    if keyword.arg == 'debug' and isinstance(keyword.value, ast.Constant):
                        if keyword.value.value is True:
                            self._agregar(nodo, 'A04:2021 - Configuración insegura (debug=True)',
                                        'media', 5.3, 'app.run(debug=True)')
            
            # A01:2021 - open() inseguro
            if nodo.func.id == 'open' and nodo.args:
                primer_arg = nodo.args[0]
                if isinstance(primer_arg, ast.Name):
                    if any(palabra in primer_arg.id.lower() 
                           for palabra in ['user', 'input', 'param', 'request', 'path', 'file', 'url']):
                        self._agregar(nodo, 'A01:2021 - Acceso a archivo inseguro (open con variable)',
                                    'alta', 7.2, f'open({primer_arg.id}, ...)')
        
        # A03:2021 - Inyección: os.system()
        elif isinstance(nodo.func, ast.Attribute):
            if nodo.func.attr == 'system':
                if isinstance(nodo.func.value, ast.Name) and nodo.func.value.id == 'os':
                    self._agregar(nodo, 'A03:2021 - Inyección (os.system)',
                                'critica', 9.8, 'os.system(...)')
            
            # A03:2021 - Inyección: subprocess con shell=True
            if nodo.func.attr in ('call', 'run', 'Popen'):
                if isinstance(nodo.func.value, ast.Name) and nodo.func.value.id == 'subprocess':
                    for keyword in nodo.keywords:
                        if keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant):
                            if keyword.value.value is True:
                                self._agregar(nodo, 'A03:2021 - Inyección (subprocess con shell=True)',
                                            'alta', 8.1, f'subprocess.{nodo.func.attr}(..., shell=True)')
            
            # A03:2021 - Inyección: cursor.execute() con concatenación
            if nodo.func.attr == 'execute':
                if isinstance(nodo.func.value, ast.Name) and 'cursor' in nodo.func.value.id.lower():
                    if nodo.args and isinstance(nodo.args[0], ast.BinOp):
                        if isinstance(nodo.args[0].op, ast.Add):
                            self._agregar(nodo, 'A03:2021 - Inyección SQL (concatenación)',
                                        'alta', 8.1, 'cursor.execute(string concatenation)')
            
            # A05:2021 - CORS abierto
            if nodo.func.attr == 'CORS' or (
                isinstance(nodo.func, ast.Attribute) and nodo.func.attr == 'add_middleware'
            ):
                for keyword in nodo.keywords:
                    if keyword.arg == 'allow_origins':
                        if isinstance(keyword.value, ast.List):
                            for elt in keyword.value.elts:
                                if isinstance(elt, ast.Constant) and elt.value == '*':
                                    self._agregar(nodo, 'A05:2021 - CORS abierto (allow_origins=["*"])',
                                                'media', 6.5, 'CORS(allow_origins=["*"])')
            
            # A10:2021 - SSRF: requests/httpx con URL controlada por variable
            if nodo.func.attr in ('get', 'post', 'put', 'delete', 'request', 'fetch'):
                if isinstance(nodo.func.value, ast.Name):
                    if nodo.func.value.id in ('requests', 'httpx', 'urllib'):
                        if nodo.args and isinstance(nodo.args[0], ast.Name):
                            self._agregar(nodo, 'A10:2021 - SSRF (request con URL variable)',
                                        'alta', 8.6, f'{nodo.func.value.id}.{nodo.func.attr}({nodo.args[0].id})')
            
            # A08:2021 - yaml.load() sin Loader seguro
            if nodo.func.attr == 'load':
                if isinstance(nodo.func.value, ast.Name) and nodo.func.value.id == 'yaml':
                    # Es inseguro si no tiene keyword Loader=yaml.SafeLoader
                    tiene_safe_loader = any(
                        kw.arg == 'Loader' and isinstance(kw.value, ast.Attribute)
                        and kw.value.attr == 'SafeLoader'
                        for kw in nodo.keywords
                    )
                    if not tiene_safe_loader:
                        self._agregar(nodo, 'A08:2021 - Deserialización insegura (yaml.load sin SafeLoader)',
                                    'alta', 7.5, 'yaml.load(data)  # falta Loader=yaml.SafeLoader')
        
        # A04:2021 - application.run(debug=True)
        if isinstance(nodo.func, ast.Attribute):
            if nodo.func.attr == 'run':
                for keyword in nodo.keywords:
                    if keyword.arg == 'debug' and isinstance(keyword.value, ast.Constant):
                        if keyword.value.value is True:
                            self._agregar(nodo, 'A04:2021 - Configuración insegura (debug=True)',
                                        'media', 5.3, 'application.run(debug=True)')
        
        self.generic_visit(nodo)

    def visit_Import(self, nodo):
        """Detecta A02:2021 - Librerías vulnerables (import)."""
        for alias in nodo.names:
            # A02:2021 - pickle, marshal, shelve
            if alias.name in ('pickle', 'marshal', 'shelve'):
                self._agregar(nodo, 'A02:2021 - Deserialización insegura',
                            'alta', 7.5, f'import {alias.name}')
            
            # A02:2021 - md5
            if alias.name == 'md5':
                self._agregar(nodo, 'A02:2021 - Algoritmo criptográfico débil (md5)',
                            'media', 5.9, 'import md5')
        
        # A08:2021 - Integridad: jsonpickle
        for alias in nodo.names:
            if alias.name == 'jsonpickle':
                self._agregar(nodo, 'A08:2021 - Deserialización insegura (jsonpickle)',
                            'alta', 7.5, 'import jsonpickle')
        
        self.generic_visit(nodo)

    def visit_ImportFrom(self, nodo):
        """Detecta A02:2021 y A03:2021 - Librerías y módulos vulnerables (from import)."""
        if nodo.module == 'os':
            for alias in nodo.names:
                if alias.name in ('system', 'popen'):
                    self._agregar(nodo, 'A03:2021 - Inyección (importar os.system/popen)',
                                'critica', 9.8, f'from os import {alias.name}')
        
        elif nodo.module == 'subprocess':
            for alias in nodo.names:
                if alias.name in ('call', 'run', 'Popen'):
                    self._agregar(nodo, 'A03:2021 - Inyección (importar subprocess)',
                                'alta', 8.1, f'from subprocess import {alias.name}')
        
        elif nodo.module == 'pickle':
            for alias in nodo.names:
                self._agregar(nodo, 'A02:2021 - Deserialización insegura (pickle)',
                            'alta', 7.5, f'from pickle import {alias.name}')
        
        elif nodo.module == 'hashlib':
            for alias in nodo.names:
                if alias.name in ('md5', 'sha1'):
                    self._agregar(nodo, 'A02:2021 - Algoritmo criptográfico débil (hashlib)',
                                'media', 5.9, f'from hashlib import {alias.name}')
        
        # A08:2021 - yaml.load sin SafeLoader
        elif nodo.module == 'yaml':
            for alias in nodo.names:
                if alias.name == 'load':
                    self._agregar(nodo, 'A08:2021 - Deserialización insegura (yaml.load)',
                                'alta', 7.5, 'from yaml import load')
        
        self.generic_visit(nodo)

    def visit_Assign(self, nodo):
        """Detecta A07:2021 - Variables secretas almacenadas en el código."""
        palabras_sensibles = ('password', 'passwd', 'secret', 'api_key', 'token', 'pwd', 'jwt', 'private_key')
        
        for target in nodo.targets:
            if isinstance(target, ast.Name):
                nombre_var = target.id.lower()
                if any(palabra in nombre_var for palabra in palabras_sensibles):
                    if isinstance(nodo.value, ast.Constant) and isinstance(nodo.value.value, str):
                        if nodo.value.value:  # No vacío
                            self._agregar(nodo, 'A07:2021 - Información sensible en el código',
                                        'alta', 7.5, f'{target.id} = \'***\'')
        
        # A05:2021 - Configuración insegura: variables de config con valores peligrosos
        for target in nodo.targets:
            if isinstance(target, ast.Name):
                nombre_lower = target.id.lower()

                # DEBUG = True
                if nombre_lower == 'debug':
                    if isinstance(nodo.value, ast.Constant) and nodo.value.value is True:
                        self._agregar(nodo, 'A05:2021 - Configuración insegura (DEBUG=True)',
                                    'media', 5.3, f'{target.id} = True')

                # ALLOWED_HOSTS = ["*"] o similar
                if nombre_lower == 'allowed_hosts':
                    if isinstance(nodo.value, (ast.List, ast.Tuple)):
                        for elt in nodo.value.elts:
                            if isinstance(elt, ast.Constant) and elt.value == '*':
                                self._agregar(nodo, 'A05:2021 - Configuración insegura (ALLOWED_HOSTS=*)',
                                            'media', 5.3, f'{target.id} = ["*"]')
        
        self.generic_visit(nodo)

    def visit_ExceptHandler(self, nodo):
        """Detecta A04:2021 - Exposición de información en bloques except."""
        if nodo.name:  # Solo si tiene variable de excepción (as e)
            # Buscar print(exception)
            for child in ast.walk(nodo):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name) and child.func.id == 'print':
                        for arg in child.args:
                            if isinstance(arg, ast.Name) and arg.id == nodo.name:
                                self._agregar(nodo, 'A04:2021 - Exposición de información (print en except)',
                                            'baja', 3.1, f'print({nodo.name})')
                
                # Buscar return str(exception) o repr(exception)
                elif isinstance(child, ast.Return):
                    if child.value and isinstance(child.value, ast.Call):
                        if isinstance(child.value.func, ast.Name):
                            if child.value.func.id in ('str', 'repr'):
                                if child.value.args and isinstance(child.value.args[0], ast.Name):
                                    if child.value.args[0].id == nodo.name:
                                        self._agregar(nodo, 'A04:2021 - Exposición de información (return en except)',
                                                    'baja', 3.1, f'return {child.value.func.id}({nodo.name})')
        
        self.generic_visit(nodo)


def analizar_contenido(contenido: str, nombre_archivo: str) -> list[VulnerabilidadDetectada]:
    """Función de entrada del motor de análisis estático.
    
    Args:
        contenido: Código fuente a analizar
        nombre_archivo: Nombre del archivo (para reportes)
    
    Returns:
        Lista de vulnerabilidades detectadas
    """
    try:
        tree = ast.parse(contenido, filename=nombre_archivo)
    except SyntaxError as e:
        return [VulnerabilidadDetectada(
            tipo_owasp="Error de sintaxis - no se pudo analizar",
            severidad="baja",
            score_cvss=0.0,
            codigo_vulnerable=str(e),
            linea_codigo=e.lineno or 0,
            fragmento_codigo=""
        )]
    
    lineas = contenido.splitlines()
    motor = MotorAST(lineas)
    motor.visit(tree)
    return motor.vulnerabilidades
