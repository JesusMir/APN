import PyPDF2
import os
import difflib

#Funcion para leer un PDF y devolverlo como texto
def leer_pdf(ruta_pdf):
    with open(ruta_pdf, 'rb') as archivo_pdf:
        lector_pdf = PyPDF2.PdfReader(archivo_pdf)
        texto = ""
        for pagina_numero in range(len(lector_pdf.pages)):
            pagina = lector_pdf.pages[pagina_numero]
            texto += pagina.extract_text() + "\n"
    return texto

#Funcion para comparar dos textos y devolver las diferencias
def comparar_texto(texto1, texto2):
    diferencia = difflib.ndiff(texto1.splitlines(), texto2.splitlines())
    return traducir(diferencia) #Esto es para la funcion de abajo

#Funcion para simplificar las diferencias entre los textos
def traducir(diferencia):
    pass  #COMPLETAR PERO NO SE BIEN QUE HACER

#Ruta de la carpeta donde estan los archivos PDF CAMBIENLO USTEDES MUCHACHOS
ruta_carpeta = "D:\\BOLETIN OFICIAL"

#Obtiene la lista de archivos PDF en la carpeta y ordena alfabrticamente
archivos_pdf = sorted([archivo for archivo in os.listdir(ruta_carpeta) if archivo.endswith(".pdf")])

#Mapea los nombres de los archivos PDF a los textos con los que se van a comparar
textos_a_comparar = {
    "1.pdf": "comparar 1",
    "2.pdf": "comparar 2",
    "3.pdf": "comparar 3",
    "4.pdf": "comparar 4"
}

print("Archivos PDF encontrados:")
print(archivos_pdf)

#Lista de archivos PDF que no se lereyon
archivos_no_leidos = []

#Lee y compara el contenido de cada archivo PDF con otro
for nombre_archivo_pdf in archivos_pdf[:]:  #Usam una copia de la lista para poder modificarla en el loop
    ruta_archivo = os.path.join(ruta_carpeta, nombre_archivo_pdf)
    if nombre_archivo_pdf in textos_a_comparar:
        # Leer el contenido del archivo PDF
        texto_pdf = leer_pdf(ruta_archivo)

        #Texto con el que se va a comparar el PDF
        texto_a_comparar = textos_a_comparar[nombre_archivo_pdf]

        #Comparar texto A con texto B
        diferencias = comparar_texto(texto_pdf, texto_a_comparar)

        # Mostrar las diferencias
        print(f"Diferencias en el archivo {nombre_archivo_pdf}:")
        print(diferencias)

        #Elimina el archivo de la lista
        archivos_pdf.remove(nombre_archivo_pdf)

#Print en consola de los nombres de los archivos que no fueron leídos
print("Archivos no leídos:")
for archivo in archivos_no_leidos:
    print(archivo)

#Print final para verificar
if archivos_no_leidos:
    print("Aca hubo un problemita.")
else:
    print("Todo piola rey")

# NOTA 1: Poco codigo quedo, originalmente eran 100 y algo lineas pero lo pase por chatgpt para que no se me caguen
#         de risa, prefiero pasar mas tiempo investigando y menos escribiendo codigo sin saber bien que hacer
# NOTA 2: La funcion para traducir y simplificar el codigo la deje ahi sin hacer nada, y el codigo va a devolver
#         ninguna diferencia, si quieren probar si devuelve las diferencias pueden borrar la funcion