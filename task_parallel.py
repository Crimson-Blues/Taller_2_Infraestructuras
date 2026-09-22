import time
import os 
import multiprocessing

line_status = None

def procesar_texto_secuencial(ruta_entrada, ruta_salida):
    """Procesa el archivo de texto secuencialmente."""
    try:
        with open(ruta_entrada, 'r') as f_in, open(ruta_salida, 'w') as f_out:
            for linea in f_in:
                linea_limpia = linea.strip()
                linea_mayusculas = linea_limpia.upper()
                f_out.write(linea_mayusculas + '\n')
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_entrada}")


def leer(input_path, output_queue):
    """
    etapa 1: lee el archivo linea por linea y la pasa a la siguiente etapa
    """
    with open(input_path, 'r') as f:
        for line in f:
            output_queue.put(line)

    output_queue.put(line_status)

def limpiar(input_queue, output_queue):
    """
    etapa 2: quita espacio al inicio y al final de cada linea y la pasa a la siguiente etapa
    """
    while True:
        line = input_queue.get()
        if line is line_status:
            output_queue.put(line_status)
            break
        output_queue.put(line.strip())


def mayusculas(input_queue, output_queue):
    """
    etapa 3: convierte cada linea a mayusculas y la pasa a la siguiente etapa
    """
    while True:
        line = input_queue.get()
        if line is line_status:
            output_queue.put(line_status)
            break
        output_queue.put(line.upper())

def escribir(input_queue, output_path):
    """
    etapa 4: escribe cada linea en el archivo final
    """
    with open(output_path, 'w') as f:
        while True:
            line = input_queue.get()
            if line is line_status:
                break
            f.write(line + '\n')
            

if __name__ == '__main__':
    texts_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "texts")
    os.makedirs(texts_folder, exist_ok=True) 

    input_path = os.path.join(texts_folder, "text_input.txt")
    sequential_output_path = os.path.join(texts_folder, "text_output_sequential.txt")
    parallel_output_path = os.path.join(texts_folder, "text_output_parallel.txt")

    # borrar txt de corridas anteriores, para que cada ejecucion sea limpia
    for ruta in (sequential_output_path, parallel_output_path):
        if os.path.exists(ruta):
            os.remove(ruta)

    # una cola por cada conexion entre etapas
    cola_1 = multiprocessing.Queue()  # leer -> limpiar
    cola_2 = multiprocessing.Queue()  # limpiar -> mayusculas
    cola_3 = multiprocessing.Queue()  # mayusculas -> escribir

    # un proceso por cada etapa del pipeline
    p1 = multiprocessing.Process(target=leer, args=(input_path, cola_1))
    p2 = multiprocessing.Process(target=limpiar, args=(cola_1, cola_2))
    p3 = multiprocessing.Process(target=mayusculas, args=(cola_2, cola_3))
    p4 = multiprocessing.Process(target=escribir, args=(cola_3, parallel_output_path))

    inicio_tareas = time.time()
    for p in (p1, p2, p3, p4):
        p.start()  # lanza los 4 procesos, no espera a que terminen
    for p in (p1, p2, p3, p4):
        p.join()  # aqui si espera a que cada uno termine
    fin_tareas = time.time()

    t_paralelo = fin_tareas - inicio_tareas

    inicio_secuencial = time.time()
    procesar_texto_secuencial(input_path, sequential_output_path)
    fin_secuencial = time.time()

    t_secuencial = fin_secuencial - inicio_secuencial

    print(f"\nTiempo total de procesamiento por pipeline: {t_paralelo:.3f} segundos")

    print(f"\nTiempo total de procesamiento secuencial: {t_secuencial:.3f} segundos")

    print(f"\nSpeedup: {t_secuencial/t_paralelo:.2f}x")

    # compara el contenido de ambas salidas para verificar que el pipeline hizo lo mismo que el secuencial
    with open(sequential_output_path, 'r') as f1, open(parallel_output_path, 'r') as f2:
        contenido_secuencial = f1.read()
        contenido_paralelo = f2.read()

    if contenido_secuencial == contenido_paralelo:
        print("\nLos archivos de salida son iguales. El pipeline produce el mismo resultado que el secuencial.")
    else:
        print("\nLos archivos de salida son diferentes. Revisa la lógica del pipeline.")