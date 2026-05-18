# repaso  de cadenas 
"""cadena = input("ingrese una palabra al programa: ")
print("estas son algunas operaciones que se puede hacer en las cadenas ")
print(f"podemos convertir a mayusculas la palabra {cadena} y se veria asi: ")
print(cadena.upper())
print(f"podemos convertir a minusculas la palabra {cadena} y se veria asi: ")
print(cadena.lower())
print(f"podemos convertir la primera letra de la palabra {cadena}" 
      +"en mayuscula y se veria asi: ")
print(cadena.capitalize())
print("podemos convertir la primera letra de cada palabra en mayuscula de"+
      f"la palabra {cadena} y se veria asi: ")
print(cadena.title())
print("puedo quitar los espacios en blanco de la derecha" 
      +f"de la palabra {cadena}")
print(cadena.rstrip())
print("puedo quitar los espacios en blanco de la izquierda" 
      +f"de la palabra {cadena}")
print(cadena.lstrip())
print(f"puedo quitar los espacios en blanco de la palabra {cadena}")
print(cadena.strip())
cadena2= input(f"ingrese una palabra para buscar dentro de la palabra {cadena}")
print(f"puedo buscar la palabra {cadena2} dentro de la palabra {cadena} y se encuentra en la posicion: ")
print(cadena.find(cadena2))
cadena2 = input(f"ingrese la palabra que desea  reemplazar dentro de la palabra {cadena}")
cadena3 =input(f"ingrese la nueva palabra que reemplazara dentro de la palabra {cadena2}:")
print(f"la palabra {cadena2} sera reemplazada por la palabra {cadena3} dentro de cadena: ")
print(cadena.replace(cadena2,cadena3))
cadena2=input(f"ingresa una palabra para verificar si esta dentro de la palabra {cadena}: ")
print(f"la palabra {cadena2} se encuentra dentro de la palabra {cadena}")
print(cadena2 in cadena)

print(f"haremos rebanadas de la palabra {cadena} sirve negativos")
try:
 i =int(input(f"ingrese un valor que este entre el rango de 0 a {len(cadena)-1}"))
except ValueError:
 i=0
j=int(input(f"ingrese un valor que este entre el rango de 0 a {len(cadena)-1}"))   
if i<0:
 j=-j
print(cadena[i::j])
"""
"""lista_numeros =[]
contador_fallos=0
contador=1
while contador<=3:
 try: 
   numero =int(input("ingrese un numero para agregar a la lista: "))
   lista_numeros.append(numero)
   contador+=1
 except ValueError:
   contador_fallos+=1
   print(f"error ingrese numeros no otros caracteres {contador_fallos} veces")    
 if contador_fallos==3:
   print("has cometido 3 errores, el programa se cerrara")
   break
print(f"la lista quedo: {lista_numeros}")

try:
 x = int(input(f"ingrese un valor que este entre el rango de 0 a {len(lista_numeros)-1}"))
 y = int(input(f"ingrese un valor que este entre el rango de 0 a {len(lista_numeros)-1}"))
 z = int(input(f"ingrese un valor que este entre el rango de 0 a {len(lista_numeros)-1}"))
except ValueError:
 print(lista_numeros[::])
else:
   print(lista_numeros[x:y:z])
"""
# retos del canal de mirudev

# reto 1 challenge four fantastic  
"""def challenge_four_fantastic(cadena:str)->bool :
 '''es contar en una cadena las R y J si son
 iguales true o si no hay ninguna , caso contrario false'''
 cadena = cadena.upper()
 contador_R = cadena.count("R")
 contador_J = cadena.count("J")
 return contador_R == contador_J

print(challenge_four_fantastic("RJRJ"))
"""
#reto 2 hacer una funcion que reciba una lista y un numero goal
# y retorne en una lista las posiciones de los primeros 2 numeros que sumados
# den el numero goal
"""def find_first_sum(nums,goal):
 visitados = {}
 for posicion, numero in enumerate(nums):
   complemento = goal - numero
   if complemento in visitados:
     return [visitados[complemento],posicion] 
   visitados[numero] = posicion 
 return None

def find_first_sum2(nums,goal):
  '''es lo mismo pero que encuentra las posicionces
  de los numeros que sumados den el numero goal pero 
  que sean los primeros en aparecer'''
  for pos,valor in enumerate(nums):
    nuevo_goal = goal - valor 
    if nuevo_goal > 0:
      result = find_first_suma(pos+1,nums,nuevo_goal)
      if not result is []:
        result.append(pos)
        result = result[::-1]
        return result
  return None

def find_first_suma(posicion_actual,nums,goal_actual):
  '''es una funcion recursiva que busca 
  el complemento del numero actual'''
  if goal_actual == 0:
    return []
  if (goal_actual < 0) or (posicion_actual >= len(nums)):
    return None
  result = find_first_suma(posicion_actual+1,nums,goal_actual - nums[posicion_actual])
  if result is not None:
      result.append(posicion_actual)
      return result
  return find_first_suma(posicion_actual+1,nums,goal_actual)

def battle(lista_A,lista_B):
 diferencia = sum(lista_A) - sum(lista_B)
 if diferencia == 0:
   return "x"
 ganador ="A" if diferencia > 0 else "B"     
 return f"{abs(diferencia)} {ganador} "
 
print("el de dos numeros: ",find_first_sum([4,5,9,1,2],18))
print("el que estuve haciendo: ",find_first_sum2([4,5,9,1,2],18))
print("el que estuve haciendo: ",find_first_sum2([4,5,9,1,2],20))
print("el battle: ",battle([1,2,3],[4,5,6]))
"""
# regex 
import re
pattern = "hola"
cadena = "hola mundo"
result = re.search(pattern,cadena)
if result:
  print("se encontro la palabra")
else:
  print("no se encontro la palabra")

def validar_correo(correo):
  patron = r"^([a-zA-Z0-9_\-\.]+)@(\w+)\.(\w{2,3})$"
  verificador_correo = re.match(patron,correo)
  if verificador_correo:
    print(f"felicitaciones el correo {correo} es valido")
  else:
    print(f"lo siento pero el correo {correo} no es valido vuelve a intentar")

def validar_contraseña(contraseña):
  '''es una funcion que valida que la contraseña sea de al menos 8 caracteres
  y que contenga al menos una letra mayuscula una letra minuscula y un numero'''
  patron = r"^(?=.*[a-z])(?=.*\d)(?=.*[A-Z]).{8,}$"
  verificador_contraseña  = re.match(patron,contraseña)
  print("contraseña valida se encriptara") if verificador_contraseña else print("Error la contraseña no cumple con los requisitos")   


print("para crear una cuenta debe ingresar su correo electronico y una contraseña")
correo = input("ingrese su correo: ")
print("la contraseña debe tener al menos 8 caracteres, una letra mayusucla una letra minuscula y un numero")
contraseña = input("ingrese su contraseña: ")
validar_correo(correo)
validar_contraseña(contraseña)
text = "Este es el curso de Python de midudev. ¡Sucribete a midudev si te gusta este contenido! midu"
patron = "midu"
result = re.finditer(patron,text)
contador=0
for match in result:
  contador+=1 
  print(f"se encontro la palabra {match.group()} en la posicion {match.start()} y terminaba en {match.end()}")
print(f"se encontro la palabra {patron}: {contador} ")  

#ejercicio
# tnenemos una lista de archivos, necesitamos saber los nombres de los ficheros con extesion txt

archivos = "file1.txt file2.pdf midu-of.webp secret.txt"
print(f"debemos mostrar lo nombres de los archivos con extension txt de {archivos}")
patron = r"[\w\-]+\.txt"  
result = re.findall(patron,archivos)
print(result)    

# ejercicio 
# cuantas palabras tienen 0 a mas "a" y despues una b?
texto = "b ab aab aaab aaaab"
patron = r"\ba*b\b"
result = re.findall(patron,texto)
print(len(result))
"""
# fechas 
from datetime import datetime,timedelta
print(datetime.now())
# si queremos especificar una fecha en particular
fecha_especifica = datetime(2003,3,9)
print(f"fecha especifica:{fecha_especifica}") 

formato_fecha = datetime.now().strftime("%d/%m/%Y")
print(f"fecha con formato: {formato_fecha}")

# operaciones con fechas

ayer = datetime.now() - timedelta(days=1)
print(f"el dia de ayer fue: {ayer}")
mañana = datetime.now() + timedelta(days=1)
print(f"el dia de mañana sera: {mañana}")

# diferencia de fechas 
fecha1 = datetime.now()
fecha2= datetime(2026,4,1)
diferencia = fecha1 - fecha2
print(f"la diferencia entre las fechas es: {diferencia}")

import locale
locale.setlocale(locale.LC_TIME,"es_BO.UTF-8")
fecha_formato = datetime.now().strftime("%A %d de %B del %Y")
print(f"fecha con formato en español: {fecha_formato}")

#como hacer peticiones a apis con python
#con y sin dependencias

# 1 sin dependencia
import urllib.request
import json 

api_posts ="https://jsonplaceholder.typicode.com/posts/"
try:
 respuesta = urllib.request.urlopen(api_posts)
 datos = respuesta.read()
 json_datos = json.loads(datos.decode("utf-8"))
 print(json_datos)
 respuesta.close()
except urllib.error.URLError as e:
  print(f"error al hacer la peticion: {e.reason}")
"""
# 2 con dependecia (requests)
"""import requests

print("\n GET: ")
api_posts ="https://jsonplaceholder.typicode.com/posts/"
respuesta = requests.get(api_posts)
json = respuesta.json()
print(json)
print(json[0])

# 3 un post
print("\n POST:")
try:
 api_posts ="https://jsonplaceholder.typicode.com/posts/"
 input = {
   "title": "prueba de post",
   "body": "esto es una prueba si funciona el post con requests",
   "userId": "10" 
 }
 respuesta  = requests.post(api_posts,json=input)
 print(respuesta.json()) 
 print(respuesta.status_code)
except requests.exceptions.RequestException as e:
 print(f"error al hacer la peticion: {e}")

#4 PUT
print("\n PUT:")
try:
 api_posts ="https://jsonplaceholder.typicode.com/posts/1"
 input = {
   "title": "prueba de post",
   "body": "esto es una prueba si funciona el post con requests",
   "userId": "10", 
   "id": "1"
 }
 respuesta  = requests.put(api_posts,json=input)
 print(respuesta.json()) 
 print(respuesta.status_code)
except requests.exceptions.RequestException as e:
 print(f"error al hacer la peticion: {e}") 

# usar la api de GPT-4o de OpenAI 
def call_openai_gpt(api_key,prompt):
 url= "https://api.openai.com/v1/chat/completions"
 headers = {
   "content-Type": "application/json",
   "Authorization": f"Bearer {api_key}"
  }
 data = {
   "model": "gpt-4o-mini",
   "messages": [{"role":"user","content": prompt}] 
 } 
 response = requests.post(url,json=data, headers=headers)
 print(response.json())

OPENAI_API_KEY = "sk-xxxxxxxx"
call_openai_gpt(OPENAI_API_KEY,"dime los tipos de datos que tiene python")

# usar la api de deepseek  
def call_deepseek(api_key,prompt):
 url= "https://api.deepseek.com/chat/completions"
 headers = {
   "content-Type": "application/json",
   "Authorization": f"Bearer {api_key}"
  }
 data = {
   "model": "deepseek-chat",
   "messages": [{"role":"user","content": prompt}] 
 } 
 response = requests.post(url,json=data, headers=headers)
 print(response.json())

DEEPSEEK_API_KEY = "sk-xxxxxxxx"
call_deepseek(DEEPSEEK_API_KEY,"dime los tipos de datos que tiene python")
"""
#clases 
"""class Coche:
  tipo = "vehiculo de cuatro ruedas"

  def __init__(self,marca,modelo,color):
    self.marca= marca
    self.modelo=modelo
    self.color=color

  def arrancar(self):
    print(f"el coche {self.marca} {self.modelo} arranco")


mi_coche = Coche("toyota","corolla","rojo")
mi_coche.arrancar()
"""
# web scraping  con regex
print("web scraping con regex")
import requests 
import re

url = "https://books.toscrape.com/"
respuestas = requests.get(url)
if respuestas.status_code == 200:
  print("felcidades se pudo hacer web scraping")
  respuestas.encoding = "uft-8"
  html = respuestas.text
  #usaremos una regex para extraer de la pagina
  patron = r'<p class="price_color">.(\d+\.\d{2})</p>'
  resultados = re.findall(patron,html)
  print(resultados)

 #web scarping con beatifulsoup
import requests
from bs4 import BeautifulSoup
url = "https://books.toscrape.com/"
respuesta = requests.get(url)
respuesta.encoding = "utf-8"
sopa = BeautifulSoup(respuesta.text,"html.parser")
precios = sopa.find_all("p",class_="price_color")
precios_libros =  [precio.text[1:] for precio in precios]
print(precios_libros)

# wiki scraper
print("wiki scraper")
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://books.toscrape.com/"
respuesta = requests.get(url)
enlaces = BeautifulSoup(respuesta.text,"html.parser").find_all("a")

lista_enlaces = [urljoin(url,enlace.get("href")) for enlace in enlaces]
print(lista_enlaces)

# prueba para pintar la consola de colores
print("\033[31m] esto sera un texto rojo \033[0m]")
input("\033[32m esto sera un texto verde \033[0m")

# playwright

# para crear entornos virtuales en python usando venv

# comandos
# python -m venv .venv (.venv es una conveccion pero no es obligatoria)
