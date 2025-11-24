import sys
from time import time
from yogi import read

start_time = 0.0
UNDEF = -1

class SolucioParcial:
    c: int
    m: int
    k: int
    c_e: list[int]
    n_e: list[int]
    produccions: list[int]
    classes: list[list[int]]
    sol: list[int]
    cost: int
    x_in_window: list[int]

    def __init__(self, c: int, m: int, k: int, c_e: list[int], n_e: list[int],
                 produccions: list[int], classes: list[list[int]]) -> None:
        """Podemos quitar parametros de entrada"""
        self.c = c
        self.m = m
        self.k = k
        self.c_e = c_e
        self.n_e = n_e
        self.produccions = produccions
        self.classes = classes
        self.sol = []
        self.cost = 0
        self.x_in_window = [0] * m

    def cooler_append(self, x: int) -> None:
        self.sol.append(x)
        act = len(self.sol) - 1
        for i in range(self.m):
            # Mirar si el que dejamos atras tenia la mejora
            last = act - self.n_e[i]
            if last >= 0:
                self.x_in_window[i] -= self.classes[self.sol[last]][i]

            # Mirar si el que añadimos tiene la mejora
            if self.classes[x][i]:
                self.x_in_window[i] += 1

            self.cost += max(0, self.x_in_window[i] - self.c_e[i])

    def calc_cost(self, x: int) -> int:
        added_cost = 0
        x_in_window = self.x_in_window[:]
        act = len(self.sol) - 1
        for i in range(self.m):
            # Mirar si el que dejamos atras tenia la mejora
            last = act - self.n_e[i]
            if last >= 0:
                x_in_window[i] -= self.classes[self.sol[last]][i]

            # Mirar si el que añadimos tiene la mejora
            if self.classes[x][i]:
                x_in_window[i] += 1

            added_cost += max(0, x_in_window[i] - self.c_e[i])
        return added_cost

def write_sol(sol: list[int], cost: int) -> None:
    global start_time
    # Si no pones archivo de salida se escribe por pantalla
    if len(sys.argv) == 1:
        print(cost, time() - start_time)
        print(" ".join(str(x) for x in sol))

    # Sino se sobreescribe el archivo de salida
    else:
        with open(sys.argv[1],"w") as f:    
            print(cost, round(time() - start_time, 1),file=f)
            print(" ".join(str(x) for x in sol),file=f)

def greedy_min_cost(s: SolucioParcial) -> None:
    for i in range(s.c):
        min_puntuation = sys.maxsize
        min_x = UNDEF
        for x in range(s.k):
            if s.produccions[x] > 0:
                puntuation = s.calc_cost(x)
                if puntuation < min_puntuation:
                    min_puntuation = puntuation
                    min_x = x

        s.produccions[min_x] -= 1
        s.cooler_append(min_x)

    write_sol(s.sol, s.cost)


def main() -> None:
    global start_time
    c, m, k = read(int), read(int), read(int)
    c_e = [read(int) for _ in range(m)]
    n_e = [read(int) for _ in range(m)]
    produccions = list[int]()
    classes = list[list[int]]()
    for _ in range(k):
        _ = read(int)
        produccions.append(read(int))
        classes.append([read(int) for _ in range(m)])

    start_time = time()
    entrada = SolucioParcial(c, m, k, c_e, n_e, produccions, classes)
    greedy_min_cost(entrada)

if __name__ == "__main__":
    main()