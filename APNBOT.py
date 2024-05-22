import os
import fitz  # PyMuPDF
from transformers import BertTokenizer, BertModel
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker
import torch
import tkinter as tk
from tkinter import ttk

Base = declarative_base()


# Definición de la tabla de textos
class Texto(Base):
    __tablename__ = 'textos'
    id = Column(Integer, primary_key=True)
    ruta_archivo = Column(String, unique=True)
    texto_procesado = Column(LargeBinary)


# Función para leer texto de un archivo PDF
def leer_pdf(ruta_archivo):
    try:
        doc = fitz.open(ruta_archivo)
        texto = ""
        for pagina in doc:
            texto += pagina.get_text()
        print(f"Leído PDF: {ruta_archivo}")
        return texto
    except Exception as e:
        print(f"Error al leer el PDF: {e}")
        return ""


# Función para procesar texto con BERT
def procesar_texto(texto, tokenizador, modelo):
    try:
        entradas = tokenizador(texto, return_tensors="pt", truncation=True, padding=True, max_length=512)
        salidas = modelo(**entradas)
        print("Texto procesado con BERT.")
        return salidas.last_hidden_state
    except Exception as e:
        print(f"Error al procesar el texto: {e}")
        return None


# Función para almacenar o actualizar resultados en una base de datos
def almacenar_o_actualizar_bd(ruta_archivo, texto_procesado, db_url="sqlite:///textos_procesados.db"):
    try:
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Convertir tensor a bytes para almacenamiento
        texto_procesado_bytes = texto_procesado.detach().numpy().tobytes()

        # Verificar si el archivo ya existe
        archivo_existente = session.query(Texto).filter_by(ruta_archivo=ruta_archivo).first()

        if archivo_existente:
            # Actualizar el registro existente
            archivo_existente.texto_procesado = texto_procesado_bytes
            session.commit()
            print(f"Texto actualizado en la base de datos para el archivo: {ruta_archivo}")
        else:
            # Insertar un nuevo registro
            nuevo_texto = Texto(ruta_archivo=ruta_archivo, texto_procesado=texto_procesado_bytes)
            session.add(nuevo_texto)
            session.commit()
            print(f"Texto almacenado en la base de datos para el archivo: {ruta_archivo}")

        session.close()
    except Exception as e:
        print(f"Error al almacenar o actualizar en la base de datos: {e}")


# Función principal para procesar múltiples archivos PDF en una carpeta
def procesar_pdfs_en_carpeta(ruta_carpeta):
    # Inicializar tokenizador y modelo
    tokenizador = BertTokenizer.from_pretrained('bert-base-uncased')
    modelo = BertModel.from_pretrained('bert-base-uncased')

    for archivo in os.listdir(ruta_carpeta):
        if archivo.endswith(".pdf"):
            ruta_archivo = os.path.join(ruta_carpeta, archivo)
            print(f"Procesando archivo: {ruta_archivo}")
            # Leer PDF
            texto = leer_pdf(ruta_archivo)

            if texto:
                # Procesar texto
                texto_procesado = procesar_texto(texto, tokenizador, modelo)

                if texto_procesado is not None:
                    # Almacenar o actualizar resultados en la base de datos
                    almacenar_o_actualizar_bd(ruta_archivo, texto_procesado)


# Función para listar archivos procesados en la base de datos
def listar_archivos_procesados(db_url="sqlite:///textos_procesados.db"):
    try:
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        archivos = session.query(Texto).all()
        data = [(archivo.id, archivo.ruta_archivo) for archivo in archivos]
        session.close()
        return data
    except Exception as e:
        print(f"Error al listar los archivos: {e}")
        return []


# Función para obtener texto procesado desde la base de datos
def obtener_texto_procesado(ruta_archivo, db_url="sqlite:///textos_procesados.db"):
    try:
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        archivo = session.query(Texto).filter_by(ruta_archivo=ruta_archivo).first()
        if archivo:
            texto_procesado = torch.tensor(list(archivo.texto_procesado))
            print(f"Texto procesado para {ruta_archivo}: {texto_procesado}")
        else:
            print(f"No se encontró el archivo {ruta_archivo} en la base de datos.")
        session.close()
    except Exception as e:
        print(f"Error al obtener el texto procesado: {e}")


# Función para mostrar la base de datos en una ventana de Tkinter
def mostrar_base_de_datos():
    data = listar_archivos_procesados()
    root = tk.Tk()
    root.title("Base de Datos de Textos Procesados")

    tree = ttk.Treeview(root, columns=("ID", "Ruta"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Ruta", text="Ruta del Archivo")

    for item in data:
        tree.insert("", "end", values=item)

    tree.pack(expand=True, fill="both")
    root.mainloop()


# Ejemplo de uso
if __name__ == "__main__":
    try:
        ruta_carpeta = "D:\\BOLETIN OFICIAL"
        procesar_pdfs_en_carpeta(ruta_carpeta)
        mostrar_base_de_datos()
    except KeyboardInterrupt:
        print("Proceso interrumpido por el usuario.")


# Casos de prueba
def test_leer_multiples_pdfs():
    ruta_carpeta = "D:\\BOLETIN OFICIAL"
    for archivo in os.listdir(ruta_carpeta):
        if archivo.endswith(".pdf"):
            ruta = os.path.join(ruta_carpeta, archivo)
            texto = leer_pdf(ruta)
            assert isinstance(texto, str) and len(texto) > 0


def test_procesar_multiples_textos():
    ruta_carpeta = "D:\\BOLETIN OFICIAL"
    tokenizador = BertTokenizer.from_pretrained('bert-base-uncased')
    modelo = BertModel.from_pretrained('bert-base-uncased')
    for archivo in os.listdir(ruta_carpeta):
        if archivo.endswith(".pdf"):
            ruta = os.path.join(ruta_carpeta, archivo)
            texto = leer_pdf(ruta)
            texto_procesado = procesar_texto(texto, tokenizador, modelo)
            assert texto_procesado is not None


def test_almacenar_multiples_en_bd():
    ruta_carpeta = "D:\\BOLETIN OFICIAL"
    tokenizador = BertTokenizer.from_pretrained('bert-base-uncased')
    modelo = BertModel.from_pretrained('bert-base-uncased')
    for archivo in os.listdir(ruta_carpeta):
        if archivo.endswith(".pdf"):
            ruta = os.path.join(ruta_carpeta, archivo)
            texto = leer_pdf(ruta)
            texto_procesado = procesar_texto(texto, tokenizador, modelo)
            almacenar_o_actualizar_bd(ruta, texto_procesado)

    # Verificar que todos los textos se almacenaron correctamente
    engine = create_engine("sqlite:///textos_procesados.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    for archivo in os.listdir(ruta_carpeta):
        if archivo.endswith(".pdf"):
            ruta = os.path.join(ruta_carpeta, archivo)
            resultado = session.query(Texto).filter_by(ruta_archivo=ruta).first()
            assert resultado is not None


if __name__ == "__main__":
    try:
        test_leer_multiples_pdfs()
        test_procesar_multiples_textos()
        test_almacenar_multiples_en_bd()
    except KeyboardInterrupt:
        print("Pruebas interrumpidas por el usuario.")