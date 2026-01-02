# pyright: basic
import subprocess
import os
from time import time

### MODIFICAR LAS COSTANTES DE ABAJO SEGUN CONVENGA ###
TEST_FILE = "mh_copy"  # Archivo que se quiera provar .py (o vacío para codon)
OPT_FILE = "results_mh1min.txt"  # Archivo con resultados
INSTANCES = (
    # [f"public_benchs/easy-{i}.txt" for i in range(1, 11)] +
    # [f"public_benchs/med-{i}.txt" for i in range(1, 11)] +
    [f"public_benchs/hard-{i}.txt" for i in range(1, 21)]
)

TMP_OUT = "tmp.txt"  # Archivo temporal donde se guardan las salidas

def load_results():
    """
    Devuelve un diccionario: inst -> [cost1, cost2, ...]
    Si no existe el archivo, lo crea vacío.
    """
    if not os.path.exists(OPT_FILE):
        open(OPT_FILE, "w").close()

    opt = {}
    with open(OPT_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            inst = parts[0]
            costs = list(map(int, parts[1:]))

            opt[inst] = costs

    return opt

def append_new_instance(inst_path, cost):
    with open(OPT_FILE, "a") as f:
        f.write(f"{inst_path} \t{cost}\n")

def append_cost_to_existing(inst_path, new_cost, optimal):
    optimal[inst_path].append(new_cost)

    with open(OPT_FILE, "w") as f:
        for inst, costs in optimal.items():
            cost_str = "\t".join(map(str, costs))
            f.write(f"{inst} \t{cost_str}\n")

def read_cost_time_from_output_file(path):
    """Lee coste encontrado por TEST_FILE."""
    with open(path, "r") as f:
        first_line = f.readline().strip().split()
        cost_str = first_line[0]
        time_execute_str = first_line[1]
        return int(cost_str), float(time_execute_str)

def main():
    optimal = load_results()
    total_time = []

    for inst_path in INSTANCES:

        print(f"\n=== Probando instancia {inst_path} ===")
        start_time = time()

        # Ejecutar TEST_FILE en el CMD
        if TEST_FILE.endswith(".py"):
            cmd_exh = f"python3 {TEST_FILE} {TMP_OUT} < {inst_path}"
        else:
            cmd_exh = f"./{TEST_FILE} {TMP_OUT} < {inst_path}"

        print(f"[INFO] Ejecutando: {cmd_exh}")
        result = subprocess.run(cmd_exh, shell=True)

        # Guardar tiempo de ejecución
        instance_time = round(time() - start_time, 1)
        total_time.append(instance_time)

        if result.returncode != 0:
            print(f"[ERROR] {TEST_FILE} falló ejecutando {inst_path}")

        # Validar con checker
        cmd_checker = f"./checker {inst_path} {TMP_OUT}"
        result = subprocess.run(cmd_checker, shell=True, capture_output=True)

        if result.returncode != 0:
            print("[ERROR] Checker detectó solución inválida")
            print(result.stdout.decode())

        # Leer salida temporal
        found_cost, time_execute = read_cost_time_from_output_file(TMP_OUT)
        print(f"[INFO] Coste encontrado: {found_cost} en el segundo {time_execute} (Total: {instance_time} s)")

        # Guardar o añadir coste
        if inst_path not in optimal:
            optimal[inst_path] = [found_cost]
            append_new_instance(inst_path, found_cost)
        else:
            append_cost_to_existing(inst_path, found_cost, optimal)

    # Eliminar temporal
    subprocess.run(f"rm {TMP_OUT}", shell=True, capture_output=True)

    if not total_time:
        print("[WARN] No se registró ningún tiempo")
        return 0

    return sum(total_time) / len(total_time)


if __name__ == "__main__":
    main()
