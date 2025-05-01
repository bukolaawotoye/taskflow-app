# main.py (Updated with ThemedTk and ttk)

from tkinter import ttk
from ttkthemes import ThemedTk
from auth import show_login_page, show_signup_page, show_main_page
from utils import clear_window

def clear_window(root):
    for widget in root.winfo_children():
        widget.destroy()

# Use ThemedTk for a modern look
root = ThemedTk(theme="breeze")  # You can try "breeze", "plastik", "equilux", etc.
root.geometry("600x600")

# Load the main menu (login/signup)
show_main_page(root)

root.mainloop()
