import numpy as np
import random
import time

start = time.perf_counter()

n = int(input("Enter a value for n : "))
e = int(input("Select the precision : "))
min = int(input("Select the minimum value range : "))
max = int(input("Select the maximum value range : "))

s = [(max - min) * random.random() + min for _ in range(n)]
sol = [0 for _ in range(n)]

A = [[0 for j in range(n)] for i in range(n)]

In = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
Q = [row[:] for row in In]

x = [0 for _ in range(n)]
eps = pow(10,-e)


def build_matrix_sol(dimension , min_val , max_val):
    global A, sol , s
    for i in range(dimension):
        for j in range(dimension):
            A[i][j] = (max_val - min_val) * random.random() + min_val

    for i in range(dimension):
        sol[i] = sum((s[j] * A[i][j]) for j in range(n))


def check_singular(R):
    for i in range(n):
        if abs(R[i][i]) < eps:
            return True
    
    return False


def check_division(value):
    if(abs(value) < eps):
        return False
    return True


def better_print(A, system = False):
    global n
    if system:
         for i in range(n):
            print("\n| ",end=" ")
        
            for j in range(n-1):
                print(f"{A[i][j]:.{e}f} , ",end=" ")
        
            print(f"{A[i][n-1]:.{e}f} |   | {sol[i]:.{e}f} |")
 
    else:
        for i in range(n):
            print("\n| ",end=" ")
        
            for j in range(n-1):
                print(f"{A[i][j]:.{e}f} , ",end=" ")
        
            print(f"{A[i][n-1]:.{e}f} |")
    

def euclidean_norm(v):
    norm = 0
    for i in v:
        norm+=abs(i) * abs(i)

    return np.sqrt(norm)


def euclidean_norm_matrix(matrix):
    norm = 0
    for line in matrix:
        for x in line:
            norm += abs(x) * abs(x)
    return np.sqrt(norm)


def transpose(A):
    global n
    transposed = [list(row) for row in zip(*A)]

    return transposed


def solve_QR():
    global A , Q , n , sol , In 

    for r in range(n-1):

        sigma = sum( (A[j][r] * A[j][r]) for j in range(r,n) ) 
        
        if sigma <= eps :
            break
        
        k = np.sqrt(sigma)

        if(A[r][r] > 0) :
            k = -k
        
        beta = sigma - k * A[r][r]

        if beta <= eps :
            break
        
        u = [0 for _ in range(n)]
        u[r] = A[r][r] - k
        
        for i in range(r+1,n):
            u[i] = A[i][r]
        
        for j in range(r+1,n):
            gamma = sum( u[i] * A[i][j] for i in range(r,n)) / beta
            for i in range(r,n):
                A[i][j] = A[i][j] - gamma * u[i]
            
        A[r][r] = k
        for i in range(r+1,n):
            A[i][r] = 0
        
        gamma = sum( u[i] * sol[i] for i in range(r,n)) / beta 
        for i in range(r,n):
            sol[i] = sol[i] - gamma * u[i]

        for j in range(n):
            gamma = sum( u[i] * Q[j][i] for i in range(r,n)) / beta
            for i in range(r,n):
                Q[j][i] = Q[j][i] - gamma * u[i]


def solve_upper_tr(A, sol):
    for i in range(n - 1, -1, -1):
        sum = 0
        for j in range(i + 1, n):
            sum += A[i][j] * x[j]

        if(check_division(A[i][i])):
            x[i] = (sol[i] - sum)/A[i][i]
        else:
            print('Nu se poate face impartirea')

    return x


def House_inverse(Q, R):
    if check_singular(A):
        return False
    
    else:
        A_inv_House = [[0 for j in range(n)] for i in range(n)]

        for j in range(n):
            x = solve_upper_tr(R, Q[j])
            for i in range(n):
                A_inv_House[i][j] = x[i]

        return A_inv_House
    
build_matrix_sol(n,min,max)
A_init = np.array([row[:] for row in A])
sol_init = np.array(sol[:])

print("\n--- MATRICEA SISTEMULUI ---")
better_print(A, True)
solve_QR()

print("\n--- MATRICEA Q ---")
better_print(Q)

print("\n--- MATRICEA Q TRANSPUS ---")
QT = transpose(Q)
better_print(QT)

print("\n--- MATRICEA R ---")
better_print(A)

x_QR = np.array(np.linalg.solve(A_init, sol_init))
x_Householder = solve_upper_tr(A, QT @ sol_init) 

print("\n--- NORME --- \n")

print("||x_QR - x_Householder|| = ", euclidean_norm(x_QR - x_Householder))
print("||A_init * x_Householder - b_init|| = ", euclidean_norm(A_init @ x_Householder - sol_init))
print("||A_init * x_QR - b_init|| = ", euclidean_norm(A_init @ x_QR - sol_init))
print("||x_Householder - s|| / ||s|| = ", euclidean_norm(x_Householder - np.array(s)) / euclidean_norm(s))
print("||x_QR - s|| / ||s|| = ", euclidean_norm(x_QR - np.array(s)) / euclidean_norm(s))

A_inv_House = House_inverse(Q, A)
if(A_inv_House):
    print("\n\n--- INVERSA MATRICEI SISTEMULUI ---")
    better_print(A_inv_House)

    A_inv_np = np.linalg.inv(A_init)
    print("\n||A_inv_Householder - A_inv_numpy||", 
          euclidean_norm_matrix(A_inv_House - A_inv_np))

print("\n\n--- VERIFICARI ---\n")

print("||Q R - A|| =",
      euclidean_norm_matrix(np.array(Q) @ A - A_init))

print("\n||Q^T Q - I|| =",
      euclidean_norm_matrix(np.array(QT) @ Q - np.array(In)))



