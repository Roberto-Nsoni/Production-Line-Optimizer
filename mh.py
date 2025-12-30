import sys, random, math
from time import time
from typing import Optional
from yogi import read

start_time = time()

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
        self.risks = []
        for x in range(self.k):
            p = 1.0
            for i in range(self.m):
                if self.classes[x][i]:
                    p *= self.c_e[i]/self.n_e[i]
            self.risks.append(1 - p)
            
    ### PARTE DEL GREEDY ###

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

            self.cost += max(0, self.x_in_window[i] - self.c_e[i])

    def puntuation(self, x: int) -> float:
        """Calcula una puntuación al añadir la clase x al final de la solución parcial."""
        act = len(self.sol) - 1
        max_produccions = max(self.produccions)

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
        costs = [i/max_cost for i in costs]

        punt = 1 * costs[x] - 0.75 * count(x) - 0.75 * risk(x)

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

    ### PARTE DE LA METAHEURISTICA ###

    def _recaculate_cost(self) -> None:
        """
        Recalcula el coste total de toda la solucion (incluido el end_sol).
        Actualiza self.cost y self.x_in_window adecuadamente.
        """

        cost = 0
        x_in_window = [0] * self.m

        # calcular el coste 
        for act in range(len(self.sol)):
            for i in range(self.m):
                last = act - self.n_e[i]
                if last >= 0:
                    x_in_window[i] -= self.classes[self.sol[last]][i]
                x_in_window[i] += self.classes[self.sol[act]][i]
                cost += max(0, x_in_window[i] - self.c_e[i])

        # end_sol
        for act in range(len(self.sol), len(self.sol) + max(self.n_e)):
            for i in range(self.m):
                last = act - self.n_e[i]
                if 0 <= last < len(self.sol):
                    x_in_window[i] -= self.classes[self.sol[last]][i]
                cost += max(0, x_in_window[i] - self.c_e[i])

        self.x_in_window = x_in_window[:]
        self.cost = cost
    
    def switch(self, x: int, y: int) -> None:
        """
        Intercambia la posicion x e y de la solucion parcial.
        Actualiza self.cost y self.x_in window adecuadamente.
        """
        self.sol[x], self.sol[y] = self.sol[y], self.sol[x]
        self._recaculate_cost()

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

def greedy_random_generator(s: SolucioParcial, alpha: float = 0.2):
    """Genera una solución greedy PERO a cada paso escoge entre los alpha(%) mejores opciones"""
    for _ in range(s.c):
        candidates = [x for x in range(s.k) if s.produccions[x] > 0]
        candidates.sort(key=lambda x: s.puntuation(x))
        rand_x = random.choice(candidates[:math.ceil(len(candidates) * alpha)]) # escoger entre los alpha(%) mejores
        s.append(rand_x)
    s.end_sol()

def simulated_annealing(s: SolucioParcial, t0: float = 10.0, max_iterations: int = 10_000, alpha: float = 0.999) -> None:
    """
    Aplica SA sobre la solución s.
    """
    t = t0
    k = 0
    best_cost = s.cost
    best_sol = s.sol[:]

    while k < max_iterations:
        # Definimos la vecindad como un switch entre dos posiciones (i, j)
        i, j = random.sample(range(s.c), 2)
        old_cost = s.cost
        s.switch(i, j)
        new_cost = s.cost

        # Dos maneras de aceptar esta nueva solucion tras el switch: 1) El nuevo coste es mejor; 2) Por aleatoriedad
        if new_cost <= old_cost or random.random() < math.exp(-(new_cost - old_cost) / t):
                if s.cost < best_cost:
                    best_cost = new_cost
                    best_sol = s.sol[:]
        else:
                s.switch(i, j) # revertir el switch si no lo aceptamos

        t *= alpha
        k += 1

    s.sol = best_sol[:]
    s.cost = best_cost

def grasp(c: int, m: int, k: int, c_e: list[int], n_e: list[int],
          produccions: list[int], classes: list[list[int]], max_iterations: Optional[int] = None):
    
    best_cost = sys.maxsize
    i = 0

    while max_iterations is None or i < max_iterations:
        # Generar una solucion inicial aleaoria
        s = SolucioParcial(c, m, k, c_e, n_e, produccions[:], classes)
        greedy_random_generator(s)

        # Aplicar Simmulated Annealing a esa solucion inical
        simulated_annealing(s)

        if s.cost < best_cost:
            write_sol(s.sol, s.cost)
            best_cost = s.cost
            if best_cost == 0:
                break
        
        i += 1

def main() -> None:
    c, m, k = read(int), read(int), read(int)
    c_e = [read(int) for _ in range(m)]
    n_e = [read(int) for _ in range(m)]
    produccions = list[int]()
    classes = list[list[int]]()
    for _ in range(k):
        _ = read(int)
        produccions.append(read(int))
        classes.append([read(int) for _ in range(m)])

    ### CAMBIAR EL ULTIMO PARAMETRO (10) SI QUIERES QUE PARE DESPUES DE HACER 10 ITERACIONES
    ### DEJALO VACIO SI NO QUIERES QUE PARE NUNCA
    grasp(c, m, k, c_e, n_e, produccions, classes, 10)

if __name__ == "__main__":
    main()

# NO HACER CASO (es un intento mio de optimizar el switch pero de momento no funcoina jeje)
    '''
    def switch(self, x: int, y: int) -> None:
        """Intercambia la posicion x e y de la solucion parcial y actualiza los costes adecuadamente."""

        delta_cost = 0

        # 1) Quitar 'x' y en su lugar añadir 'y'.
        for up in range(self.m):
            if self.classes[self.sol[x]][up] and not self.classes[self.sol[y]][up]:
                win_size = self.n_e[up]
                for i in range(-win_size + 1, win_size):
                    lower = max(0, x + i)
                    upper = min(self.c - 1, lower + self.n_e[up])
                    delta_cost -= (1 if sum(self.classes[car][up] for car in self.sol[lower:(upper + 1)]) else 0)

            elif not self.classes[self.sol[x]][up] and self.classes[self.sol[y]][up]:
                win_size = self.n_e[up]
                for i in range(-win_size + 1, win_size):
                    lower = max(0, x + i)
                    upper = min(self.c - 1, lower + self.n_e[up])
                    delta_cost += (1 if sum(self.classes[car][up] for car in self.sol[lower:(upper + 1)]) else 0)
        
        # 2) Quitar 'y' y en su lugar añadir 'x'.
        for up in range(self.m):
            if self.classes[self.sol[x]][up] and not self.classes[self.sol[y]][up]:
                win_size = self.n_e[up]
                for i in range(-win_size + 1, win_size):
                    lower = max(0, x + i)
                    upper = min(self.c - 1, lower + self.n_e[up])
                    delta_cost += (1 if sum(self.classes[car][up] for car in self.sol[lower:(upper + 1)]) else 0)

            elif not self.classes[self.sol[x]][up] and self.classes[self.sol[y]][up]:
                win_size = self.n_e[up]
                for i in range(-win_size + 1, win_size):
                    lower = max(0, x + i)
                    upper = min(self.c - 1, lower + self.n_e[up])
                    delta_cost -= (1 if sum(self.classes[car][up] for car in self.sol[lower:(upper + 1)]) else 0)

        self.sol[x], self.sol[y] = self.sol[y], self.sol[x]
        self.cost += delta_cost
    
        '''