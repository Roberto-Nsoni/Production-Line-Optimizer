import subprocess
import os

TEST_FILE = "greedy.py"
BENCH_DIR = "public_benchs"
OPT_FILE = "results_greedy.txt"
TMP_OUT = "tmp.txt"

def load_results():
    """
    Devuelve un diccionario con los costes óptimos cargados del archivo.
    """
    if not os.path.exists(OPT_FILE):
        # Si el archivo no existe, lo creamos vacío
        open(OPT_FILE, "w").close()

    opt = {}
    with open(OPT_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            inst_raw, cost = line.split()
            inst = inst_raw.replace(".txt", "")   # quitar .txt
            opt[inst] = int(cost)
    return opt

def append_optimal_cost(inst_name, cost):
    """
    Escribe "<inst_name>.txt <cost>" al final del archivo results.txt
    """
    with open(OPT_FILE, "a") as f:
        f.write(f"{inst_name}.txt\t{cost}\n")
    print(f"[INFO] Añadido al archivo óptimos: {inst_name} {cost}")


def read_cost_from_output_file(path):
    """Lee coste encontrado por {TEST_FILE}"""
    with open(path, "r") as f:
        first_line = f.readline().strip().split()
        cost_str = first_line[0]
        time_execute_str = first_line[1]
        return int(cost_str), float(time_execute_str)

def main():
    optimal = load_results()

    families = ["easy", "med"]
    numbers = range(1, 10 + 1)

    for fam in families:
        for num in numbers:

            inst_name = f"{fam}-{num}"
            inst_path = f"{BENCH_DIR}/{inst_name}.txt"

            print(f"\n=== Probando instancia {inst_name} ===")

            # Ejecutar TEST_FILE en el CMD
            cmd_exh = f"./{TEST_FILE} {TMP_OUT} < {inst_path}"
            print(f"[INFO] Ejecutando: {cmd_exh}")

            result = subprocess.run(cmd_exh, shell=True)

            if result.returncode != 0:
                print(f"[ERROR] {TEST_FILE} falló ejecutando {inst_name}")
                continue

            # Validar con checker
            cmd_checker = f"./checker {inst_path} {TMP_OUT}"
            print(f"[INFO] Ejecutando checker...")

            result = subprocess.run(
                cmd_checker,
                shell=True,
                capture_output=True
            )

            if result.returncode != 0:
                print("[ERROR] Checker detectó solución inválida")
                print(result.stdout.decode())
                continue
            else:
                print("[OK] Checker validó la solución")

            # Comprobar si existe óptimo en results.txt
            found_cost, time_execute = read_cost_from_output_file(TMP_OUT)
            print(f"[INFO] Coste encontrado por {TEST_FILE}: {found_cost} en {time_execute} s")

            if inst_name not in optimal:
                print(f"[INFO] No existe entrada para {inst_name} en results.txt")
                print("[INFO] La añado automáticamente.")

                append_optimal_cost(inst_name, found_cost)

                # actualizar diccionario en memoria
                optimal[inst_name] = found_cost
                continue

            # Si existe, comparar
            real_cost = optimal[inst_name]
            print(f"[INFO] Coste óptimo registrado: {real_cost}")

            if found_cost == real_cost:
                print("[OK] Coste correcto ✓")
            else:
                print("[WRONG] Coste incorrecto ✗")

    # Eliminar archivo temporal
    subprocess.run(
                    f"rm {TMP_OUT}",
                    shell=True,
                    capture_output=True
                )

if __name__ == "__main__":
    main()
