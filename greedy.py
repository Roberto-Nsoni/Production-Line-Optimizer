import sys
from time import time
from yogi import read

start_time = time()
UNDEF = -1

class SolucioParcial:
    c: int
    m: int
    k: int
    c_e: list[int]
    n_e: list[int]
    produccions: list[int] # produccions[x] indica cuantos coches de la clase x hay que hacer aun
    classes: list[list[int]] # classes[x][i] == 1 si la clase x tiene la mejora i, == 0 alternamente
    sol: list[int] # registra la solucion acual
    cost: int # coste actual de la solucion
    x_in_window: list[int] # x_in_window[i] indica cuantos coches tiene la ventana de la mejora i en ese momento
    rem_upgrades: list[int] # rem_upgrades[i] indica cuantas mejoras del tipo i quedan aun por poner
    risks: list[float]

    def __init__(self, c: int, m: int, k: int, c_e: list[int], n_e: list[int],
                 produccions: list[int], classes: list[list[int]]) -> None:
        """TODO: Podemos quitar parametros de entrada"""
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
        self.rem_upgrades = [sum(produccions[i]*classes[i][j] for i in range(self.k)) for j in range(self.m)]
        self.risks = []
        for x in range(self.k):
            p = 1.0
            for i in range(self.m):
                if self.classes[x][i]:
                    p *= self.c_e[i]/self.n_e[i]
            self.risks.append(1 - p)
            

    def append(self, x: int) -> None:
        """Añade el elemento x a la solucion parcial y actualiza las ventanas y los costes adecuadamente"""
        self.sol.append(x)
        self.produccions[x] -= 1
        act = len(self.sol) - 1
        for i in range(self.m):
            # Mirar si el que dejamos atras tenia la mejora
            last = act - self.n_e[i]
            if last >= 0:
                self.x_in_window[i] -= self.classes[self.sol[last]][i]

            # Mirar si el que añadimos tiene la mejora
            if self.classes[x][i]:
                self.x_in_window[i] += 1
                self.rem_upgrades[i] -= 1

            self.cost += max(0, self.x_in_window[i] - self.c_e[i])

    def puntuations(self, a: float, b: float, c: float) -> dict[int, float]:
        """..."""
        act = len(self.sol) - 1
        max_produccions = max(self.produccions)
        punt = {i: 0.0 for i in range(self.k)}

        def cost(x: int) -> float:
            """Calcula el coste de meter la clase x en la solucion"""
            cost = 0
            for i in range(self.m):
                delta = 0
                # Mirar si el que dejamos atras tenia la mejora
                last = act - self.n_e[i]
                if last >= 0:
                    delta -= self.classes[self.sol[last]][i]

                # Mirar si el que añadimos tiene la mejora
                delta += self.classes[x][i]
                
                cost += max(0, self.x_in_window[i] + delta - self.c_e[i])
            
            return float(cost)
        
        def count(x: int) -> float:
            """..."""
            return self.produccions[x] / max_produccions
        
        def risk(x: int) -> float:
            return self.risks[x]

        costs = [cost(x) for x in range(self.k)]
        max_cost = max(costs) or 1.0
        costs = [i /max_cost for i in costs]

        for x in range(self.k):
            punt[x] = a * costs[x] + b * count(x) +  c * risk(x)

        return punt
    
    def end_sol(self) -> None:
        """Termina de extender las ventanas hasta el final (sin añadir nuevos coches) y calcula el coste final de la solución"""
        x_in_window = self.x_in_window[:]
        for act in range(len(self.sol), len(self.sol) + max(self.n_e)):
            for i in range(self.m):
                last = act - self.n_e[i]
                if 0 <= last < len(self.sol):
                    x_in_window[i] -= self.classes[self.sol[last]][i]

                self.cost += max(0, x_in_window[i] - self.c_e[i])
        
        
    
def write_sol(sol: list[int], cost: int) -> None:
    global start_time
    # Si no pones archivo de salida se escribe por pantalla
    if len(sys.argv) == 1:
        print(cost, round(time() - start_time, 1))
        print(" ".join(str(x) for x in sol))

    # Sino se sobreescribe el archivo de salida
    else:
        with open(sys.argv[1],"w") as f:    
            print(cost, round(time() - start_time, 1),file=f)
            print(" ".join(str(x) for x in sol),file=f)

def greedy_min_cost(s: SolucioParcial, a: float, b: float, c: float) -> None:
    for _ in range(s.c):
        candidates = {x: p for x, p in s.puntuations(a,b,c).items() if s.produccions[x] > 0}
        x = max(candidates, key = lambda i: -candidates[i])
        s.append(x)
    s.end_sol()

    # write_sol(s.sol, s.cost)


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
    greedy_min_cost(entrada, 1, -0.75, -0.75)

if __name__ == "__main__":
    main()