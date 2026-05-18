def es_palindromo(texto):
  texto=texto.replace(" ","").lower()
  longitud_texto=len(texto)-1
  i=0
  while longitud_texto>=0:
    if texto[longitud_texto] == texto[i]:
      i+=1
      longitud_texto-=1
    else:
      return False
  return True   

print("ana",es_palindromo("ana"))
print("abba",es_palindromo("abba"))
print("hola",es_palindromo("hola"))
print("Amo la paloma",es_palindromo("Amo la paloma"))
print("ana lava lana",es_palindromo("ana lava lana"))

