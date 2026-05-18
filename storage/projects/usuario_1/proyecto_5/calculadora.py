primer_numero= input("Ingrese el primer número: ")
segundo_numero = input("Ingrese el segundo número: ")

if '.' not in primer_numero and '.' not in segundo_numero:
    primer_numero= int(primer_numero)
    segundo_numero= int(segundo_numero)
elif "." in primer_numero and "." in segundo_numero:
    primer_numero= float(primer_numero)
    segundo_numero=float(segundo_numero)
elif "." in primer_numero and "." not in segundo_numero:
    primer_numero= float(primer_numero)
    segundo_numero=int(segundo_numero)
else:
    primer_numero= int(primer_numero)
    segundo_numero=float(segundo_numero)

suma= primer_numero + segundo_numero
resta= primer_numero - segundo_numero
multiplicacion= primer_numero * segundo_numero
division= primer_numero / segundo_numero

mensaje=f"""
para los numeros {primer_numero} y {segundo_numero}
el resultado de la suma es {suma}
el resultado de la resta es {resta}
el resultado de la multiplicacion es {multiplicacion}
el resultado de la division es {division}
 """
print(mensaje)