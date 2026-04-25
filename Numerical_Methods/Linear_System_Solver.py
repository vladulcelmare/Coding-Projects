import numpy as np
import Functions as Func
import Matrix_U as MU
import tkinter as tk
user_matrix = []

def Ask_User():
    global user_matrix
    print("Console LOG")
    print("Welcome to a basic Linear Ecuation solver, made by me!")
    root = Func.Initialise_Root()
    return root

r = Ask_User()

r.mainloop()

