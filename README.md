# Manufacturing Production Line Optimizer

An advanced optimization suite designed to solve the Car Sequencing Problem, minimizing production penalties in an automated assembly line through three approaches: Exact, Greedy, and Metaheuristic algorithms.

## The Challenge
In automotive manufacturing, different car classes require specific upgrades at dedicated work stations. Each station has a capacity constraint: **at most `C_e` cars requiring a specific upgrade can be processed in any window of `N_e` consecutive cars.**

Violating these constraints incurs a financial penalty (for every window: max{0, i - c_e}). This project aims to find the optimal production sequence to minimize the total penalty cost across all stations.

## Implemented Strategies

The project provides three distinct approaches to handle different problem scales:

1. **Exhaustive Search (`exh.py`):** - Uses Backtracking to find the absolute optimal solution.
   - Optimized with a Lower Bound function that prunes branches by calculating the minimum inevitable future cost.
   - Features "any-time" behavior: writes the best solution found so far to the output file.

2. **Greedy Constructor (`greedy.py`):**
   - A high-speed heuristic that builds the sequence car-by-car.
   - Uses a weighted penalty function considering: current cost, remaining cars per class, and "class risk" (how likely a class is to cause future conflicts).

3. **Advanced Metaheuristic (`mh.py`):**
   - Implements a GRASP (Greedy Randomized Adaptive Search Procedure) framework.
   - Combines a Randomized Greedy constructor with a Simulated Annealing local search to escape local minima.
   - Dynamically adjusts the "temperature" to refine the solution over time.

## Performance & Compilation
To achieve C-like performance while maintaining Python's flexibility, all `.py` files are designed to be compiled using Codon.

### Compilation
```bash
# Compile the Python scripts with Codon
codon build -release exh.py
codon build -release greedy.py
codon build -release mh.py

# Compile the C++ validation checker
g++ -O3 checker.cc -o checker
```

## Testing & Validation

### 1. The Checker
To ensure a solution is valid (correct format and consistent cost), use the provided C++ checker:
```bash
./checker input.txt output.txt
```

*Note: The checker validates correctness, not optimality.*

### 2. Automated Benchmark Script (`test.py`)
I developed a comprehensive testing utility that automates the evaluation of any algorithm across multiple public benchmarks:
- **Automatic Validation:** Runs the algorithm and immediately pipes it through the `checker`.
- **Performance Tracking:** Logs execution time and calculates cost averages.
- **Result Comparison:** Maintains a record of costs found in `public_benchs/` (easy, medium, and hard instances) to track progress.

Run it using:
```bash
python3 test.py <script_to_test> <results_summary_file>
```

## Technical Features
- **Algorithm Design:** Backtracking, Greedy heuristics, and Local Search.
- **Operations Research:** Resource-constrained scheduling and penalty minimization.
- **Performance Optimization:** Using Codon for high-performance computing and efficient state management in Python.
- **Automation:** Built a custom testing infrastructure for CI/CD-like validation.

## Contributions
This project was developed for the Algorithms & Programming III course at UPC.
