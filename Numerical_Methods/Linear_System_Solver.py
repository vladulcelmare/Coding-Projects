import numpy as np
import Functions as Func
import Matrix_U as MU
import tkinter as tk

def Ask_User(): # very basic at first, but has a lot of functions behind. will only work if called, otherwise no program
    print("Console LOG")
    print("Welcome to a basic Linear Ecuation solver, made by me!")
    root = Func.Initialise_Root()
    return root

r = Ask_User()

r.mainloop()

