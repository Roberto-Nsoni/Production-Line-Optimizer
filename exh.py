import sys
from time import time
from yogi import read

start_time = 0.0

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
    rem_upgrades: list[int]

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

    def cooler_append(self, x: int) -> None:
        """Añade el elemento x a la solucion parcial y actualiza las ventanas y los costes adecuadamente"""
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
                self.rem_upgrades[i] -= 1

            self.cost += max(0, self.x_in_window[i] - self.c_e[i])
    
    def cooler_pop(self) -> None:
        """Elimina el ultimo elemento de la solucion parcial y actualiza las ventanas y los costes adecuadamente"""
        x = self.sol[-1]
        act = len(self.sol) - 1
        for i in range(self.m):
            self.cost -= max(0, self.x_in_window[i] - self.c_e[i])

            # Mirar si el que vuelve a entrar tenia la mejora
            last = act - self.n_e[i]
            if last >= 0:
                self.x_in_window[i] += self.classes[self.sol[last]][i]
            
            # Mirar si el que hace pop tenia la mejora
            if self.classes[x][i]:
                self.x_in_window[i] -= 1
                self.rem_upgrades[i]+= 1

        self.sol.pop()
    
    def end_sol(self) -> int:
        """Termina de extender las ventanas hasta el final (sin añadir nuevos coches) y calcula el coste final de la solución"""
        x_in_window = self.x_in_window[:]
        added_cost = 0
        for act in range(len(self.sol), len(self.sol) + max(self.n_e)):
            for i in range(self.m):
                last = act - self.n_e[i]
                if 0 <= last < len(self.sol):
                    x_in_window[i] -= self.classes[self.sol[last]][i]

                added_cost += max(0, x_in_window[i] - self.c_e[i])
        
        return added_cost

    def lower_bound(self) -> int:
        """..."""
        lb = self.cost
        rem_len = self.c - len(self.sol)

        for i in range(self.m):
            # Exceso actual
            me_paso = max(0, self.x_in_window[i] - self.c_e[i] - 1)
            lb += me_paso * (me_paso + 1) // 2

            # Clases restantes
            complete_sets = self.n_e[i] * (self.rem_upgrades[i] // self.c_e[i]) # c_e puede ser cero?
            rest = self.rem_upgrades[i] % self.c_e[i]

            if complete_sets == 0:
                partial_sets = rest
            else:
                partial_sets = -(self.n_e[i] - self.c_e[i]) if rest == 0 else rest

            lb += max(0, (complete_sets + partial_sets) - rem_len)

        return lb


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

def min_cost_rec(s: SolucioParcial, best_cost: int, best_sol: list[int]) -> tuple[int, list[int]]:

    if len(s.sol) == s.c:
        added_cost = s.end_sol()
        if s.cost + added_cost < best_cost:
            write_sol(s.sol, s.cost + added_cost)
            return s.cost + added_cost, s.sol[:]

    if s.lower_bound() < best_cost:
        if len(s.sol) != 0: 
            last = s.sol[-1]
        else:
            last = 0
        for x in list(range(last+1, s.k)) + list(range(0, last+1)):
            if s.produccions[x] > 0:
                s.produccions[x] -= 1
                s.cooler_append(x)
                best_cost, best_sol = min_cost_rec(s, best_cost, best_sol)
                s.cooler_pop()
                s.produccions[x] += 1
    
    return best_cost, best_sol

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
    min_cost_rec(entrada, sys.maxsize, [])

if __name__ == "__main__":
    main()  
