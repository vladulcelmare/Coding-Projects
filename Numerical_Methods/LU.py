import random
import numpy as np

n = int(input("Enter matrix dimension: "))
ep = int(input("Enter precision for epsilon : " ))
eps = pow(10,-ep)
min = int(input("Enter the minimum value range : "))
max = int(input("Enter the maximum value range : "))

A = [[round((max - min) * random.random() + min, ep) for _ in range(n)] for _ in range(n)]
A_init = [[]]

SOL = [round((max - min) * random.random() + min, ep) for _ in range(n)]
SOL_init = []

x = [0 for _ in range(n)]
x_lib = np.zeros(n)

def euclidean_norm(v):
    norm = 0
    for i in v:
        norm+=abs(i)*abs(i)
    
    norm = np.sqrt(norm)
    return norm


def check_division(value):
    if abs(value) > eps:
        return True
    
    return False


def check_sing_t(T,size):
    for i in range(0,size):
        if T[i][i] == 0:
            return False

    return True


def tri_det(T,size):
    result = 1
    for i in range(0,size):
        result *= T[i][i]
    
    return round(result, ep)


def compute_det(U):
    if check_sing_t(U,n):
        return tri_det(U,n)
    else:
        print("Cannot compute. A is not LU compatible.")
        return 0
    

def inf_substitution(matrix):
    global SOL 
    for i in range(n):
        sum = 0
        for j in range(i):
            sum += matrix[i][j] * x[j] 
        x[i] = SOL[i] - sum
    
    SOL = x


def sup_substitution(matrix):
    global SOL 
    for i in range(n - 1, -1, -1):
        sum = 0
        for j in range(i + 1, n):
            sum += matrix[i][j] * x[j]

        if(check_division(matrix[i][i])):
            x[i] = (SOL[i] - sum)/matrix[i][i]
        else:
            print('Nu se poate face impartirea')


def doolittle(A):
    for p in range(n):
        for i in range(p, n):
            sum = 0
            for k in range(p):
                sum += A[p][k] * A[k][i]
            A[p][i] = A_init[p][i] - sum

        for i in range(p + 1, n):
            sum = 0
            for k in range(p):
                sum += A[i][k] * A[k][p]
            if(check_division(A[p][p])):
                    A[i][p] = (A_init[i][p] - sum) / A[p][p]
            else:
                print('Nu se poate face impartirea')
    
    A = [[round(x, ep) for x in line] for line in A]
    print('\nDescompunere LU:\n')
    for i in range(n):
        print(A[i])


def solve(A,SOL,x):
    global A_init, SOL_init, x_lib

    A_init = [row[:] for row in A]
    SOL_init = SOL[:]

    print("\nMatricea sistemului si termenii liberi:\n")
    for i in range(n):
        print(A_init[i], SOL_init[i])

    doolittle(A)

    print('\nDeterminant: ', compute_det(A))
    
    inf_substitution(A)
    sup_substitution(A)

    x = [round(value, ep) for value in x]
    print("\nSolutia calculata: ", x)
    
    A_init_np = np.array(A_init)
    x_np = np.array(x)
    SOL_np = np.array(SOL_init)
    
    print('\nVerificarea solutiei: ', euclidean_norm(A_init_np @ x_np - SOL_np))
    
    x_lib = np.linalg.solve(A_init_np, SOL_np)
    
    print('\nDiferenta solutie calculata si solutie numpy: ', euclidean_norm(x_np - x_lib))
    
    A_inv = np.linalg.inv(A_init_np)
    print("\nInversa matricei A:\n ")
    A_inv = [[round(x, ep).item() for x in line] for line in A_inv]
    for line in range(n):
        print(A_inv[line])
    
    print('\n||xLU - A^-1 @ b_init||2: ', euclidean_norm(x_np - A_inv @ SOL_np))


solve(A,SOL,x)

