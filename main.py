import tkinter
import sqlite3

# Helper function to clear window
def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

# --- AUTH PAGES ---
def show_signup_page():
    clear_window()
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
            show_login_page()
        else:
            tkinter.Label(root, text="All fields are required!", fg="red").pack()

    tkinter.Button(root, text="Register", command=register_user).pack()
    tkinter.Button(root, text="Back", command=show_main_page).pack()

def show_login_page():
    clear_window()
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
                display_admin(username)
            else:
                display_user(username)
        else:
            tkinter.Label(root, text="Invalid credentials", fg="red").pack()

    tkinter.Button(root, text="Login", command=validate_user).pack()
    tkinter.Button(root, text="Back", command=show_main_page).pack()

def show_main_page():
    clear_window()
    root.title("Task Manager")
    tkinter.Button(root, text="Login", command=show_login_page).pack()
    tkinter.Button(root, text="Signup", command=show_signup_page).pack()

# --- ADMIN DASHBOARD ---
def display_admin(name):
    clear_window()
    root.title(f"Welcome Admin: {name}")
    tkinter.Button(root, text="Create Task", command=lambda: create_task(name)).pack()
    tkinter.Button(root, text="Delete Task", command=lambda: delete_task(name)).pack()
    tkinter.Button(root, text="Add users to a task", command=lambda: add_users_to_task(name)).pack()
    tkinter.Button(root, text="View All Tasks", command=lambda: view_all_tasks(name)).pack()

def create_task(name):
    clear_window()
    root.title("Create Task")

    tkinter.Label(root, text="Task Name").pack()
    task_name_entry = tkinter.Entry(root)
    task_name_entry.pack()

    tkinter.Label(root, text="Task Description").pack()
    task_description_entry = tkinter.Entry(root)
    task_description_entry.pack()

    def save_task():
        task_name = task_name_entry.get()
        task_description = task_description_entry.get()
        if task_name and task_description:
            with sqlite3.connect('tasks.db') as conn:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS tasks (task_id INTEGER PRIMARY KEY AUTOINCREMENT, task_name TEXT, task_description TEXT)''')
                c.execute("INSERT INTO tasks (task_name, task_description) VALUES (?, ?)", (task_name, task_description))
                conn.commit()
            tkinter.Label(root, text="Task created successfully!", fg="green").pack()
        else:
            tkinter.Label(root, text="All fields are required!", fg="red").pack()

    tkinter.Button(root, text="Save", command=save_task).pack()
    tkinter.Button(root, text="Back", command=lambda: display_admin(name)).pack()

def delete_task(name):
    clear_window()
    root.title("Delete Task")

    tkinter.Label(root, text="Enter Task ID to Delete").pack()
    task_id_entry = tkinter.Entry(root)
    task_id_entry.pack()

    def perform_delete():
        task_id = task_id_entry.get()
        if task_id:
            with sqlite3.connect('tasks.db') as conn:
                c = conn.cursor()
                c.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
                c.execute("DELETE FROM task_assignments WHERE task_id = ?", (task_id,))
                conn.commit()
            tkinter.Label(root, text="Task deleted!", fg="green").pack()
        else:
            tkinter.Label(root, text="Task ID required", fg="red").pack()

    tkinter.Button(root, text="Delete", command=perform_delete).pack()
    tkinter.Button(root, text="Back", command=lambda: display_admin(name)).pack()

def add_users_to_task(name):
    clear_window()
    root.title("Assign Users to Task")

    with sqlite3.connect('userData.db') as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE role = 'User'")
        users = c.fetchall()

    tkinter.Label(root, text="Task ID").pack()
    task_id_entry = tkinter.Entry(root)
    task_id_entry.pack()

    tkinter.Label(root, text="Select Users").pack()
    user_vars = {}
    for user in users:
        var = tkinter.BooleanVar()
        user_vars[user[0]] = var
        tkinter.Checkbutton(root, text=user[0], variable=var).pack()

    def assign_users():
        task_id = task_id_entry.get()
        selected_users = [u for u, var in user_vars.items() if var.get()]
        if task_id and selected_users:
            with sqlite3.connect('tasks.db') as conn:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS task_assignments (task_id INTEGER, username TEXT)''')
                c.execute("DELETE FROM task_assignments WHERE task_id = ?", (task_id,))
                for user in selected_users:
                    c.execute("INSERT INTO task_assignments (task_id, username) VALUES (?, ?)", (task_id, user))
                conn.commit()
            tkinter.Label(root, text="Users assigned successfully!", fg="green").pack()
        else:
            tkinter.Label(root, text="Task ID and at least one user required", fg="red").pack()

    tkinter.Button(root, text="Assign", command=assign_users).pack()
    tkinter.Button(root, text="Back", command=lambda: display_admin(name)).pack()

def view_all_tasks(admin_name):
    clear_window()
    root.title("All Tasks Overview")

    table_frame = tkinter.Frame(root)
    table_frame.pack(pady=10)

    headers = ["Task Name", "Status", "Assigned To"]
    for i, h in enumerate(headers):
        tkinter.Label(table_frame, text=h, borderwidth=2, relief="groove", width=30, bg="#cce6ff", font=("Arial", 10, "bold")).grid(row=0, column=i)

    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS tasks (task_id INTEGER PRIMARY KEY AUTOINCREMENT, task_name TEXT, task_description TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS task_assignments (task_id INTEGER, username TEXT)")
        c.execute("SELECT * FROM tasks")
        tasks = c.fetchall()

        for row_idx, task in enumerate(tasks, start=1):
            task_id, task_name, _ = task
            c.execute("SELECT username FROM task_assignments WHERE task_id = ?", (task_id,))
            assignees = c.fetchall()
            assignee_list = ', '.join([a[0] for a in assignees]) if assignees else 'No one assigned'
            status = "Not Started" if not assignees else "In Progress"

            tkinter.Label(table_frame, text=task_name, borderwidth=1, relief="solid", width=30).grid(row=row_idx, column=0)
            tkinter.Label(table_frame, text=status, borderwidth=1, relief="solid", width=30).grid(row=row_idx, column=1)
            tkinter.Label(table_frame, text=assignee_list, borderwidth=1, relief="solid", width=30).grid(row=row_idx, column=2)

    tkinter.Button(root, text="Back", command=lambda: display_admin(admin_name)).pack(pady=10)

# --- USER VIEW ---
def display_user(name):
    clear_window()
    root.title(f"Welcome {name}")

    tkinter.Label(root, text="Your Assigned Tasks").pack()
    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS task_assignments (task_id INTEGER, username TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS tasks (task_id INTEGER PRIMARY KEY AUTOINCREMENT, task_name TEXT, task_description TEXT)''')
        c.execute("SELECT task_id FROM task_assignments WHERE username = ?", (name,))
        task_ids = c.fetchall()
        for tid in task_ids:
            c.execute("SELECT task_name, task_description FROM tasks WHERE task_id = ?", (tid[0],))
            task = c.fetchone()
            if task:
                tkinter.Label(root, text=f"{task[0]}: {task[1]}").pack()
    tkinter.Button(root, text="Logout", command=show_main_page).pack()

# --- MAIN TKINTER WINDOW ---
root = tkinter.Tk()
root.geometry("600x600")
show_main_page()
root.mainloop()
