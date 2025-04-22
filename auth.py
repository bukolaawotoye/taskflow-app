import tkinter
import sqlite3
from admin import display_admin
from user import display_user
from utils import clear_window

def show_main_page(root):
    clear_window(root)
    root.title("Task Manager")
    tkinter.Button(root, text="Login", command=lambda: show_login_page(root)).pack()
    tkinter.Button(root, text="Signup", command=lambda: show_signup_page(root)).pack()

def show_signup_page(root):
    clear_window(root)
    root.title("Sign Up Page")

    tkinter.Label(root, text="Username").pack()
    username_entry = tkinter.Entry(root)
    username_entry.pack()

    tkinter.Label(root, text="Password").pack()
    password_entry = tkinter.Entry(root, show="*")
    password_entry.pack()

    tkinter.Label(root, text="Role").pack()
    role_var = tkinter.StringVar(value="Admin")
    tkinter.Radiobutton(root, text="Assigning Task", variable=role_var, value="Admin").pack()
    tkinter.Radiobutton(root, text="Being Assigned Task", variable=role_var, value="User").pack()

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
            tkinter.Label(root, text="User registered successfully!", fg="green").pack()
            show_login_page(root)
        else:
            tkinter.Label(root, text="All fields are required!", fg="red").pack()

    tkinter.Button(root, text="Register", command=register_user).pack()
    tkinter.Button(root, text="Back", command=lambda: show_main_page(root)).pack()

def show_login_page(root):
    clear_window(root)
    root.title("Login Page")

    tkinter.Label(root, text="Username").pack()
    username_entry = tkinter.Entry(root)
    username_entry.pack()

    tkinter.Label(root, text="Password").pack()
    password_entry = tkinter.Entry(root, show="*")
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
                display_admin(root, username)
            else:
                display_user(root, username)
        else:
            tkinter.Label(root, text="Invalid credentials", fg="red").pack()

    tkinter.Button(root, text="Login", command=validate_user).pack()
    tkinter.Button(root, text="Back", command=lambda: show_main_page(root)).pack()