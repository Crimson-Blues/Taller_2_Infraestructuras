from PIL import Image
import os
import time
import multiprocessing
import numpy as np

def convertir_a_gris(ruta_imagen):
    """Convierte una imagen a escala de grises."""
    try:
        imagen = Image.open(ruta_imagen)
        imagen_gris = imagen.convert('L') # 'L' representa escala de grises
        nombre_archivo, extension = os.path.splitext(ruta_imagen)
        ruta_gris = nombre_archivo + "_gris" + extension
        imagen_gris.save(ruta_gris)
        #print(f"Imagen convertida: {ruta_imagen} -> {ruta_gris}")
    except FileNotFoundError:
        print(f"Error: No se encontró la imagen {ruta_imagen}")
    except Exception as e:
        print(f"Error al procesar {ruta_imagen}: {e}")

def procesar_imagenes_secuencial(lista_imagenes):
    """Procesa una lista de imágenes secuencialmente."""
    for ruta_imagen in lista_imagenes:
        convertir_a_gris(ruta_imagen)

def procesar_imagenes_paralelo(lista_imagenes):
    """Procesa una lista de imágenes empleando paralelización
    por dominio: Se divide la totalidad de la lista de imágenes
    en sublistas que se procesan de forma paralela por procesos 
    independientes."""

    #Número de procesos a correr el paralelos
    num_procesos = 5 #Número de núcleos en procesador
    tamano_chunk = len(lista_imagenes) // num_procesos

    # Lista para almacenar procesos
    procesos = []

    #No es necesarioa queue de resultados dado que la función convertir_a_gris guarda las imágenes

    for i in range(num_procesos):
        inicio_chunk = i * tamano_chunk
        fin_chunk = (i + 1) * tamano_chunk if i < num_procesos - 1 else len(lista_imagenes)
        chunk = lista_imagenes[inicio_chunk:fin_chunk]
        p = multiprocessing.Process(target=procesar_imagenes_secuencial, args=(chunk,))
        procesos.append(p)
        p.start()

    # Esperar a que todos los procesos terminen
    for p in procesos:
        p.join()
    
            
if __name__ == '__main__':
    directorio_imagenes = "cats_from_memes" 
    lista_imagenes = [os.path.join(directorio_imagenes, f) for f in os.listdir(directorio_imagenes) if os.path.isfile(os.path.join(directorio_imagenes, f))]
    inicio_sec = time.time()
    procesar_imagenes_secuencial(lista_imagenes)
    fin_sec = time.time()
    t_sec = fin_sec - inicio_sec
    print(f"Tiempo total de procesamiento secuencial: {t_sec:.3f} segundos")

    inicio_par = time.time() #Empezar a contabilizar tiempo de solución paralela
    procesar_imagenes_paralelo(lista_imagenes)
    fin_par = time.time()  # Tiempo de fin de solució paralela
    t_par = fin_par - inicio_par
    print(f"Tiempo total de procesamiento paralelo: {t_par:.3f} segundos")
    print(f"Speedup: {t_sec/t_par:.2f}x" )