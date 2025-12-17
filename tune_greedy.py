from time import time
from yogi import read
from greedy import SolucioParcial, greedy_min_cost

INTERVALS = 10 # Entre [0, 1] (aunque en realidad calculará entre [-1, 1])

# Generamos automáticamente los archivos de prueba
INSTANCES =(
    [f"public_benchs/easy-{i}.txt" for i in range(1, 11)] + 
    [f"public_benchs/med-{i}.txt" for i in range(1, 11)] + 
    [f"public_benchs/hard-{i}.txt" for i in range(1, 21)] + 
    [f"public_benchs/extra-{i}.txt" for i in range(1, 201)] 
)

def read_instance(filename):
    """Lee la instancia desde un archivo"""
    with open(filename) as f:
        tokens = list(map(int, f.read().split()))
    idx = 0
    def next_int():
        nonlocal idx
        val = tokens[idx]
        idx += 1
        return val

    c, m, k = next_int(), next_int(), next_int()
    c_e = [next_int() for _ in range(m)]
    n_e = [next_int() for _ in range(m)]
    produccions = []
    classes = []
    for _ in range(k):
        _ = next_int()  # id clase
        produccions.append(next_int())
        classes.append([next_int() for _ in range(m)])
    return c, m, k, c_e, n_e, produccions, classes

def evaluate_weights(a, b, c):
    """Devuelve el coste promedio sobre todas las instancias"""
    total_cost = 0
    total_cases = 0
    for filename in INSTANCES:
        c1, m1, k1, c_e1, n_e1, produccions1, classes1 = read_instance(filename)
        sol = SolucioParcial(c1, m1, k1, c_e1, n_e1, produccions1.copy(), classes1)
        greedy_min_cost(sol, a, b, c)  # se calcula sol.cost
        total_cost += sol.cost
        total_cases += 1
    return total_cost / total_cases

def main():
    best_weights = None
    best_cost = float('inf')

    # Valores de prueba para a,b,c
    weight_values = [i/INTERVALS for i in range(-INTERVALS, INTERVALS + 1)]

    for a in weight_values:
        for b in weight_values:
            for c in weight_values:
                cost = evaluate_weights(a, b, c)
                print(f"Probando a={a} b={b} c={c} → coste promedio={cost}")
                if cost < best_cost:
                    best_cost = cost
                    best_weights = (a, b, c)

    print("\nMejores pesos encontrados:")
    print(f"a={best_weights[0]}, b={best_weights[1]}, c={best_weights[2]}, coste promedio={best_cost}")

if __name__ == "__main__":
    main()