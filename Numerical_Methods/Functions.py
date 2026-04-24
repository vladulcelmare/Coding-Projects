import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Label
from tkinter import simpledialog
import Matrix_U as MU

parameters = [None for _ in range(6)]

def Check_if_Number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
    
def Fetch_Data(index):
    global parameters
    if index == 4:
        return (parameters[4][0].get(), parameters[4][1].get())
    
    return parameters[index].get()

def Print_Parameters():
    for i, p in enumerate(parameters):
        if p is None:
            print(i, "-> None")
        elif isinstance(p, tuple):
            print(i, "->", tuple(x.get() for x in p))
        else:
            print(i, "->", p.get())

def Initialise_Root():
    root = tk.Tk()
    root.title("Linear Equation Solver")
    root.geometry("800x600")
    
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    top_frame = ttk.Frame(root)
    top_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    for i in range(5):
        top_frame.columnconfigure(i, weight=1)

    # 0 -> Random

    choice1 = tk.StringVar(value="Yes")
    parameters[0] = choice1
    random_frame = ttk.LabelFrame(top_frame, text="Random?")
    random_frame.grid(row=0, column=0, sticky="nsew", padx=5)
    random_frame.columnconfigure((0, 1), weight=1)
    tk.Radiobutton(random_frame, text="Yes", variable=choice1, value="Yes").grid(row=0, column=0)
    tk.Radiobutton(random_frame, text="No", variable=choice1, value="No").grid(row=0, column=1)

    # 1 -> Method

    choice2 = tk.StringVar(value="QR")
    parameters[1] = choice2
    method_frame = ttk.LabelFrame(top_frame, text="Method")
    method_frame.grid(row=0, column=1, sticky="nsew", padx=5)
    method_frame.columnconfigure((0, 1), weight=1)
    tk.Radiobutton(method_frame, text="LU", variable=choice2, value="LU").grid(row=0, column=0)
    tk.Radiobutton(method_frame, text="QR", variable=choice2, value="QR").grid(row=0, column=1)

    # 2 -> Size

    size_frame = ttk.LabelFrame(top_frame, text="Dimensions")
    size_frame.grid(row=0, column=2, sticky="nsew", padx=5)
    size_frame.columnconfigure((1, 3), weight=1)
    
    m_entry = ttk.Entry(size_frame, width=5)
    m_entry.grid(row=0, column=1, sticky="ew", padx=2)
    n_entry = ttk.Entry(size_frame, width=5)
    n_entry.grid(row=0, column=3, sticky="ew", padx=2)
    
    parameters[2] = m_entry
    parameters[3] = n_entry
    
    ttk.Label(size_frame, text="m:").grid(row=0, column=0, padx=2)
    ttk.Label(size_frame, text="n:").grid(row=0, column=2, padx=2)

    # 3 -> Range

    value_frame = ttk.LabelFrame(top_frame, text="Range")
    value_frame.grid(row=0, column=3, sticky="nsew", padx=5)
    value_frame.columnconfigure((1, 3), weight=1)
    
    min_entry = ttk.Entry(value_frame, width=5)
    min_entry.grid(row=0, column=1, sticky="ew", padx=2)
    max_entry = ttk.Entry(value_frame, width=5)
    max_entry.grid(row=0, column=3, sticky="ew", padx=2)
    
    ttk.Label(value_frame, text="min:").grid(row=0, column=0, padx=2)
    ttk.Label(value_frame, text="max:").grid(row=0, column=2, padx=2)

    parameters[4] = (min_entry , max_entry)
    # 4 -> Precision

    precision_frame = ttk.LabelFrame(top_frame, text="Precision")
    precision_frame.grid(row=0, column=4, sticky="nsew", padx=5)
    precision_frame.columnconfigure(1, weight=1)
    
    eps_entry = ttk.Entry(precision_frame, width=8)
    eps_entry.grid(row=0, column=1, sticky="ew", padx=5)
    
    parameters[5] = eps_entry
    
    ttk.Label(precision_frame, text="ε:").grid(row=0, column=0, padx=5)
    
    

    return root

def Check_Options(root):
    global parameters
    for i in parameters:
        if i is None:
            messagebox.showerror("Errpr, there are INVALID parameters.")

    btn = ttk.Button(root, text="Solve", command=MU.random_LU)
    btn.grid(row=1, column=0)

    return
