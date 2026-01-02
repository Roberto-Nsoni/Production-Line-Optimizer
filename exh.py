import sys
from time import time
from yogi import read

start_time = 0.0

class PartialSolution:
    """
    Clase que almacena una solución parcial del problema durante una búsqueda
    exhaustiva que construye la secuencia de coches de forma incremental.

    c: número total de coches que debe tener la solución final
    c_e: para cada mejora i, número máximo de coches que pueden tener
    dicha mejora dentro de una ventana de tamaño n_e[i]
    n_e: para cada mejora i, tamaño de la ventana en la que se aplique la restricción
    classes: matriz que describe las clases de coches. classes[x][i] vale 1
    si la clase x tiene la mejora i y vale 0 alternativamente
    
    sol: secuencia parcial de coches construida hasta el momento
    cost: coste acumulado de la solución parcial actual

    remaining_cars: número de coches pendientes por colocar de cada clase
    cars_in_window: para cada mejora i, cars_in_window[i] representa el número de 
    coches con dicha mejora que hay actualmente en la ventana correspondiente
    rem_upgrades: para cada mejora i, rem_upgrades[i] representa el número total de 
    coches restantes que requieren esa mejora
    """

    # Datos del problema
    c: int
    c_e: list[int]
    n_e: list[int]
    classes: list[list[int]]

    # Construcción de la solución
    sol: list[int]
    cost: int

    # Parámetros auxiliares
    remaining_cars: list[int]
    cars_in_window: list[int]
    rem_upgrades: list[int]

    def __init__(self, c: int, m: int, k: int, c_e: list[int], n_e: list[int],
                 remaining_cars: list[int], classes: list[list[int]]) -> None:
        self.c = c
        self.c_e = c_e
        self.n_e = n_e
        self.remaining_cars = remaining_cars[:]
        self.classes = classes
        self.sol = []
        self.cost = 0
        self.cars_in_window = [0] * m
        self.rem_upgrades = [sum(remaining_cars[i]*classes[i][j] for i in range(k)) for j in range(m)]

    def cooler_append(self, x: int) -> None:
        """Añade un coche de clase x a la solucion parcial y actualiza las ventanas y los costes adecuadamente."""

        self.sol.append(x)
        act = len(self.sol) - 1
        for i in range(self.m):
            # Mirar si el que dejamos atrás tenía la mejora
            last = act - self.n_e[i]
            if last >= 0:
                self.cars_in_window[i] -= self.classes[self.sol[last]][i]

            # Mirar si el que añadimos tiene la mejora
            if self.classes[x][i]:
                self.cars_in_window[i] += 1
                self.rem_upgrades[i] -= 1

            self.cost += max(0, self.cars_in_window[i] - self.c_e[i])
    
    def cooler_pop(self) -> None:
        """Elimina el último elemento de la solucion parcial y actualiza las ventanas y los costes adecuadamente."""

        x = self.sol[-1]
        act = len(self.sol) - 1
        for i in range(self.m):
            self.cost -= max(0, self.cars_in_window[i] - self.c_e[i])

            # Mirar si el que vuelve a entrar tenía la mejora
            last = act - self.n_e[i]
            if last >= 0:
                self.cars_in_window[i] += self.classes[self.sol[last]][i]
            
            # Mirar si el que hace pop (el que quitamos) tenía la mejora
            if self.classes[x][i]:
                self.cars_in_window[i] -= 1
                self.rem_upgrades[i]+= 1

        self.sol.pop()
    
    def end_sol(self) -> int:
        """Termina de extender las ventanas hasta el final (sin añadir nuevos coches) y devuelve su coste añadido."""

        cars_in_window = self.cars_in_window[:]
        added_cost = 0

        # Avanza desde el final de la solución hasta el final de la ventana más grande
        for act in range(len(self.sol), len(self.sol) + max(self.n_e)):
            for i in range(self.m):
                # Mirar si el que dejamos atrás tenía la mejora i
                last = act - self.n_e[i]
                if 0 <= last < len(self.sol):
                    cars_in_window[i] -= self.classes[self.sol[last]][i]

                added_cost += max(0, cars_in_window[i] - self.c_e[i])
        
        return added_cost

    def lower_bound(self) -> int:
        """
        Calcula una cota inferior del coste de la solución actual. 
        Tiene en cuenta:
        1) El coste mínimo de avanzar las ventanas hasta que dejen de contener coches
        2) El coste mínimo inevitable que tienes que asumir con los coches que te quedan
        """
        lb = self.cost
        rem_len = self.c - len(self.sol)

        for i in range(self.m):
            # 1) Exceso actual en la ventana, para desplazarla fuera se paga mínimo 1+2+...+excess
            excess = max(0, self.cars_in_window[i] - self.c_e[i] - 1)
            lb += excess * (excess + 1) // 2

            # 2) Calcular cuántas posiciones mínimas se necesitan para colocar las mejoras restantes sin generar coste:
            # Posiciones ocupadas por bloques completos de ventanas sin penalización
            full_window_positions = self.n_e[i] * (self.rem_upgrades[i] // self.c_e[i])
            rest = self.rem_upgrades[i] % self.c_e[i]

            # Si no tenemos coches restantes, podemos quitar los de 'relleno' de la ventana anterior
            if full_window_positions != 0 and rest == 0:
                residual_positions = -(self.n_e[i] - self.c_e[i])
            else:
                residual_positions = rest

            lb += max(0, (full_window_positions + residual_positions) - rem_len)

        return lb
    
    @property
    def m(self) -> int:
        """Devuelve el número total de mejoras."""
        return len(self.classes[0])
    
    @property
    def k(self) -> int:
        """Devuelve el número total de clases."""
        return len(self.classes)



def write_sol(sol: list[int], cost: int) -> None:
    """
    Escribe la solución dada junto con su coste y el tiempo de ejecución.
    Escribe esta solución por pantalla o en un archivo en función de si este último
    se ha especificado a través de la línea de comandos.
    """

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



def min_cost_rec(s: PartialSolution, best_cost: int, best_sol: list[int]) -> tuple[int, list[int]]:
    """
    Calcula de forma exhaustiva la mejor solución para el problema dada una solución parcial s.
    Sobreescribe en el fichero indicado por línea de comandos la mejor solución encontrada hasta el momento.
    Devuelve la distribución de coches de dicha soución y su coste.
    """

    if len(s.sol) == s.c:
        final_cost = s.cost + s.end_sol()
        if final_cost < best_cost:
            write_sol(s.sol, final_cost)
            return final_cost, s.sol[:]

    if s.lower_bound() < best_cost:

        last = s.sol[-1] if len(s.sol) != 0 else 0 

        # Continuar búsqueda con la siguiente clase a la anterior
        for x in list(range(last+1, s.k)) + list(range(0, last+1)):
            if s.remaining_cars[x] > 0:
                s.remaining_cars[x] -= 1
                s.cooler_append(x)
                best_cost, best_sol = min_cost_rec(s, best_cost, best_sol)
                s.cooler_pop()
                s.remaining_cars[x] += 1
    
    return best_cost, best_sol

def main() -> None:

    global start_time

    c, m, k = read(int), read(int), read(int)
    c_e = [read(int) for _ in range(m)]
    n_e = [read(int) for _ in range(m)]

    remaining_cars = list[int]()
    classes = list[list[int]]()
    for _ in range(k):
        _ = read(int)
        remaining_cars.append(read(int))
        classes.append([read(int) for _ in range(m)])

    start_time = time()
    s = PartialSolution(c, m, k, c_e, n_e, remaining_cars, classes)
    min_cost_rec(s, sys.maxsize, [])

if __name__ == "__main__":
    main()  
