import sys
from time import time
from yogi import read

start_time = 0.0

class GreedyConstructor:
    """
    Clase que construye una solución greedy para el problema.
    Permite construir una solución razonablemente buena a partir 
    de asignar una función de penalización.

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
    risks: para cada clase x, se asigna un valor entre (0, 1) en base a cuanto de
    espaciados se debería dejar los coches para no generar coste. Valores cercanos
    a 1 indican clases más conflictivas que conviene espaciar.
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
    risks: list[float]

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

        # Calcular riesgos
        self.risks = []
        for x in range(self.k):
            p = 1.0
            for i in range(self.m):
                if self.classes[x][i]:
                    p *= self.c_e[i]/self.n_e[i]
            self.risks.append(1 - p)
            

    def cooler_append(self, x: int) -> None:
        """
        Añade un coche de clase x a la solucion parcial y actualiza las ventanas
        y los costes adecuadamente
        """
        self.sol.append(x)
        self.remaining_cars[x] -= 1
        act = len(self.sol) - 1
        for i in range(self.m):
            # Mirar si el que dejamos atrás tenía la mejora
            last = act - self.n_e[i]
            if last >= 0:
                self.cars_in_window[i] -= self.classes[self.sol[last]][i]

            # Mirar si el que añadimos tiene la mejora
            if self.classes[x][i]:
                self.cars_in_window[i] += 1

            self.cost += max(0, self.cars_in_window[i] - self.c_e[i])

    def penalizations(self) -> dict[int, float]:
        """
        Asigna una penalización ponderada a cada clase teniendo en cuenta el
        estado actual de la solución.
        La penalización tiene en cuenta:
        - El coste de poner esa clase a continuación
        - El número de coches restantes de esa clase
        - El riesgo asociado a la clase

        Devuelve un diccionario [clase, penalización].
        """
        act = len(self.sol) - 1
        max_rem_cars = max(self.remaining_cars)
        penalization = {x: 0.0 for x in range(self.k)}

        def cost(x: int) -> float:
            """Calcula y devuelve el coste de añadir un coche de la clase x en la solución."""
            cost = 0
            for i in range(self.m):
                delta = 0
                # Mirar si el que dejamos atrás tenía la mejora
                last = act - self.n_e[i]
                if last >= 0:
                    delta -= self.classes[self.sol[last]][i]

                # Mirar si el que añadimos tiene la mejora
                delta += self.classes[x][i]
                
                cost += max(0, (self.cars_in_window[i] + delta) - self.c_e[i])
            
            return float(cost)
        
        def count(x: int) -> float:
            """Devuelve el números de coches restantes de la clase x normalizado."""
            return self.remaining_cars[x] / max_rem_cars
        
        # Normalizar costes
        costs = [cost(x) for x in range(self.k)]
        max_cost = max(costs)
        if max_cost == 0: max_cost = 1.0
        costs = [i /max_cost for i in costs]

        for x in range(self.k):
            if self.remaining_cars[x] > 0:
                penalization[x] = 1 * costs[x] - 0.75 * count(x) - 0.75 * self.risks[x]

        return penalization
    
    def end_sol(self) -> None:
        """
        Termina de extender las ventanas hasta el final (sin añadir nuevos coches)
        y actualiza el coste de la solución.
        """
        x_in_window = self.cars_in_window[:]

        # Avanza desde el final de la solución hasta el final de la ventana más grande
        for act in range(len(self.sol), len(self.sol) + max(self.n_e)):
            for i in range(self.m):
                # Mirar si el que dejamos atrás tenía la mejora i
                last = act - self.n_e[i]
                if 0 <= last < len(self.sol):
                    x_in_window[i] -= self.classes[self.sol[last]][i]

                self.cost += max(0, x_in_window[i] - self.c_e[i])

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
        print(cost, round(time() - start_time, 1))
        print(" ".join(str(x) for x in sol))

    # Sino se sobreescribe el archivo de salida
    else:
        with open(sys.argv[1],"w") as f:    
            print(cost, round(time() - start_time, 1),file=f)
            print(" ".join(str(x) for x in sol),file=f)


def greedy_min_cost(g: GreedyConstructor) -> None:
    """
    Construye una solución greedy (golosa), escogiendo en todo momento la clase con menor penalización.
    Sobreescribe en el fichero indicado por línea de comandos la solución encontrada.
    """
    for _ in range(g.c):
        candidates = {x: p for x, p in g.penalizations().items() if g.remaining_cars[x] > 0}
        x = min(candidates, key = lambda i: candidates[i])
        g.cooler_append(x)
    g.end_sol()

    write_sol(g.sol, g.cost)


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
    g = GreedyConstructor(c, m, k, c_e, n_e, remaining_cars, classes)
    greedy_min_cost(g)

if __name__ == "__main__":
    main()