import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from admin import display_admin
from user import display_user
from utils import clear_window

def add_hover_effect(button):
    def on_enter(e): button.configure(style="Hover.TButton")
    def on_leave(e): button.configure(style="TButton")
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

def show_main_page(root):
    clear_window(root)
    root.title("Task Manager")
    root.configure(bg="#e6f0f5")  # Soft pastel blue

    style = ttk.Style()
    style.configure("TButton", font=("Verdana", 13, "bold"), padding=10)
    style.configure("Hover.TButton", font=("Verdana", 13, "bold"), padding=10, background="#d0e0ea")

    container = ttk.Frame(root)
    container.place(relx=0.5, rely=0.5, anchor="center")

    # Title Label
    title = ttk.Label(
        root,
        text="Welcome to TaskFlow!",
        font=("Verdana", 30, "bold"),
        background="#e6f0f5"
    )
    title.place(relx=0.5, rely=0.25, anchor="center")

    # Wiggle animation using relx offset
    def wiggle_label(label, relx=0.5, direction=1):
        offset = 0.003 * direction  # Smaller wiggle (in relative coords)
        new_relx = relx + offset
        label.place(relx=new_relx, rely=0.25, anchor="center")
        label.after(200, lambda: wiggle_label(label, relx, -direction))  

    # Start animation
    wiggle_label(title)

    # Buttons
    login_btn = ttk.Button(container, text="Login", width=30, command=lambda: show_login_page(root))
    login_btn.pack(pady=10)
    add_hover_effect(login_btn)

    signup_btn = ttk.Button(container, text="Sign Up", width=30, command=lambda: show_signup_page(root))
    signup_btn.pack(pady=10)
    add_hover_effect(signup_btn)

def show_signup_page(root):
    clear_window(root)
    root.title("Sign Up Page")
    root.configure(bg="#e6f0f5")

    style = ttk.Style()
    style.configure("TButton", font=("Verdana", 13, "bold"), padding=10)
    style.configure("Hover.TButton", font=("Verdana", 13, "bold"), padding=10, background="#d0e0ea")

    container = ttk.Frame(root)
    container.place(relx=0.5, rely=0.5, anchor="center")

    ttk.Label(container, text="Create Your Account", font=("Verdana", 20, "bold"), background="#e6f0f5").pack(pady=(0, 10))

    frame = ttk.Frame(container)
    frame.pack()

    # Username
    ttk.Label(frame, text="Username", font=("Verdana", 12, "bold"), background="#e6f0f5").pack(pady=(0, 5))
    username_entry = ttk.Entry(frame)
    username_entry.pack()

    # Password
    ttk.Label(frame, text="Password", font=("Verdana", 12, "bold"), background="#e6f0f5").pack(pady=(10, 5))
    password_entry = ttk.Entry(frame, show="*")
    password_entry.pack()

    # Role Selection (use tk.Radiobutton for background support)
    ttk.Label(frame, text="Select Your Role", font=("Verdana", 12, "bold"), background="#e6f0f5").pack(pady=(10, 5))
    role_var = tk.StringVar(value="User")  # Default to User

    tk.Radiobutton(frame, text="Admin", variable=role_var, value="Admin", bg="#e6f0f5", font=("Verdana", 11, "bold")).pack(pady=(10, 5))
    tk.Radiobutton(frame, text="User", variable=role_var, value="User", bg="#e6f0f5", font=("Verdana", 11, "bold")).pack(pady=(10, 5))

    def register_user():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        role = role_var.get()

        if username and password:
            with sqlite3.connect('userData.db') as conn:
                c = conn.cursor()
                c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, role TEXT)")
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
                conn.commit()

                # Debug: print all users
                c.execute("SELECT username, role FROM users")
                print("Users in DB:", c.fetchall())

            messagebox.showinfo("Success", f"{role} account created for {username}!")
            show_login_page(root)
        else:
            messagebox.showerror("Error", "All fields are required!")

    ttk.Button(frame, text="Register", command=register_user).pack(pady=(10, 5))

    # Back to login
    ttk.Button(frame, text="⬅️ Back to Login", command=lambda: show_login_page(root)).pack()

def show_login_page(root):
    clear_window(root)
    root.title("Login Page")
    root.configure(bg="#e6f0f5")

    style = ttk.Style()
    style.configure("TButton", font=("Verdana", 13, "bold"), padding=10)
    style.configure("Hover.TButton", font=("Verdana", 13, "bold"), padding=10, background="#d0e0ea")

    container = ttk.Frame(root)
    container.place(relx=0.5, rely=0.5, anchor="center")

    ttk.Label(container, text="Login to TaskFlow", font=("Verdana", 20, "bold"), background="#e6f0f5").pack(pady=(0, 10))

    frame = ttk.Frame(container)
    frame.pack()

    ttk.Label(frame, text="Username", font=("Verdana", 12, "bold"), background="#e6f0f5").pack(pady=(0, 5))
    username_entry = ttk.Entry(frame)
    username_entry.pack()

    ttk.Label(frame, text="Password", font=("Verdana", 12, "bold"), background="#e6f0f5").pack(pady=(10, 5))
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

    ttk.Button(frame, text="Login", command=validate_user).pack(pady=(10, 5))
    ttk.Button(frame, text="Back", command=lambda: show_main_page(root)).pack()
