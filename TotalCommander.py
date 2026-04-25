import shutil
import tkinter as tk
import os
from tkinter import messagebox
from tkinter import Label
from tkinter import ttk
from tkinter import simpledialog
from functools import partial
import cryptography
from cryptography.fernet import Fernet
import datetime

# global list to store the previous paths (useful for displaying the path)
list_left = []
list_right = []
last_isleft = True


# functions
def set_last(flag):
    global last_isleft
    last_isleft = flag

def ConvertSize(num_bytes):
    if num_bytes is None:
        return ""  # we cannot display the size of the folder/file
    units = ["B", "KB", "MB", "GB", "TB"]  # standard data size
    size = float(num_bytes)  # precise values
    pos = 0  # we start on position 0 (bytes)
    while size >= 1024:
        if pos <= 3:  # not out of bounds
            size /= 1024
            pos += 1
    if pos == 0:
        return f"{size:.0f} {units[pos]}"  # .0f means we have 0 numbers after ,
    return f"{size:.1f} {units[pos]}"


def FFDate(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime("%Y-%m-%d %H:%M")


def get_global_left():  # returns the path entered dynamically by the user
    path = entry_search_left.get()  # we take the input
    global last_isleft
    last_isleft = True
    path = os.path.expanduser(os.path.expandvars(path))  # path.expanduser expands into the full path, expandvars expands for windows environments
    if not path:  # if we typed nothing
        return

    if not os.path.isdir(path):  # if what we typed isnt a thing
        messagebox.showwarning("Invalid path", f"Directory not found:\n{path}")
        return
    if path == '.':
        path = os.getcwd()
    print(f"User has typed {path} in the LEFT PANEL")
    return path


def get_global_right(): 
    path = entry_search_right.get()   
    global last_isleft
    last_isleft = False
    path = os.path.expanduser(os.path.expandvars(path)) 
    if not path:
        # if we typed nothing
        return

    if not os.path.isdir(path):
        messagebox.showwarning("Invalid path", f"Directory not found:\n{path}")
        return
    if path == '.':
        path = os.getcwd()
    print(f"User has typed {path} on the RIGHT PANEL")
    return path


def load_directory_left(): # loads the file treeview in accordance with the entry
    path = get_global_left()    # we take the input
    global last_isleft
    last_isleft = True
    list_left.clear()  # in case the user wants to reset, we do not want to have the old path added onto the new one

    if path is None:
        return

    path_entry_left.config(state='normal')  # converted from read only
    path_entry_left.delete(0, tk.END)  # we delete the old path
    path_entry_left.insert(0, path)  # we place the path
    path_entry_left.config(state='readonly')  # we go back to read only

    for item in files_tree_left.get_children():  # we want to delete everything that was displayed before
        files_tree_left.delete(item)

    list_left.append(path)  # to avoid forgetting the old path, we will memorise it in a list

    try:
        with os.scandir(path) as entries:  # in entries we memorise os.scandir(our input) = iterator
            sorted_entries = sorted(
                entries,
                key=lambda e: (not e.is_dir(), e.name.lower())  # converts into a tuple : lambda is a single short line function which returns (...) due to ,
            )

            for entry in sorted_entries: # we go through the previously sorted elements of the iterator
                try:
                    symbol = "📁" if entry.is_dir() else "📄"
                    if entry.is_dir():#if folder
                        try:
                            count = sum(1 for i in os.scandir(entry.path))  # we count the number of items a folder has, returns 1 if its an item
                            size_display = f"{count} Items"
                        except PermissionError:
                            size_display = "Cannot compute size"
                        type_display = "Folder"
                    else:#if file
                        stat = entry.stat()# memorises the details of the folder
                        size_display = ConvertSize(stat.st_size) # for size
                        ext = os.path.splitext(entry.name)[1].lower() # takes the .extension
                        type_display = f"{ext[1:].upper()} file" if ext else "File" # removes the .

                    mtime = FFDate(entry.stat().st_mtime)

                    files_tree_left.insert("", "end", values=(  # the order in which we insert : symbol, file/folder name, type, size, last time modified
                        symbol,
                        entry.name,
                        type_display,
                        size_display,
                        mtime
                    ))
                    print(f"Data displayed accurately for {entry.name} in {path}")
                except (PermissionError, OSError):
                    print(f"ERR - PERMISION DENIED to {entry.name} in {path}")
                    continue
        
    except PermissionError:
        print(f"ERR - ACCESS DENIED to {path}")
        messagebox.showerror("Error", f"Access denied to:\n{path}")
    except Exception as e:
        print(f"ERR - ? in {path}")
        messagebox.showerror("Error", str(e))


def click_directory_left(event):
    path = list_left[0]  # we get the old value
    
    item_id = files_tree_left.identify_row(event.y)

    if not item_id:
        return
    values = files_tree_left.item(item_id, "values")

    if not values:
        return
    filename = values[1]  # the name of the folder we click on
    path = os.path.join(path, filename)  

    if not path:  # if we chose nothing
        messagebox.showwarning("Empty path", "Please choose a valid path first!")
        return

    if not os.path.isdir(path):  # if what we chose isnt a thing
        messagebox.showwarning("Invalid path", f"Directory not found:\n{path}")
        return
    list_left.pop()  # we remove it if safe to do so
    list_left.append(path)  # we place it again in the list

    path_entry_left.config(state='normal')  
    path_entry_left.delete(0, tk.END)  
    path_entry_left.insert(0, path)  
    path_entry_left.config(state='readonly')  

    for item in files_tree_left.get_children():  # we want to delete everything that was displayed before
        files_tree_left.delete(item)

    try:
        with os.scandir(path) as entries:  
            sorted_entries = sorted(
                entries,
                key=lambda e: (not e.is_dir(), e.name.lower())  
            )

            for entry in sorted_entries:
                try:
                    symbol = "📁" if entry.is_dir() else "📄"
                    if entry.is_dir():
                        try:
                            count = sum(1 for i in os.scandir(entry.path))
                            size_display = f"{count} Items"
                        except PermissionError:
                            size_display = "idk"
                        type_display = "Folder"
                    else:
                        stat = entry.stat()
                        size_display = ConvertSize(stat.st_size)
                        ext = os.path.splitext(entry.name)[1].lower()
                        type_display = f"{ext[1:].upper()} file" if ext else "File"
                        

                    mtime = FFDate(entry.stat().st_mtime)

                    files_tree_left.insert("", "end", values=(
                        symbol,
                        entry.name,
                        type_display,
                        size_display,
                        mtime
                    ))
                    print(f"Data displayed accurately for {entry.name} in {path}")
                except (PermissionError, OSError):
                    continue

    except PermissionError:
        print(f"ERR - ACCESS DENIED to {path}")
        messagebox.showerror("Error", f"Access denied to:\n{path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def load_directory_right():
    path = get_global_right()
    list_right.clear()
    global last_isleft
    last_isleft = False
    if path is None:
        return

    path_entry_right.config(state='normal')
    path_entry_right.delete(0, tk.END)
    path_entry_right.insert(0, path)
    path_entry_right.config(state='readonly')

    for item in files_tree_right.get_children():
        files_tree_right.delete(item)
    list_right.append(path)
    try:
        with os.scandir(path) as entries:
            sorted_entries = sorted(
                entries,
                key=lambda e: (not e.is_dir(), e.name.lower())
            )

            for entry in sorted_entries:
                try:
                    symbol = "📁" if entry.is_dir() else "📄"
                    if entry.is_dir():
                        try:
                            count = sum(1 for i in os.scandir(entry.path))
                            size_display = f"{count} Items"
                        except PermissionError:
                            size_display = "idk"
                        type_display = "Folder"
                    else:
                        stat = entry.stat()
                        size_display = ConvertSize(stat.st_size)
                        ext = os.path.splitext(entry.name)[1].lower()
                        type_display = f"{ext[1:].upper()} file" if ext else "File"

                    mtime = FFDate(entry.stat().st_mtime)
                    
                    files_tree_right.insert("", "end", values=(
                        symbol,
                        entry.name,
                        type_display,
                        size_display,
                        mtime
                    ))
                    print(f"Data displayed accurately for {entry.name} in {path}")
                except (PermissionError, OSError):
                    print(f"ERR - PERMISION DENIED to {entry.name} in {path}")
                    continue

    except PermissionError:
        print(f"ERR - ACCESS DENIED to {path}")
        messagebox.showerror("Error", f"Access denied to:\n{path}")
    except Exception as e:
        print(f"ERR - ? in {path}")
        messagebox.showerror("Error", str(e))


def click_directory_right(event):
    path = list_right[0]
    
    item_id = files_tree_right.identify_row(event.y)

    if not item_id:
        return
    values = files_tree_right.item(item_id, "values")
    if not values:
        return
    filename = values[1]
    path = os.path.join(path, filename)

    if not path:
        messagebox.showwarning("Empty path", "Please click on a directory path first!")
        return

    if not os.path.isdir(path):
        messagebox.showwarning("Invalid path", f"Directory not found:\n{path}")
        return

    list_right.pop()
    list_right.append(path)

    path_entry_right.config(state = 'normal')
    path_entry_right.delete(0, tk.END)
    path_entry_right.insert(0, path)
    path_entry_right.config(state = 'readonly')

    for item in files_tree_right.get_children():
        files_tree_right.delete(item)

    try:
        
        with os.scandir(path) as entries:
            sorted_entries = sorted(
                entries,
                key=lambda e: (not e.is_dir(), e.name.lower())
            )

            for entry in sorted_entries:
                try:
                    symbol = "📁" if entry.is_dir() else "📄"
                    if entry.is_dir():
                        try:
                            count = sum(1 for i in os.scandir(entry.path))
                            size_display = f"{count} Items"
                        except PermissionError:
                            size_display = "idk"
                        type_display = "Folder"
                    else:
                        stat = entry.stat() 
                        size_display = ConvertSize(stat.st_size)
                        ext = os.path.splitext(entry.name)[1].lower() 
                        type_display = f"{ext[1:].upper()} file" if ext else "File" 

                    mtime = FFDate(entry.stat().st_mtime)

                    files_tree_right.insert("", "end", values=(
                        symbol,
                        entry.name,
                        type_display,
                        size_display,
                        mtime
                    ))
                    print(f"Data displayed accurately for {entry.name} in {path}")
                except (PermissionError, OSError):
                    continue

    except PermissionError:
        print(f"ERR - ACCESS DENIED to {path}")
        messagebox.showerror("Error", f"Access denied to:\n{path}")
    except Exception as e:
        print(f"ERR - ? in {path}")
        messagebox.showerror("Error", str(e))

def refresh_left():
    current_path = path_entry_left.get().strip() # we take the path display minus blank spaces
    global last_isleft
    last_isleft = True
    if not current_path or not os.path.isdir(current_path):
        #if its invalid we stop
        return
  
    print(f"Refreshing left panel: {current_path}")
    
    entry_search_left.delete(0, tk.END) # we delete the old entry and we insert the last accessed entry
    entry_search_left.insert(0, current_path)
    load_directory_left()

def refresh_right():
    global last_isleft
    last_isleft = False
    current_path = path_entry_right.get().strip()
    if not current_path or not os.path.isdir(current_path):
        
        return
    
    print(f"Refreshing right panel: {current_path}")

    entry_search_right.delete(0, tk.END)
    entry_search_right.insert(0, current_path)
    load_directory_right()
    

def delete_selected():
    
    select_left = files_tree_left.selection() # we are looking to find where we clicked
    select_right = files_tree_right.selection()
    
    if select_left and select_right:
        if last_isleft == True:
            item = files_tree_left
            item_id = select_left[0] # the id of the first item chosen
            path = list_left[0] # current path
        else:
            item = files_tree_right
            item_id = select_right[0]
            path = list_right[0]
    elif select_left:
        item = files_tree_left
        item_id = select_left[0] # the id of the first item chosen
        path = list_left[0] # current path
    
    elif select_right:
        item = files_tree_right
        item_id = select_right[0]
        path = list_right[0]
    
    else:
        print ("No item selected in order to delete")
        return

    values = item.item(item_id, "values")
    filename = values[1] # the name since values has on pos 0 the name
    full_path = os.path.join(path, filename)

    if messagebox.askyesno("Delete", f"Delete {filename}?"):
        try:
            print(f"User has chosen to delete {full_path}")
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)  # if its a folder
            else:
                os.remove(full_path)  # if its a file
            refresh_left()
            refresh_right()
        except Exception as e:
            print("Failed")
            messagebox.showerror("Error", str(e))


def rename_selected():
    
    select_left = files_tree_left.selection()
    select_right = files_tree_right.selection()

    if select_left and select_right:
        if last_isleft == True:
            item = files_tree_left
            item_id = select_left[0] 
            path = list_left[0] 
        else:
            item = files_tree_right
            item_id = select_right[0]
            path = list_right[0]
    elif select_left:
        item = files_tree_left
        item_id = select_left[0] 
        path = list_left[0] 
    
    elif select_right:
        item = files_tree_right
        item_id = select_right[0]
        path = list_right[0]
    
    else:
        print("No item selected to rename")
        return

    values = item.item(item_id , "values") # the filetree alongside the contents
    filename = values[1] # the name
    full_path = os.path.join(path, filename) 
    new_name = simpledialog.askstring("New name", f"Please choose a new name for {filename}", parent = root)
    print(f"User has selected {new_name} to replace {filename}")
    if new_name is None: #incase its empty or we clicked No
        print("Aborted")
        return

    new_path = os.path.join(path, new_name.strip()) 

    if new_path == path :
        messagebox.showerror("Rename failed", "You must choose a new name which isn't made up of only blank spaces")
        print("Aborted")
        return

    try:
        os.rename(full_path, new_path)
        print(f"{new_path} has replaced {full_path}")
    except OSError as e:
        messagebox.showerror("Rename failed", f"Could not rename: \n{e}")
    
    refresh_left()
    refresh_right()

def create_folder():
    
    select_left = files_tree_left.selection()
    select_right = files_tree_right.selection()

    if select_left and select_right:
        if last_isleft == True:
            item = files_tree_left
            item_id = select_left[0] 
            path = list_left[0] 
        else:
            item = files_tree_right
            item_id = select_right[0]
            path = list_right[0]
    elif select_left:
        item = files_tree_left
        item_id = select_left[0] 
        path = list_left[0] 
    
    elif select_right:
        item = files_tree_right
        item_id = select_right[0]
        path = list_right[0]
    
    else: # SPECIAL CASE ONLY FOR FOLDER CREATION
        if list_left: # say we havent clicked anything. that means we want to see the active space and place it in there
            path = list_left[0]
        elif list_right:
            path = list_right[0]
        else:
            print("No path selected for folder creation")
            return
    
    if select_left or select_right:
        values = item.item(item_id,"values")
        filename = values[1]
        full_path = os.path.join(path,filename)
    else:
        full_path = path # this is incase we just use the special case, aka the entry only

    if os.path.isdir(full_path) == False :
        messagebox.showerror("Creation failed", "You cannot create a folder in a file")
        return
    
    if path is None:
        messagebox.showerror("Creation failed", "Please choose a location for your new folder")
        return

    new_folder = simpledialog.askstring("New folder", f"Please choose a new name for the folder in {full_path}", parent = root)

    if new_folder is None:
        return
    if new_folder.strip() is None:
        messagebox.showerror("Creation failed", "Please choose a valid name")
        return
    try:
        print(f"Success! Folder {new_folder} has been created in {full_path}")
        folder = os.path.join(full_path,new_folder)
        os.mkdir(folder)
        refresh_left()
        refresh_right()
    except FileExistsError:
        messagebox.showerror("Creation failed" , "Folder already exists!")
    except OSError:
        messagebox.showerror("Creation failed", "Could not create a new folder")

def create_key():
    key = Fernet.generate_key()
    with open('key.key',"wb") as f: #writes in binary the randomly created 32 byte key
        f.write(key)

def load_key():
    with open('key.key',"rb") as f:
        key = f.read() 
    return Fernet(key) #we convert it into a Fernet obj

def move_ff():
    selected_left = files_tree_left.selection()
    selected_right = files_tree_right.selection()
    
    source_dir = ""
    dest_dir = ""
    name_dir = ""
    
    # determining source and destination directories
    if selected_left and selected_right:
        if last_isleft == True:
            item = files_tree_left
            item_id = selected_left[0] 
            path = list_left[0] 
        else:
            item = files_tree_right
            item_id = selected_right[0]
            path = list_right[0]
    elif selected_left:
        item_id = selected_left[0]
        path = list_left[0]
        item = files_tree_left
        
        if not list_right:
            messagebox.showerror("Error", "No destination selected")
            return
        else: 
            dest_dir = list_right[0]
        
    elif selected_right:
        item_id = selected_right[0]
        path = list_right[0]
        item = files_tree_right
        if not list_left:
            messagebox.showerror("Error", "No destination selected")
            return
        else:
            dest_dir = list_left[0] 
            
    else:
        print("No item selected to move")
        return
    values = item.item(item_id, "values")
    name_dir = values[1] #name
    source_dir = os.path.join(path, name_dir)
    dest_dir = os.path.join(dest_dir, name_dir)
    
    try:
        shutil.move(source_dir, dest_dir)
        print (f"Moved {source_dir} to {dest_dir} with success")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to move: {e}")
        return
    
    refresh_left()
    refresh_right()
        
passw = [] # for Fernet, in case the program closes while a file is encrypted the user can simply press encrypt again and then decrypt, while generating a new password

def encrypt_path(path, fernet):
    if os.path.isfile(path):#if file
        with open(path, "rb") as f:
            data = f.read()
        with open(path, "wb") as f:
            f.write(fernet.encrypt(data))

    elif os.path.isdir(path):#if folder
        for root, dirs, files in os.walk(path):#we go through the 3 tuple returned by oswalk
            for name in files:
                encrypt_path(os.path.join(root, name), fernet)

def encrypt_content():
    passw.clear()

    select_left = files_tree_left.selection()
    select_right = files_tree_right.selection()

    if select_left and select_right:
        if last_isleft == True:
            item = files_tree_left
            item_id = select_left[0] 
            path = list_left[0] 
        else:
            item = files_tree_right
            item_id = select_right[0]
            path = list_right[0]
    elif select_left:
        item = files_tree_left
        item_id = select_left[0] 
        path = list_left[0] 
    
    elif select_right:
        item = files_tree_right
        item_id = select_right[0]
        path = list_right[0]
    else:
        return

    values = item.item(item_id, "values")
    filename = values[1]
    full_path = os.path.join(path, filename)

    password = simpledialog.askstring("Set password","Create a password : ", parent = root)
    if password is None:
        return

    passw.append(password)

    fernet = load_key()
    encrypt_path(full_path, fernet)

    messagebox.showinfo("Success", "Encryption complete")


def decrypt_path(path, fernet):
    if os.path.isfile(path):
        with open(path, "rb") as f:
            data = f.read()
        with open(path, "wb") as f:
            f.write(fernet.decrypt(data))

    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for name in files:
                decrypt_path(os.path.join(root, name), fernet)


def decrypt_content():
    select_left = files_tree_left.selection()
    select_right = files_tree_right.selection()

    if select_left and select_right:
        if last_isleft == True:
            item = files_tree_left
            item_id = select_left[0] # the id of the first item chosen
            path = list_left[0] # current path
        else:
            item = files_tree_right
            item_id = select_right[0]
            path = list_right[0]
    elif select_left:
        item = files_tree_left
        item_id = select_left[0] # the id of the first item chosen
        path = list_left[0] # current path
    
    elif select_right:
        item = files_tree_right
        item_id = select_right[0]
        path = list_right[0]
    else:
        print("No item selected to decrypt")
        return

    values = item.item(item_id, "values")
    filename = values[1]
    full_path = os.path.join(path, filename)

    password = simpledialog.askstring("Password","Enter your set password : ", parent = root)
    if password is None:
        return

    if not passw or password != passw[0]:
        messagebox.showerror("Error", "Wrong password")
        return

    fernet = load_key()

    try:
        decrypt_path(full_path, fernet)
    except Exception:
        messagebox.showerror("Error", "Decryption failed")
        return

    messagebox.showinfo("Success", "Decryption complete")

def enc_dec():#XOR logic
    global root
    select_left = files_tree_left.selection()
    select_right = files_tree_right.selection()

    if select_left and select_right:
        if last_isleft == True:
            item = files_tree_left
            item_id = select_left[0] 
            path = list_left[0] 
        else:
            item = files_tree_right
            item_id = select_right[0]
            path = list_right[0]
    elif select_left:
        item = files_tree_left
        item_id = select_left[0] 
        path = list_left[0] 
    
    elif select_right:
        item = files_tree_right
        item_id = select_right[0]
        path = list_right[0]
    else:
        print("No item selected to decrypt")
        return
    
    values = item.item(item_id, "values")
    filename = values[1]
    full_path = os.path.join(path, filename)
    
    password = simpledialog.askstring("Password","Enter your set password : ", parent = root)
    if password is None:
        return
    
    if os.path.isfile(full_path):
        with open(full_path, "rb") as f:
            data = f.read()
        key = password.encode("utf-8") # convert the password into a compatible key
        length = len(key)
        enc = bytes([b ^ key[i % length] for i, b in enumerate(data)]) # we take the XOR of each individual file byte with the password -> key byte (modulo is for looping logic)
        with open(full_path, "wb") as f:
            f.write(enc)
        
    elif os.path.isdir(full_path):
        for root, dirs, files in os.walk(path):
            for name in files:
                fol_path = os.path.join(root, name)
                with open(fol_path, "rb") as f:
                    data = f.read()
                key = password.encode("utf-8")
                length = len(key)
                enc = bytes([b ^ key[i % length] for i, b in enumerate(data)])
                with open(fol_path, "wb") as f:
                    f.write(enc)
    
                    
    messagebox.showinfo("Success", "Content modified")
# setting up the pop-up icon
def preview_content():
    select_left = files_tree_left.selection() # we are looking to find where we clicked
    select_right = files_tree_right.selection()

    if select_left and select_right:
        if last_isleft == True:
            item = files_tree_left
            item_id = select_left[0] # the id of the first item chosen
            path = list_left[0] # current path
        else:
            item = files_tree_right
            item_id = select_right[0]
            path = list_right[0]
    elif select_left:
        item = files_tree_left
        item_id = select_left[0] # the id of the first item chosen
        path = list_left[0] # current path

    elif select_right:
        item = files_tree_right
        item_id = select_right[0]
        path = list_right[0]

    else:
        print ("No item selected in order to preview")
        return

    values = item.item(item_id, "values")
    filename = values[1] # we need the name since values has on pos 0 the symbol/ logo
    full_path = os.path.join(path, filename)

    try: 

        with open(full_path, "rb") as f: #open in binary 
            raw_bytes = f.read(1000)  # read first 100 bytes

        try:
            # try to decode as text - we check if its a text file
            display_text = raw_bytes.decode('utf-8') 
        except:
           #if it is not a text file => raw bytes format
            display_text = str(raw_bytes)

        messagebox.showinfo(f"Preview: {filename}", display_text)

    except Exception as e:
        print("Failed to preview")
        messagebox.showerror("Error", f"Could not read file:\n{str(e)}")


if not os.path.exists("key.key"):
    create_key()
    print("Key file has been created. Use in case of forgotten password")

print("---------------")
print("| CONSOLE LOG |")
print("---------------")
print()
print("Initialising root")
root = tk.Tk()
root.title("File Manager")
root.geometry("800x600+550+200")
root.rowconfigure(0, weight=0)  # header row
root.rowconfigure(1, weight=1)  # main content row
root.columnconfigure(0, weight=1)
print("Root has been initialised")
# changing the style
print()
print("Configuring style")
style = ttk.Style(root)
DARK = "#a9a9a9"
style.configure("TFrame", background=DARK)  # TFrame is used to control ALL frames (gray)
style.configure("TLabel", background=DARK)  # TLabel is for all labels
style.configure("TButton", background=DARK)  # TButton for all buttons
print("Style has been configured")
print()
# header ( section dedicated to changing the HEADER )
print("Setting up the header")
header_frame = ttk.Frame(root)
header_frame.grid(row=0,  # occupies row 0 of our root
                  column=0,
                  sticky="ew"  # we want it to occupy the space given
                  )
header_label = ttk.Label(header_frame,
                         text="Total Commander",
                         font=('Arial', 10, 'bold'),
                         anchor=tk.CENTER  # centers the text
                         )
header_label.grid(row=0,
                  column=0,
                  pady=5,
                  sticky="ew"  # how it stretches IN the HEADER frame
                  )
header_frame.grid_columnconfigure(0, weight=1)
print("Header has been created successfully")
# mainframe ( section dedicated to STORING the CONTENT and SEARCH mechanic )
print()
print("Creating mainframe")
mainframe = ttk.Frame(root)
mainframe.grid(row=1,
               column=0,
               sticky="nsew",
               padx=0,
               pady=0
               )
mainframe.columnconfigure(0, weight=1)  # left
mainframe.columnconfigure(1, weight=0)  # middle ( used for FUNCTIONS )
mainframe.columnconfigure(2, weight=1)  # right
mainframe.rowconfigure(0, weight=1)  # only the first "search" row
print("Mainframe complete")
print()
print("Separating mainframe")
# leftframe
print()
print("Creating left panel")
left_panel = ttk.Frame(mainframe, borderwidth=1, relief=tk.SUNKEN)
left_panel.grid(row=0,
                column=0,
                sticky="nsew"
                )
left_panel.rowconfigure(0, weight=0)  # search row
left_panel.rowconfigure(1, weight=0)  # path row
left_panel.rowconfigure(2, weight=1)  # file list row
left_panel.columnconfigure(0, weight=0)
left_panel.columnconfigure(1, weight=1)
left_panel.columnconfigure(2, weight=0)

# left search frame
print("Creating search box")
search_label_left = ttk.Label(left_panel,
                              text="Search: ",
                              font=('Arial', 10, 'bold')

                              )
search_label_left.grid(row=0,
                       column=0,
                       sticky="w",  # so it goes to the LEFT since its the FIRST
                       padx=5
                       )
entry_search_left = ttk.Entry(left_panel)
entry_search_left.grid(row=0,
                       column=1,
                       sticky="ew",  # so it takes the CENTER
                       padx=5
                       )
entry_search_left.bind("<Return>", lambda e : load_directory_left())

search_button_left = ttk.Button(left_panel,
                                text="Search",
                                command=load_directory_left
                                )
search_button_left.grid(row=0,
                        column=2,
                        sticky="e",  # so it takes the RIGHT since its the LAST
                        padx=5
                        )

# left path frame
print("Creating dynamic path display")
path_label_left = ttk.Label(left_panel,
                            text="path: ",
                            font=('Arial', 10, 'bold')
                            )
path_label_left.grid(row=1,
                     column=0,
                     sticky="w",
                     )
path_entry_left = ttk.Entry(left_panel,
                            state='readonly'  # read only so the user cant edit it
                            )
path_entry_left.grid(row=1,
                     column=1,
                     sticky="ew",
                     columnspan=2
                     )

# LEFT FILES FRAME (row=2)
left_content_frame = ttk.Frame(left_panel)
left_content_frame.grid(row=2,
                        column=0,
                        columnspan=3,
                        sticky="nsew",
                        padx=2,
                        pady=2
                        )
left_content_frame.columnconfigure(0, weight=1)  # left file content list (occupies all the space)
left_content_frame.columnconfigure(1, weight=0)  # left scrollbar (occupies just the space it needs)
left_content_frame.rowconfigure(0, weight=1)  # single
columns = ("symbol", "name", "type", "size", "modified")
files_tree_left = ttk.Treeview(
    left_content_frame,
    columns=columns,
    show="headings",
    selectmode="extended"  # we will use this later for making an on click function
)
files_scroll_left = ttk.Scrollbar(left_content_frame,
                                  orient="vertical",
                                  command=files_tree_left.yview
                                  )
files_tree_left.configure(yscrollcommand=files_scroll_left.set)
files_tree_left.grid(row=0,
                     column=0,
                     sticky="nsew",
                     columnspan=2
                     )
files_scroll_left.grid(row=0,
                       column=1,
                       sticky="ns"
                       )
files_tree_left.heading("symbol", text="s")
files_tree_left.heading("name", text="Name")
files_tree_left.heading("type", text="Type")
files_tree_left.heading("size", text="Size")
files_tree_left.heading("modified", text="Last mod.")
files_tree_left.column("symbol",width=5, anchor="w")
files_tree_left.column("name", width=260, anchor="w")
files_tree_left.column("type", width=120, anchor="w")
files_tree_left.column("size", width=90, anchor="w")
files_tree_left.column("modified", width=140, anchor="w")

# double click event function ( opening a file / folder )
files_tree_left.bind("<Double-1>", click_directory_left)
files_tree_left.bind("<Button-1>", lambda e: set_last(True))

# MIDDLE PANEL/FUNCTIONS PANEL
print("Setting up separator column")
mid_panel = ttk.Frame(mainframe, width=100)
mid_panel.grid(row=0,
               column=1,
               sticky="ns"
               )
mid_panel_header = ttk.Label(mid_panel,
                             text="Functions",
                             font=('Arial', 12, 'bold')
                             )
mid_panel_header.grid(row=0,
                      column=0,
                      pady=10
                      )
new_folder_func_panel = ttk.Button(mid_panel,
                                   text="New Folder",
                                   command = create_folder
                                   )
new_folder_func_panel.grid(row=1,
                           column=0,
                           sticky="ew"
                           )
delete_func_panel = ttk.Button(mid_panel,
                               text="Delete",
                               command = delete_selected
                               )
delete_func_panel.grid(row=2,
                       column=0,
                       sticky="ew"
                       )
rename_func_panel = ttk.Button(mid_panel,
                               text="Rename",
                               command = rename_selected
                               )
rename_func_panel.grid(row=3,
                       column=0,
                       sticky="ew"
                       )
encrypt_func_panel = ttk.Button(mid_panel,
                                text="Encrypt",
                                command = encrypt_content)
encrypt_func_panel.grid(row=4,
                        column=0,
                        sticky="ew"
                        )
decrypt_func_panel = ttk.Button(mid_panel,
                                text="Decrypt",
                                command = decrypt_content
                                )
decrypt_func_panel.grid(row=5,
                        column=0,
                        sticky="ew"
                        )
move_func_panel = ttk.Button(mid_panel,
                             text="Move",
                             command = move_ff
                             )
move_func_panel.grid(row=6,
                     column=0,
                     sticky="ew"
                     )
enc_func_panel = ttk.Button(mid_panel,
                            text="XOR Enc/Dec",
                            command = enc_dec) 
enc_func_panel.grid(row=7,
                    column=0,
                    sticky="ew"
                    )
preview_func_panel = ttk.Button(mid_panel,
                             text="Preview",
                             command = preview_content
                             )
preview_func_panel.grid(row=8,
                     column=0,
                     sticky="ew"
                     )

print("Separation complete")
print("Functionality provided")
# RIGHT PANEL
right_panel = ttk.Frame(mainframe, relief=tk.SUNKEN, borderwidth=1)
right_panel.grid(row=0,
                 column=2,
                 sticky="nsew"
                 )
right_panel.columnconfigure(0, weight=0)
right_panel.columnconfigure(1, weight=1)
right_panel.columnconfigure(2, weight=0)
right_panel.rowconfigure(0, weight=0)  # search row
right_panel.rowconfigure(1, weight=0)  # path row
right_panel.rowconfigure(2, weight=1)  # file list row

# RIGHT SEARCH FRAME (row=0)
print()
print("Creating right panel")
search_label_right = ttk.Label(right_panel,
                               text="Search: ",
                               font=('Arial', 10, 'bold')
                               )
search_label_right.grid(row=0,
                        column=0,
                        sticky="w",  # so it goes to the LEFT since its the FIRST
                        padx=5
                        )
entry_search_right = ttk.Entry(right_panel)
entry_search_right.grid(row=0,
                        column=1,
                        sticky="ew",  # so it takes the CENTER
                        padx=5
                        )
entry_search_right.bind("<Return>", lambda e : load_directory_right())
# RIGHT PATH FRAME (row=1)
print("Creating search box")
path_label_right = ttk.Label(right_panel,
                             text="path: ",
                             font=('Arial', 10, 'bold')
                             )
path_label_right.grid(row=1,
                      column=0,
                      sticky="w",  # so it goes to the LEFT since its the FIRST
                      )
path_entry_right = ttk.Entry(right_panel, state='readonly')  # read only so the user cant edit it
path_entry_right.grid(row=1,
                      column=1,
                      sticky="ew",  # so it takes the CENTER,
                      columnspan=2
                      )

# RIGHT FILES FRAME (row=2)
print("Creating dynamic path display")
right_content_frame = ttk.Frame(right_panel)
right_content_frame.grid(row=2,
                         column=0,
                         columnspan=3,
                         sticky="nsew",
                         padx=2,
                         pady=2
                         )
right_content_frame.columnconfigure(0, weight=1)  # right file content list (occupies all the space)
right_content_frame.columnconfigure(1, weight=0)  # right scrollbar (occupies just the space it needs)
right_content_frame.rowconfigure(0, weight=1)  # single
columns = ("symbol","name", "type", "size", "modified")
files_tree_right = ttk.Treeview(
    right_content_frame,
    columns=columns,
    show="headings",
    selectmode="extended"  # we will use this later for making an on click function
)
files_scroll_right = ttk.Scrollbar(right_content_frame,
                                   orient="vertical",
                                   command=files_tree_right.yview
                                   )
files_tree_right.configure(yscrollcommand=files_scroll_right.set)
files_tree_right.grid(row=0,
                      column=0,
                      sticky="nsew",
                      columnspan=2
                      )
files_scroll_right.grid(row=0,
                        column=1,
                        sticky="ns"
                        )
files_tree_right.heading("symbol", text="s")
files_tree_right.heading("name", text="Name")
files_tree_right.heading("type", text="Type")
files_tree_right.heading("size", text="Size")
files_tree_right.heading("modified", text="Last mod.")
files_tree_right.column("symbol",width=5, anchor="w")
files_tree_right.column("name", width=260, anchor="w")
files_tree_right.column("type", width=120, anchor="w")
files_tree_right.column("size", width=90, anchor="w")
files_tree_right.column("modified", width=140, anchor="w")

# RIGHT SEARCH BUTTON
search_button_right = ttk.Button(right_panel,
                                 text="Search",
                                 command=load_directory_right
                                 )
search_button_right.grid(row=0,
                         column=2,
                         sticky="ew",  # so it takes the RIGHT since its the LAST
                         padx=5
                         )

# double click event function ( opening a file / folder )
files_tree_right.bind("<Double-1>", click_directory_right)
files_tree_right.bind("<Button-1>", lambda e: set_last(False))


print()
print("LOADING COMPLETE !")
root.mainloop()
