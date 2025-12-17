# pyright: basic
import random, os

NUM_ARCHIVOS = 200 # Nuemero de archivos que se quieran crear
MAX_C = 100 # Máxima c que se pueda generar
MAX_M = 50 # Máxima m que se pueda generar
MAX_K = 10 # Máxima k que se pueda generar

BORRAR = False # 'False' si quieres generar las entradas, 'True' si las quieres eliminar pero has creado tantas que te da palo hacerlo a mano

def random_biased(c):
    # Parámetros adaptativos:
    #   - Si c es grande → distribución muy inclinada hacia la izquierda (n pequeño)
    #   - Si c es pequeño → distribución más centrada
    a = 2
    b = max(2, c / 5)  # si c crece, b crece → sesgo hacia valores pequeños

    x = random.betavariate(a, b)
    n = int(x * (c - 2))
    return n

def generar_input_string(max_coches, max_mejoras, max_clases, max_cantidad_clase=10):
    # Elegir cantidades aleatorias
    m = random.randint(3, max_mejoras)
    k = random.randint(3, max_clases)
    
    # Escoger cantidad por clase primero, luego sumarlas
    c = 0
    while not 0 < c <= max_coches:
        cantidades = [random.randint(1, max_cantidad_clase) for _ in range(k)]
        c = sum(cantidades)

    # Generar ce y ne con ce <= ne
    ce = []
    ne = []
    for _ in range(m):
        ni = 2 + random_biased(c)
        ci = random.randint(1, ni - 1)
        ce.append(ci)
        ne.append(ni)

    # Generar clases
    clases = []
    for i in range(k):
        mejoras = [random.randint(0, 1) for _ in range(m)]
        clases.append((i, cantidades[i], mejoras))

    # Construir string de salida
    out = []
    out.append(f"{c} {m} {k}")
    out.append(" ".join(map(str, ce)))
    out.append(" ".join(map(str, ne)))
    for cl_id, cantidad, mejoras in clases:
        out.append(f"{cl_id} {cantidad} " + " ".join(map(str, mejoras)))

    return "\n".join(out)


def generar_archivos(num_archivos, c, m, k):
    ret = []
    for i in range(1, num_archivos + 1):
        contenido = generar_input_string(c, m, k)
        nombre = f"public_benchs/extra-{i}.txt"
        with open(nombre, "w") as f:
            f.write(contenido)
        print(f"Archivo generado: {nombre}")
        ret.append(nombre)
    return ret

if __name__ == "__main__":
    if BORRAR:
        i = 1
        try:
            while True:
                os.remove(f"public_benchs/extra-{i}.txt")
                i += 1
        except FileNotFoundError:
            print(f"[INFO] {i - 1} archivos borrados.")
            pass
    else:
        generar_archivos(NUM_ARCHIVOS, MAX_C, MAX_M, MAX_K)