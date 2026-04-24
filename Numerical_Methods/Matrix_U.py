import numpy as np
import Functions as Func
import random
import tkinter as tk

def safe_fetch(i, default=0):
    try:
        return Func.Fetch_Data(i)
    except:
        return default

m = 1 # default values, they dont overwrite anything , just for global functions sake
n = 1
ep = 5
min_val = 0
max_val = 1

def euclidean_norm(v): # computes || ||2
    norm = 0
    for i in v:
        norm += abs(i) * abs(i)
    return np.sqrt(norm)

def manhattan_norm(v): # computes || ||1
    norm = 0
    for i in v:
        norm += abs(i)
    return norm

def inf_norm(v): # computes || ||inf
    max_val_norm = abs(v[0])
    for i in v:
        if abs(i) > max_val_norm:
            max_val_norm = abs(i)
    return max_val_norm

def check_division(value): # division check
    if abs(value) > pow(10, -ep):
        return True
    return False

def check_sing_t(T, size): # checks whether a triangular matrix is singular
    for i in range(size):
        if abs(T[i][i]) < pow(10, -ep):
            return True
    return False

def tri_det(T, size): # computes the determinant of a triangular matix
    result = 1
    for i in range(size):
        result *= T[i][i]
    return round(result, ep)

def compute_det(U): # computes the determinant for A ( L has L[i][i] = 1 so the det is 1, therefore detA = detU and it is triangular)
    if not check_sing_t(U, n):
        return tri_det(U, n)
    else:
        print("Cannot compute. A is not LU compatible.")
        return 0

def transpose(A): # transpose
    return [list(row) for row in zip(*A)]

def matmul(A, B): # matrix multiplication, done fast (thanks web)
    return [
        [
            sum(A[i][k] * B[k][j] for k in range(len(B)))
            for j in range(len(B[0]))
        ]
        for i in range(len(A))
    ]

def random_LU():
    global m, n, min_val, max_val, ep

    n = int(Func.Fetch_Data(3))
    m = int(Func.Fetch_Data(2))
    min_val_f, max_val_f = Func.Fetch_Data(4)
    min_val = float(min_val_f)
    max_val = float(max_val_f)
    ep = int(Func.Fetch_Data(5))

    if m < n:
        print("LU does not work for this case. Please try QR or SVD")
        return -1

    A_gen = [[round((max_val - min_val) * random.random() + min_val, ep) for _ in range(n)] for _ in range(m)]
 
    SOL_gen = [round((max_val - min_val) * random.random() + min_val, ep) for _ in range(m)]

    if m > n:
        print("\nComputing (A^T * A) since m > n...")
        A_T = transpose(A_gen)
        A = matmul(A_T, A_gen)
        SOL = [sum(A_T[i][k] * SOL_gen[k] for k in range(m)) for i in range(n)]
    else:
        A = A_gen
        SOL = SOL_gen

    A_init = [row[:] for row in A] # copies A, in A we will only have L and U at the end
    
    
    y = [0 for _ in range(n)] # Ly = b
    x = [0 for _ in range(n)] # Ux = y
    
    x_lib = np.zeros(n)

    def inf_substitution(matrix, SOL_in): # inferior direct substitution , pretty straightforward
        for i in range(n):
            s = 0
            for j in range(i):
                s += matrix[i][j] * y[j]
            y[i] = SOL_in[i] - s

    def sup_substitution(matrix): # superior ---||---
        for i in range(n - 1, -1, -1):
            s = 0
            for j in range(i + 1, n):
                s += matrix[i][j] * x[j]

            if check_division(matrix[i][i]):
                x[i] = (y[i] - s) / matrix[i][i]
            else:
                print(f"Cannot compute division. Value too low : {matrix[i][i]}")

    def doolittle(mat_A):
        for p in range(n):
            for i in range(p, n):
                s = 0
                for k in range(p):
                    s += mat_A[p][k] * mat_A[k][i]
                mat_A[p][i] = A_init[p][i] - s

            for i in range(p + 1, n):
                s = 0
                for k in range(p):
                    s += mat_A[i][k] * mat_A[k][p]

                if check_division(mat_A[p][p]):
                    mat_A[i][p] = (A_init[i][p] - s) / mat_A[p][p]
                else:
                    print(f"Cannot compute division. Value too low : {mat_A[p][p]}")

        mat_A[:] = [[round(val, ep) for val in row] for row in mat_A]

        print("\nLU factorisation:\n")
        for row in mat_A:
            print(row)

    def solve(mat_A, SOL_vec, final_x):
        global x_lib

        print("\nA & SOL (System Matrix and Free Terms):\n")
        for i in range(n):
            print(A_init[i], SOL_vec[i])

        doolittle(mat_A)

        print("\nDeterminant:", compute_det(mat_A))

        inf_substitution(mat_A, SOL_vec)
        sup_substitution(mat_A)

        for i in range(n):
            final_x[i] = round(x[i], ep)
            
        print("\nComputed result:", final_x)

        A_init_np = np.array(A_init)
        x_np = np.array(final_x)
        SOL_np = np.array(SOL_vec)

        print("\nVerify ||Ax - b||2:", euclidean_norm(A_init_np @ x_np - SOL_np))

        try:
            x_lib = np.linalg.solve(A_init_np, SOL_np)
            print("\nDifference vs. numpy:", euclidean_norm(x_np - x_lib))
        except:
            print("\nNumpy could not solve (Singular Matrix).")

        try:
            A_inv = np.linalg.inv(A_init_np)
            print("\nInverse A:\n")
            A_inv_rounded = [[round(val, ep) for val in row] for row in A_inv]
            for row in A_inv_rounded:
                print(row)

            diff_inv = euclidean_norm(x_np - A_inv @ SOL_np)
            print("\n||xLU - A^-1 b||2:", diff_inv)
        except:
            print("\nInverse could not be computed.")

    solve(A, SOL, x)
