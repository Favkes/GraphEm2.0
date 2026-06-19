import tkinter as tk
from tkinter import filedialog, messagebox




class Graph:
    nodes: list
    data_loaded: str

    def __init__(self):
        data_loaded = ""

    def build(self):
        data = self.data_loaded

    def load_data(self, data: str):
        self.data_loaded = data


graph = Graph()

root = tk.Tk()
root.title("GraphEm 2.0")
root.geometry("500x500")


frame_input_data = tk.Frame(root)
frame_input_data.grid()

lbl = tk.Label(frame_input_data, text="Lalala! :]")
lbl.grid()

data_field = tk.Text(root)
data_field.grid()


# Menu bar -----------------------------------------------------
menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)

def func_import_data():
    path = filedialog.askopenfilename()
    if path:
        print("Importing from file:", path)
        with open(path, "r") as f:
            data = f.read()
            data_field.delete(1.0, tk.END)
            data_field.insert(tk.END, data)
        return
    print("No file chosen")
file_menu.add_command(label="Import data", command=func_import_data)

def func_save_data():
    path = filedialog.asksaveasfilename()
    if path:
        print("Saving to file:", path)
        with open(path, "w") as f:
            data = data_field.get(1.0, tk.END)
            f.write(data)
        return
    print("No file chosen")
    messagebox.showinfo("Save data", "Tu będzie zapisywanie danych do pliku")
file_menu.add_command(label="Save data", command=func_save_data)

menubar.add_cascade(label="File", menu=file_menu)
root.config(menu=menubar)


# Data management buttons -----------------------------------------------------
frame_data_management = tk.Frame(root)
frame_data_management.grid(column=1, row=1)
def func_load_data_to_program():
    # messagebox.showinfo("Info", "This will load the data into the program")
    choice = messagebox.askyesno("Question", "Would you like to load this data into the graph?")
    if choice:
        graph.load_data(data_field.get(1.0, tk.END))
    else:
        print("Loading to program cancelled")
button_load_data_to_program = tk.Button(frame_data_management, text="Load data to program", command=func_load_data_to_program)
button_load_data_to_program.grid()

root.mainloop()
