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
    risc: list[float]
    mejoras_prob: list[float]

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
        self.risc = []
        for x in range(k):
            p = 1.0
            for i in range(m):
                if classes[x][i]:
                    p  *= c_e[i]/n_e[i]
            self.risc.append((1-p)/m)

        # self.risc = [sum(n_e[i]/c_e[i] for i in range(m) if classes[x][i])/m for x in range(k)]
        self.mejoras_prob = [sum(1 for i in range(m) if (classes[x][i] and n_e[i]/c_e[i] < 0.5))/m for x in range(k)]

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

    def end_sol(self) -> None:
        """Termina de extender las ventanas hasta el final (sin añadir nuevos coches) y calcula el coste final de la solución"""
        x_in_window = self.x_in_window[:]
        added_cost = 0
        for act in range(len(self.sol), len(self.sol) + max(self.n_e)):
            for i in range(self.m):
                last = act - self.n_e[i]
                if 0 <= last < len(self.sol):
                    x_in_window[i] -= self.classes[self.sol[last]][i]

                added_cost += max(0, x_in_window[i] - self.c_e[i])
        
        self.cost += added_cost
        return None

    def calc_cost(self, x: int) -> int:
        added_cost = 0
        actual = len(self.sol) - 1
        for i in range(self.m):
            # Mirar si el que dejamos atras tenia la mejora
            window = self.x_in_window[i]
            last = actual - self.n_e[i]

            if last >= 0:
                window -= self.classes[self.sol[last]][i]

            # Mirar si el que añadimos tiene la mejora
            if self.classes[x][i]:
                window += 1

            added_cost += max(0, window - self.c_e[i])
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


def priority(s: SolucioParcial, candidats: list[int]) -> int:
    return max(candidats, key=lambda x: 0.25*s.produccions[x]/s.c + 1.0*s.risc[x] -1.0*s.mejoras_prob[x])

def greedy_min_cost2(s: SolucioParcial) -> None:
    for _ in range(s.c):

        costs = [s.calc_cost(x) if s.produccions[x] > 0 else sys.maxsize for x in range(s.k)]
        min_punt = min(costs)
        candidats = [x for x in range(s.k) if costs[x] == min_punt]

        if len(candidats) > 1:
            x = priority(s, candidats)
        else:
            x = candidats[0]

        s.produccions[x] -= 1
        s.cooler_append(x)

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
    greedy_min_cost2(entrada)

if __name__ == "__main__":
    main()