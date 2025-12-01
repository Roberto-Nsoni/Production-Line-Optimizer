import random, os
import yogi
import tests

def generar_input_string(max_coches, max_mejoras, max_clases, max_cantidad_clase=10):
    # Elegir cantidades aleatorias
    M = random.randint(3, max_mejoras)
    K = random.randint(3, max_clases)
    
    # Escoger cantidad por clase primero, luego sumarlas
    C = 0
    while not 0 < C <= max_coches:
        cantidades = [random.randint(1, max_cantidad_clase) for _ in range(K)]
        C = sum(cantidades)

    # Generar ce y ne con ce <= ne
    ce = []
    ne = []
    for _ in range(M):
        n = random.randint(2, min(C, 6))
        c = random.randint(1, n - 1)
        ce.append(c)
        ne.append(n)

    # Generar clases
    clases = []
    for i in range(K):
        mejoras = [random.randint(0, 1) for _ in range(M)]
        clases.append((i, cantidades[i], mejoras))

    # Construir string de salida
    out = []
    out.append(f"{C} {M} {K}")
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
    NUM_ARCHIVOS = 200
    tests.OPT_FILE = "results_extra.txt"
    tests.TEST_FILE = "greedy.py"
    generar_archivos(NUM_ARCHIVOS, 100, 50, 10)
    print(tests.main())
    os.remove(tests.OPT_FILE)