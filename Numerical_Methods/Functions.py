import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Label
from tkinter import simpledialog
from tkinter import filedialog
from functools import partial
import Matrix_U as MU

parameters = [None for _ in range(6)]
matrix_data = []
sol_data = []
flag = False

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

def Error_Code_Guide():
    messagebox.showinfo("Possible error codes alongside their meaning : ", "\nCode 1 -> invalid input for LU / QR ; displays warning " \
    " \nCode 2 -> input is not numerical ; displays error " \
    " \nCode 3 -> error in receiving imported filename.txt ; displays error" \
    " \nCode 4 -> invalid .txt format ; displays error" \
    " \nCode 5 -> ambiguity ; displays error")

def Format_Matrix_Guide():
    messagebox.showinfo(".txt format :", "\n m(number of rows) n(number of columns) min max eps" \
    " \nA11 A12 ... A1n" \
    " \nA21 A22 ... A2n" \
    " \n..............." \
    " \nAm1 Am2 ... Amn" \
    " \n^^^^^^^^^^^^^^^" \
    " \nsystem matrix" \
    " \nb1 b2 ... bn" \
    " \n^^^^^^^^^^^^" \
    " \nsystem solution")

def Display_Error(code):
    if code == 1:
        messagebox.showwarning("WAR!" , f"Custom error code {code} ! Possible causes : \n LU -> m < n \n QR -> inverse cannot be computed as m != n")

    if code == 2:
        messagebox.showerror("ERR" , f"Custom error code {code} ! Reason : invalid input. Please revise the input")

def Check_fields():
    global parameters

    for i in range(2,6):
        if parameters[i] is None:
            return False
        
        if isinstance(parameters[i], tuple):
            for entry in parameters[i]:
                if Check_if_Number(entry.get()) == False:
                    return False
                
    for i in range(2,6):
        if isinstance(parameters[i], tuple):
            continue

        if Check_if_Number(parameters[i].get()) == False:
            return False
        

    return True

def set_entry(entry, value):
    entry.delete(0, tk.END)
    entry.insert(0, str(value))


def Import_From_File(result_box):
    global parameters, matrix_data, sol_data

    file_path = filedialog.askopenfilename(title="Select input file", filetypes=[("Text files", "*.txt")])

    if not file_path:
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        parts = lines[0].split()
        if len(parts) != 5:
            Display_Error(4)
            return

        m, n = map(int, parts[:2])
        min_val, max_val, eps = map(float, parts[2:])

        if len(lines) != 1 + m + 1:
            Display_Error(4)
            return

        A = []
        for i in range(1, 1 + m):
            row = list(map(float, lines[i].split()))
            if len(row) != n:
                Display_Error(4)
                return
            A.append(row)

        b = list(map(float, lines[1 + m].split()))
        if len(b) != m:
            Display_Error(4)
            return

        if flag:
            set_entry(parameters[2], m)
            set_entry(parameters[3], n)

            set_entry(parameters[4][0], min_val)
            set_entry(parameters[4][1], max_val)

            set_entry(parameters[5], eps)

        matrix_data = A[:]
        sol_data = b[:]
        
    except Exception as e:
        print(e)
        Display_Error(3)

def Print_Parameters():
    for i, p in enumerate(parameters):
        if p is None:
            print(i, "-> None")
        elif isinstance(p, tuple):
            print(i, "->", tuple(x.get() for x in p))
        else:
            print(i, "->", p.get())

def check(btn):
    global parameters 

    print("User has selected a new field")
    if Check_fields():
        print("All fields complete. Can now safely solve")
        btn.grid(row = 0, column = 1)
    else:
        btn.grid_remove()
        

def Combined_check_focus(event,btn):
    event.widget.tk_focusNext().focus()
    check(btn)
    return "break"

def print_to_textbox(result_box, mesaj):
    
    result_box.config(state="normal")
    
    result_box.delete("1.0", tk.END)

    if isinstance(mesaj, list):
        mesaj = "\n".join(str(x) for x in mesaj)

    result_box.insert(tk.END, str(mesaj) + "\n")
    
    result_box.config(state="disabled")

def Check_Function(result_box):
    global parameters

    if parameters[0].get() == "Yes" :
        
        if parameters[1].get() == "LU":
            result = MU.random_LU()
            print_to_textbox(result_box, result)

        elif parameters[1].get() == "QR":
            result = MU.random_QR()
            print_to_textbox(result_box, result)

    else:
        if parameters[1].get() == "LU":
            MU.random_LU()

        elif parameters[1].get() == "QR":
            print("ok")

def help():

    x = simpledialog.askinteger("Help prompt","Please type an option number to display the requested info \n 1. Code guide \n 2. .txt format")
    if x is None:
        return

    if x == 1:
        Error_Code_Guide()
    else:
        Format_Matrix_Guide()

def Initialise_Root():
    root = tk.Tk()
    root.title("Linear Equation Solver")
    root.geometry("800x600")
    
    root.columnconfigure(0, weight=1)

    root.rowconfigure(0, weight = 0)
    root.rowconfigure(1, weight = 1)
    root.rowconfigure(2, weight = 0)
    
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

    result_frame = ttk.LabelFrame(root, text="Solving linear system",labelanchor="n")
    result_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
    result_frame.columnconfigure(0, weight=1)
    result_frame.rowconfigure(0, weight=1)

    result_box = tk.Text(result_frame, wrap="none", height=15) 
    result_box.grid(row=0, column=0, sticky="nsew")

    
    yscroll = ttk.Scrollbar(result_frame, orient="vertical", command=result_box.yview)
    yscroll.grid(row=0, column=1, sticky="ns")
    xscroll = ttk.Scrollbar(result_frame, orient="horizontal", command=result_box.xview)
    xscroll.grid(row=1, column=0, sticky="ew")
    
    result_box.config(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    
    button_frame = ttk.Frame(root)
    button_frame.grid(row = 2, column = 0, sticky="ew")

    for i in range(3):
        if i == 1:
            button_frame.columnconfigure(i, weight = 1)
        else:
            button_frame.columnconfigure(i, weight = 0)
    
    button_frame.rowconfigure(0,weight=1)

    btn = ttk.Button(button_frame, text="Solve", command=partial(Check_Function, result_box))
    btn.grid(row = 0, column = 1)

    m_entry.bind("<Return>" , lambda e : Combined_check_focus(e , btn))
    n_entry.bind("<Return>" , lambda e : Combined_check_focus(e , btn))

    min_entry.bind("<Return>" , lambda e : Combined_check_focus(e , btn))
    max_entry.bind("<Return>" , lambda e : Combined_check_focus(e , btn))

    eps_entry.bind("<Return>" , lambda e : check(btn))

    btn.grid_remove()

    btn2 = ttk.Button(button_frame, text="Import")
    btn2.grid(row = 0, column = 0)


    btn3 = ttk.Button(button_frame, text="Help", command=help)
    btn3.grid(row = 0, column = 2)

    return root

