import tkinter as tk
from auth import show_main_page
from utils import clear_window  # Just in case you use it later

def clear_window(root):
    for widget in root.winfo_children():
        widget.destroy()

root = tk.Tk()
root.title("TaskFlow")
root.geometry("800x600")  # Bigger for notebook aesthetic

show_main_page(root)

root.mainloop()

