import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from admin import display_admin
from user import display_user
from utils import clear_window

# Add hover effect for motion
def add_hover_effect(button):
    def on_enter(e): button.configure(style="Hover.TButton")
    def on_leave(e): button.configure(style="TButton")
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

def show_main_page(root):
    clear_window(root)
    root.title("Task Manager")
    root.configure(bg="#d9eaf7")

    style = ttk.Style()
    style.configure("Card.TFrame", background="#fefefe", relief="flat", borderwidth=0, padding=40)
    style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10)
    style.configure("Hover.TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#d0ebff")
    style.map("TButton", background=[("active", "#bbdefb")])
    style.configure("TLabel", font=("Segoe UI", 11))

    container = ttk.Frame(root, style="Card.TFrame")
    container.place(relx=0.5, rely=0.5, anchor="center")

    ttk.Label(
        root,
        text="Welcome to TaskFlow!",
        font=("Segoe UI", 28, "bold"),
        background="#d9eaf7",
        foreground="#2c3e50"
    ).place(relx=0.5, rely=0.25, anchor="center")

    login_btn = ttk.Button(container, text="Login", width=30, command=lambda: show_login_page(root))
    login_btn.pack(pady=10)
    add_hover_effect(login_btn)

    signup_btn = ttk.Button(container, text="Sign Up", width=30, command=lambda: show_signup_page(root))
    signup_btn.pack(pady=10)
    add_hover_effect(signup_btn)

def show_signup_page(root):
    clear_window(root)
    root.title("Sign Up Page")
    root.configure(bg="#d9eaf7")

    style = ttk.Style()
    style.configure("Card.TFrame", background="#ffffff", padding=40, relief="flat")
    style.configure("TLabel", font=("Segoe UI", 11))
    style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10)
    style.configure("Hover.TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#d0ebff")

    container = ttk.Frame(root)
    container.place(relx=0.5, rely=0.5, anchor="center")

    ttk.Label(container, text="Create Your Account", font=("Segoe UI", 22, "bold"), background="#d9eaf7").pack(pady=(0, 10))

    frame = ttk.Frame(container, style="Card.TFrame")
    frame.pack()

    ttk.Label(frame, text="Username", font=("Segoe UI", 12, "bold")).pack(pady=(0, 5))
    username_entry = ttk.Entry(frame)
    username_entry.pack()

    ttk.Label(frame, text="Password", font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))
    password_entry = ttk.Entry(frame, show="*")
    password_entry.pack()

    ttk.Label(frame, text="Role", font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))
    role_var = tk.StringVar(value="Admin")
    ttk.Radiobutton(frame, text="Assigning Task", variable=role_var, value="Admin").pack(anchor="w")
    ttk.Radiobutton(frame, text="Being Assigned Task", variable=role_var, value="User").pack(anchor="w")

    def register_user():
        username = username_entry.get()
        password = password_entry.get()
        role = role_var.get()

        if username and password:
            with sqlite3.connect('userData.db') as conn:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, role TEXT)''')
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
                conn.commit()
            messagebox.showinfo("Success", "User registered successfully!")
            show_login_page(root)
        else:
            messagebox.showerror("Missing Fields", "All fields are required!")

    register_btn = ttk.Button(frame, text="Register", command=register_user)
    register_btn.pack(pady=(10, 5))
    add_hover_effect(register_btn)

    back_btn = ttk.Button(frame, text="Back", command=lambda: show_main_page(root))
    back_btn.pack()
    add_hover_effect(back_btn)

def show_login_page(root):
    clear_window(root)
    root.title("Login Page")
    root.configure(bg="#d9eaf7")

    style = ttk.Style()
    style.configure("Card.TFrame", background="#ffffff", padding=40, relief="flat")
    style.configure("TLabel", font=("Segoe UI", 11))
    style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10)
    style.configure("Hover.TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#d0ebff")

    container = ttk.Frame(root)
    container.place(relx=0.5, rely=0.5, anchor="center")

    ttk.Label(container, text="Login to Your Account", font=("Segoe UI", 22, "bold"), background="#d9eaf7").pack(pady=(0, 10))

    frame = ttk.Frame(container, style="Card.TFrame")
    frame.pack()

    ttk.Label(frame, text="Username", font=("Segoe UI", 12, "bold")).pack(pady=(0, 5))
    username_entry = ttk.Entry(frame)
    username_entry.pack()

    ttk.Label(frame, text="Password", font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))
    password_entry = ttk.Entry(frame, show="*")
    password_entry.pack()

    def validate_user():
        username = username_entry.get()
        password = password_entry.get()

        with sqlite3.connect('userData.db') as conn:
            c = conn.cursor()
            c.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
            result = c.fetchone()

        if result:
            role = result[0]
            if role == "Admin":
                display_admin(root, username, show_main_page)
            else:
                display_user(root, username, show_main_page)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    login_btn = ttk.Button(frame, text="Login", command=validate_user)
    login_btn.pack(pady=(10, 5))
    add_hover_effect(login_btn)

    back_btn = ttk.Button(frame, text="Back", command=lambda: show_main_page(root))
    back_btn.pack()
    add_hover_effect(back_btn)