import numpy as np
import Functions as Func
import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Label
from tkinter import simpledialog
from tkinter import filedialog

def safe_fetch(i, default=0):
    try:
        return Func.Fetch_Data(i)
    except:
        return default

m = 1
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
    return sum(abs(i) for i in v)

def inf_norm(v): # computes || ||inf
    return max(abs(i) for i in v)

def check_division(value): # division check
    return abs(value) > pow(10, -ep)

def check_sing_t(T, size): # checks whether a square triangular matrix is singular
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
        messagebox.showwarning("WAR!" , "Not LU compatible. Determinant may be 0.")
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

def euclidean_norm_matrix(matrix): # matrix norm (thanks web) i think this is frobenius norm
    return np.sqrt(sum(abs(x) * abs(x) for row in matrix for x in row))


def format_row(row, decimals=None): # formatting functions
    global ep
    if decimals is None: # takes epsilon digits if None
        decimals = ep

    formatted = []
    for val in row:
        v = float(val)
        if v == 0.0: # ignores 0
            # placeholder, will be replaced after we know column width
            formatted.append(None)
        elif v < 0:
            formatted.append(f"{v:.{max(0, decimals - 1)}f}")
        else:
            formatted.append(f"{v:.{decimals}f}")

    # compute max width among non-zero entries
    max_width = max((len(s) for s in formatted if s is not None), default=decimals + 2)

    final = []
    for i, val in enumerate(row):
        if formatted[i] is None:
            # pad 0.0 to right matching max column width
            zero_str = f"{'0.0':>{max_width}}"
            final.append(zero_str)
        else:
            final.append(f"{formatted[i]:>{max_width}}")

    return "[" + ", ".join(final) + "]"


def random_LU():
    global m, n, min_val, max_val, ep

    text = []

    n = int(float(Func.Fetch_Data(3)))
    m = int(float(Func.Fetch_Data(2)))
    min_val_f, max_val_f = Func.Fetch_Data(4)
    min_val = float(min_val_f)
    max_val = float(max_val_f)
    ep = int(float(Func.Fetch_Data(5))) # takes every parameter inserted by user

    if m < n: # this case wont work for LU
        print("LU does not work for this case. Please try QR or SVD")
        Func.Display_Error(1)
        return -1

    A_gen = [[round((max_val - min_val) * random.random() + min_val, ep) for _ in range(n)] for _ in range(m)]
    # generates random A and SOL and rounds precision to the one given by user
    SOL_gen = [round((max_val - min_val) * random.random() + min_val, ep) for _ in range(m)]

    if m > n: # makes it into n x n 
        print("\nComputing (A^T * A) since m > n...")
        A_T = transpose(A_gen)
        A = matmul(A_T, A_gen)
        SOL = [sum(A_T[i][k] * SOL_gen[k] for k in range(m)) for i in range(n)]
    else:
        A = A_gen
        SOL = SOL_gen

    A_init = [row[:] for row in A]
    
    y = [0 for _ in range(n)] # Ly = b
    x = [0 for _ in range(n)] # Ux = y

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
                Func.Display_Error(2)

    def doolittle(mat_A):
        for p in range(n): # step p
            for i in range(p, n): # computes U row -> formula : Upi = SUM k = 1,p (Lpk * Uki)
                s = 0
                for k in range(p):
                    s += mat_A[p][k] * mat_A[k][i]
                mat_A[p][i] = A_init[p][i] - s

            for i in range(p + 1, n): # computes L column -> formula : Lip = (Aip - SUM k = 1,p (Lik * Ukp)) / Upp
                s = 0
                for k in range(p):
                    s += mat_A[i][k] * mat_A[k][p]

                if check_division(mat_A[p][p]):
                    mat_A[i][p] = (A_init[i][p] - s) / mat_A[p][p]
                else:
                    print(f"Cannot compute division. Value too low : {mat_A[p][p]}")
                    Func.Display_Error(2)

        mat_A[:] = [[round(val, ep) for val in row] for row in mat_A]

        text.append("\n--- LU factorisation (A holds L and U, L = lower part with 1 if i == j , U = upper) ---\n")
        for row in mat_A:
            text.append(format_row(row))

    def solve(mat_A, SOL_vec, final_x):

        text.append("\nA & SOL (System Matrix and Free Terms):\n")
        for i in range(n):
            text.append((f"Row {i}", format_row(A_init[i]), SOL_vec[i]))

        doolittle(mat_A)

        text.append("")
        text.append(("Determinant", compute_det(mat_A)))

        inf_substitution(mat_A, SOL_vec)
        sup_substitution(mat_A)

        for i in range(n):
            final_x[i] = round(x[i], ep)
            
        text.append("")
        text.append(("Computed result", format_row(final_x)))

        A_init_np = np.array(A_init)
        x_np = np.array(final_x)
        SOL_np = np.array(SOL_vec)

        text.append("")
        text.append(("Verify ||Ax - b||2", euclidean_norm(A_init_np @ x_np - SOL_np).item()))

        try:
            x_lib = np.linalg.solve(A_init_np, SOL_np)
            text.append("")
            text.append(("Difference vs. numpy", euclidean_norm(x_np - x_lib).item()))
        except:
            print("\nNumpy could not solve (Singular Matrix).")
            Func.Display_Error(1)

        try:
            if compute_det(A_init):
                A_inv = np.linalg.inv(A_init_np)
                text.append("\nInverse A:\n")
                A_inv_rounded = [[round(val.item(), ep) for val in row] for row in A_inv]
                for row in A_inv_rounded:
                    text.append(format_row(row))

                diff_inv = euclidean_norm(x_np - A_inv @ SOL_np).item()
                text.append("")
                text.append(("||xLU - A^-1 b||2", diff_inv))
        except:
            print("\nInverse could not be computed.")
            Func.Display_Error(1)

    solve(A, SOL, x)

    return text

steps = 0
def random_QR():
    global m, n, min_val, max_val, ep , steps
    text = []

    n = int(float(Func.Fetch_Data(3)))
    m = int(float(Func.Fetch_Data(2)))
    min_val_f, max_val_f = Func.Fetch_Data(4)
    min_val = float(min_val_f)
    max_val = float(max_val_f)
    ep = int(float(Func.Fetch_Data(5)))

    s = [(max_val - min_val) * random.random() + min_val for _ in range(n)]

    A = [[round((max_val - min_val) * random.random() + min_val, ep) for _ in range(n)] for _ in range(m)]
    SOL = [ sum(A[i][j] * s[j] for j in range(n)) for i in range(m)]

    A_init = [row[:] for row in A]
    b = SOL[:]

    Q = [[1 if i == j else 0 for j in range(m)] for i in range(m)]
    eps = pow(10,-ep)

    def check_singular(R):
        for i in range(min(m, n)):
            if abs(R[i][i]) < eps:
                return True
        return False

    def solve_QR():
        global steps
        steps = 0
        eps = pow(10,-ep)
        for r in range(min(m, n)):
            sigma = sum(A[j][r] ** 2 for j in range(r, m)) # computes sum (A[j][r] ^ 2)

            if sigma <= eps: # if sigma too small
                continue

            k = np.sqrt(sigma)

            if A[r][r] > 0:
                k = -k # opposite sign of sqrt

            beta = sigma - k * A[r][r] # computes beta

            if beta <= eps: # my own check , to avoid weird divisions
                continue
            
            steps += 1
            # always take m
            u = [0 for _ in range(m)]
            u[r] = A[r][r] - k # forms special U vector => 0 on first r elements, then formula then copies

            for i in range(r + 1, m):
                u[i] = A[i][r]

            for j in range(r + 1, n): # 2 fors make A into R which is Hn * ... * H1 * A , Hi = reflexion matrix
                gamma = sum(u[i] * A[i][j] for i in range(r, m)) / beta
                for i in range(r, m):
                    A[i][j] -= gamma * u[i]

            A[r][r] = k
            for i in range(r + 1, m):
                A[i][r] = 0 # cuz A is sup triangular

            gamma = sum(u[i] * SOL[i] for i in range(r, m)) / beta
            for i in range(r, m): # modifies sol since it keeps being multiplied with reflexion matrices
                SOL[i] -= gamma * u[i]

            for j in range(m): # modifies Q with Q transpose
                gamma = sum(u[i] * Q[j][i] for i in range(r, m)) / beta
                for i in range(r, m):
                    Q[j][i] -= gamma * u[i]

    def solve_upper_tr(R, b): # same as solve upper from LU, since R is superior triangular
        x_local = [0 for _ in range(n)]

        for i in range(min(n, len(R)) - 1, -1, -1):
            s = 0
            for j in range(i + 1, n):
                s += R[i][j] * x_local[j]

            if check_division(R[i][i]):
                x_local[i] = (b[i] - s) / R[i][i]
            else:
                print("Division error")
                Func.Display_Error(2)

        return x_local
    
    def House_inverse(Q, R): # computes inverse by treating it as a system
        
        if m != n:

            return
        
        if check_singular(R):
            Func.Display_Error(1)
            return False


        A_inv = [[0 for _ in range(m)] for _ in range(m)]

        #QT = transpose(Q) if householder returns q transpose

        for j in range(m):
            x_col = solve_upper_tr(R, Q[j])
            for i in range(m):
                A_inv[i][j] = x_col[i]

        return A_inv
    
    text.append("\nA & SOL (System Matrix and Free Terms):\n")
    for i in range(m):
        text.append((f"Row {i}", format_row(A_init[i]), b[i]))
        
    solve_QR()

    text.append("\n--- Q ---\n")
    for row in Q:
        text.append(format_row(np.array(row).tolist()))

    text.append("\n--- Q^T ---\n")
    QT = transpose(Q)
    for row in QT:
        text.append(format_row(np.array(row).tolist()))

    text.append("\n--- R ---\n")
    for row in A:
        text.append(format_row(np.array(row).tolist()))

    if(m == n):
        text.append("")
        text.append(("Determinant", tri_det(A,n).item() * pow(-1, steps)))

    x_QR = np.linalg.lstsq(A_init, b, rcond=None)[0]

    x_custom = solve_upper_tr(A, np.array(QT) @ np.array(b))
    
    text.append("")
    text.append(("Computed result", format_row(np.array(x_custom).tolist())))

    text.append("")
    text.append(("Verify ||QR - A||2", euclidean_norm_matrix(np.array(Q) @ A - A_init).item()))
    print("Computed euclidean norm to check factorisation accuracy")

    text.append("")
    text.append(("Difference vs. numpy", euclidean_norm(x_QR - x_custom).item()))
    print("Computed euclidean norm to check solution accuracy")

    text.append("")
    text.append(("||Q^T Q - I||2", euclidean_norm_matrix(np.array(QT) @ np.array(Q) - np.eye(m)).item()))
    print("Computed euclidean norm to verify corectness for Q")

    if(m == n):
        text.append("\nInverse A:\n")
        invA = House_inverse(Q,A)
        for row in invA:
            text.append(format_row(np.array(row).tolist()))
    
        text.append("")
        text.append(("||A*A-1 - I||2", euclidean_norm_matrix(np.array(A_init) @ np.array(invA) - np.eye(m)).item()))
        print("Computed euclidean norm to verify A-1 accuracy. Result may vary due to random input")
    else:
        Func.Display_Error(1)
    return text

def fixed_LU():
    global m, n, min_val, max_val, ep

    text = []

    n = int(float(Func.Fetch_Data(3)))
    m = int(float(Func.Fetch_Data(2)))
    min_val_f, max_val_f = Func.Fetch_Data(4)
    min_val = float(min_val_f)
    max_val = float(max_val_f)
    ep = int(float(Func.Fetch_Data(5))) # takes every parameter inserted by user

    if m < n: # this case wont work for LU
        print("LU does not work for this case. Please try QR or SVD")
        Func.Display_Error(1)
        return -1

    A_gen , SOL_gen = Func.Fetch_Matrix_Sol()

    print(A_gen, SOL_gen)

    if m > n: # makes it into n x n 
        print("\nComputing (A^T * A) since m > n...")
        A_T = transpose(A_gen)
        A = matmul(A_T, A_gen)
        SOL = [sum(A_T[i][k] * SOL_gen[k] for k in range(m)) for i in range(n)]
    else:
        A = A_gen
        SOL = SOL_gen

    A_init = [row[:] for row in A]
    
    y = [0 for _ in range(n)] # Ly = b
    x = [0 for _ in range(n)] # Ux = y

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
                Func.Display_Error(2)

    def doolittle(mat_A):
        for p in range(n): # step p
            for i in range(p, n): # computes U row -> formula : Upi = SUM k = 1,p (Lpk * Uki)
                s = 0
                for k in range(p):
                    s += mat_A[p][k] * mat_A[k][i]
                mat_A[p][i] = A_init[p][i] - s

            for i in range(p + 1, n): # computes L column -> formula : Lip = (Aip - SUM k = 1,p (Lik * Ukp)) / Upp
                s = 0
                for k in range(p):
                    s += mat_A[i][k] * mat_A[k][p]

                if check_division(mat_A[p][p]):
                    mat_A[i][p] = (A_init[i][p] - s) / mat_A[p][p]
                else:
                    print(f"Cannot compute division. Value too low : {mat_A[p][p]}")
                    Func.Display_Error(2)

        mat_A[:] = [[round(val, ep) for val in row] for row in mat_A]

        text.append("\n--- LU factorisation (A holds L and U, L = lower part with 1 if i == j , U = upper) ---\n")
        for row in mat_A:
            text.append(format_row(row))

    def solve(mat_A, SOL_vec, final_x):

        text.append("\nA & SOL (System Matrix and Free Terms):\n")
        for i in range(n):
            text.append((f"Row {i}", format_row(A_init[i]), SOL_vec[i]))

        doolittle(mat_A)

        text.append("")
        text.append(("Determinant", compute_det(mat_A)))

        inf_substitution(mat_A, SOL_vec)
        sup_substitution(mat_A)

        for i in range(n):
            final_x[i] = round(x[i], ep)
            
        text.append("")
        text.append(("Computed result", format_row(final_x)))

        A_init_np = np.array(A_init)
        x_np = np.array(final_x)
        SOL_np = np.array(SOL_vec)

        text.append("")
        text.append(("Verify ||Ax - b||2", euclidean_norm(A_init_np @ x_np - SOL_np).item()))

        try:
            x_lib = np.linalg.solve(A_init_np, SOL_np)
            text.append("")
            text.append(("Difference vs. numpy", euclidean_norm(x_np - x_lib).item()))
        except:
            print("\nNumpy could not solve (Singular Matrix).")
            Func.Display_Error(1)

        try:
            if compute_det(A_init):
                A_inv = np.linalg.inv(A_init_np)
                text.append("\nInverse A:\n")
                A_inv_rounded = [[round(val.item(), ep) for val in row] for row in A_inv]
                for row in A_inv_rounded:
                    text.append(format_row(row))

                diff_inv = euclidean_norm(x_np - A_inv @ SOL_np).item()
                text.append("")
                text.append(("||xLU - A^-1 b||2", diff_inv))
        except:
            print("\nInverse could not be computed.")
            Func.Display_Error(1)

    solve(A, SOL, x)

    return text

def fixed_QR():
    global m, n, min_val, max_val, ep , steps
    text = []

    n = int(float(Func.Fetch_Data(3)))
    m = int(float(Func.Fetch_Data(2)))
    min_val_f, max_val_f = Func.Fetch_Data(4)
    min_val = float(min_val_f)
    max_val = float(max_val_f)
    ep = int(float(Func.Fetch_Data(5)))

    A , SOL = Func.Fetch_Matrix_Sol()

    A_init = [row[:] for row in A]
    b = SOL[:]

    Q = [[1 if i == j else 0 for j in range(m)] for i in range(m)]
    eps = pow(10,-ep)

    def check_singular(R):
        for i in range(min(m, n)):
            if abs(R[i][i]) < eps:
                return True
        return False

    def solve_QR():
        global steps
        steps = 0
        eps = pow(10,-ep)
        for r in range(min(m, n)):
            sigma = sum(A[j][r] ** 2 for j in range(r, m)) # computes sum (A[j][r] ^ 2)

            if sigma <= eps: # if sigma too small
                continue

            k = np.sqrt(sigma)

            if A[r][r] > 0:
                k = -k # opposite sign of sqrt

            beta = sigma - k * A[r][r] # computes beta

            if beta <= eps: # my own check , to avoid weird divisions
                continue
            
            steps += 1
            # always take m
            u = [0 for _ in range(m)]
            u[r] = A[r][r] - k # forms special U vector => 0 on first r elements, then formula then copies

            for i in range(r + 1, m):
                u[i] = A[i][r]

            for j in range(r + 1, n): # 2 fors make A into R which is Hn * ... * H1 * A , Hi = reflexion matrix
                gamma = sum(u[i] * A[i][j] for i in range(r, m)) / beta
                for i in range(r, m):
                    A[i][j] -= gamma * u[i]

            A[r][r] = k
            for i in range(r + 1, m):
                A[i][r] = 0 # cuz A is sup triangular

            gamma = sum(u[i] * SOL[i] for i in range(r, m)) / beta
            for i in range(r, m): # modifies sol since it keeps being multiplied with reflexion matrices
                SOL[i] -= gamma * u[i]

            for j in range(m): # modifies Q with Q transpose
                gamma = sum(u[i] * Q[j][i] for i in range(r, m)) / beta
                for i in range(r, m):
                    Q[j][i] -= gamma * u[i]

    def solve_upper_tr(R, b): # same as solve upper from LU, since R is superior triangular
        x_local = [0 for _ in range(n)]

        for i in range(min(n, len(R)) - 1, -1, -1):
            s = 0
            for j in range(i + 1, n):
                s += R[i][j] * x_local[j]

            if check_division(R[i][i]):
                x_local[i] = (b[i] - s) / R[i][i]
            else:
                print("Division error")
                Func.Display_Error(2)

        return x_local
    
    def House_inverse(Q, R): # computes inverse by treating it as a system
        
        if m != n:

            return
        
        if check_singular(R):
            return False

        A_inv = [[0 for _ in range(m)] for _ in range(m)]

        #QT = transpose(Q) if householder returns q transpose

        for j in range(m):
            x_col = solve_upper_tr(R, Q[j])
            for i in range(m):
                A_inv[i][j] = x_col[i]

        return A_inv
    
    text.append("\nA & SOL (System Matrix and Free Terms):\n")
    for i in range(m):
        text.append((f"Row {i}", format_row(A_init[i]), b[i]))
        
    solve_QR()

    text.append("\n--- Q ---\n")
    for row in Q:
        text.append(format_row(np.array(row).tolist()))

    text.append("\n--- Q^T ---\n")
    QT = transpose(Q)
    for row in QT:
        text.append(format_row(np.array(row).tolist()))

    text.append("\n--- R ---\n")
    for row in A:
        text.append(format_row(np.array(row).tolist()))

    if(m == n):
        text.append("")
        text.append(("Determinant", tri_det(A,n).item() * pow(-1, steps)))

    x_QR = np.linalg.lstsq(A_init, b, rcond=None)[0]

    x_custom = solve_upper_tr(A, np.array(QT) @ np.array(b))
    
    text.append("")
    text.append(("Computed result", format_row(np.array(x_custom).tolist())))

    text.append("")
    text.append(("Verify ||QR - A||2", euclidean_norm_matrix(np.array(Q) @ A - A_init).item()))
    print("Computed euclidean norm to check factorisation accuracy")

    text.append("")
    text.append(("Difference vs. numpy", euclidean_norm(x_QR - x_custom).item()))
    print("Computed euclidean norm to check solution accuracy")

    text.append("")
    text.append(("||Q^T Q - I||2", euclidean_norm_matrix(np.array(QT) @ np.array(Q) - np.eye(m)).item()))
    print("Computed euclidean norm to verify corectness for Q")

    if(m == n):
        text.append("\nInverse A:\n")
        invA = House_inverse(Q,A)
        for row in invA:
            text.append(format_row(np.array(row).tolist()))
    
        text.append("")
        text.append(("||A*A-1 - I||2", euclidean_norm_matrix(np.array(A_init) @ np.array(invA) - np.eye(m)).item()))
        print("Computed euclidean norm to verify A-1 accuracy. Result may vary due to random input")
    else:
        Func.Display_Error(1)
    return text