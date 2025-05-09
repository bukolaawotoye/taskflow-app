import tkinter as tk
from tkinter import ttk
import sqlite3
from functools import partial
from utils import clear_window

def display_admin(root, name, show_main_page_callback):
    clear_window(root)
    root.title(f"Welcome Admin: {name}")
    root.configure(bg="#e6f0f5")
    style = ttk.Style()
    style.configure("TButton", font=("Verdana", 12, "bold"), padding=10)

    admin_header = ttk.Label(
        root,
        text=f"Welcome, Admin: {name.title()}",
        font=("Verdana", 26, "bold"),
        background="#e6f0f5"
    )
    admin_header.place(relx=0.5, rely=0.15, anchor="center")

    # Button container
    container = ttk.Frame(root)
    container.place(relx=0.5, rely=0.5, anchor="center")

    ttk.Button(container, text="Create Task", width=30, command=lambda: create_task(root, name, show_main_page_callback)).pack(pady=5)
    ttk.Button(container, text="Delete Task", width=30, command=lambda: delete_task(root, name, show_main_page_callback)).pack(pady=5)
    ttk.Button(container, text="View All Tasks", width=30, command=lambda: view_all_tasks(root, name, show_main_page_callback)).pack(pady=5)
    ttk.Button(container, text="Logout", width=30, command=lambda: show_main_page_callback(root)).pack(pady=10)

def create_task(root, name, show_main_page_callback):
    clear_window(root)
    root.title("Create Task")
    root.configure(bg="#e6f0f5")

    style = ttk.Style()
    style.configure("TButton", font=("Verdana", 12, "bold"), padding=10)

    container = ttk.Frame(root)
    container.place(relx=0.5, rely=0.5, anchor="center")

    # Header
    ttk.Label(root, text="Create New Task", font=("Verdana", 20, "bold"), background="#e6f0f5").place(relx=0.5, rely=0.1, anchor="center")

    # Task Name
    ttk.Label(container, text="Task Name", font=("Verdana", 12, "bold"), background="#e6f0f5").pack()
    task_name_entry = ttk.Entry(container, width=40)
    task_name_entry.pack()

    # Task Description
    ttk.Label(container, text="Task Description", font=("Verdana", 12, "bold"), background="#e6f0f5").pack(pady=(10, 0))
    task_description_entry = ttk.Entry(container, width=40)
    task_description_entry.pack()

    # Due Date
    ttk.Label(container, text="Due Date (YYYY-MM-DD)", font=("Verdana", 12, "bold"), background="#e6f0f5").pack(pady=(10, 0))
    due_date_entry = ttk.Entry(container, width=40)
    due_date_entry.pack()

    # Fetch all users to assign
    with sqlite3.connect('userData.db') as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE role = 'User'")
        users = c.fetchall()

    ttk.Label(container, text="Assign to Users:", font=("Verdana", 12, "bold"), background="#e6f0f5").pack(pady=(15, 5))
    user_vars = {}

    for user in users:
        var = tk.BooleanVar()
        user_vars[user[0]] = var
        ttk.Checkbutton(container, text=user[0].title(), variable=var).pack(anchor="w")

    # Save task
    def save_task():
        task_name = task_name_entry.get().strip()
        task_description = task_description_entry.get().strip()
        due_date = due_date_entry.get().strip()
        selected_users = [u for u, var in user_vars.items() if var.get()]

        if task_name and task_description and due_date and selected_users:
            with sqlite3.connect('tasks.db') as conn:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    task_name TEXT, 
                    task_description TEXT, 
                    due_date DATE
                )''')
                c.execute('''CREATE TABLE IF NOT EXISTS task_assignments (
                    task_id INTEGER, 
                    username TEXT, 
                    status TEXT DEFAULT 'Incomplete'
                )''')
                c.execute("INSERT INTO tasks (task_name, task_description, due_date) VALUES (?, ?, ?)", 
                          (task_name, task_description, due_date))
                task_id = c.lastrowid
                for user in selected_users:
                    c.execute("INSERT INTO task_assignments (task_id, username) VALUES (?, ?)", 
                              (task_id, user))
                conn.commit()

            ttk.Label(container, text="✅ Task created and assigned successfully!", foreground="green").pack(pady=10)
        else:
            ttk.Label(container, text="⚠️ All fields and at least one user are required.", foreground="red").pack(pady=10)

    ttk.Button(container, text="Save Task", command=save_task).pack(pady=10)
    ttk.Button(container, text="⬅️ Back", command=lambda: display_admin(root, name, show_main_page_callback)).pack()


def truncate_text(text, max_length=20):
    """Truncate long text with '...' for table display."""
    return text if len(text) <= max_length else text[:max_length] + "..."

def view_all_tasks(root, name, show_main_page_callback):
    clear_window(root)
    root.title("All Tasks")
    root.configure(bg="#e6f0f5")

    style = ttk.Style()
    style.configure("TButton", font=("Verdana", 12, "bold"), padding=10)

    main_frame = ttk.Frame(root)
    main_frame.place(relx=0.5, rely=0.3, anchor="n")

    # Header
    ttk.Label(
        main_frame,
        text="All Tasks Overview",
        font=("Verdana", 22, "bold"),
    ).pack(pady=(0, 10))

    # Container for table
    table_container = ttk.Frame(main_frame)
    table_container.pack(pady=10)

    headers = ["Task Name", "Description", "Status", "Assigned To", "Due Date"]
    for i, h in enumerate(headers):
        ttk.Label(
            table_container,
            text=h,
            borderwidth=2,
            relief="ridge",
            width=20,
            anchor="center",
            background="#cce6ff",
            font=("Verdana", 10, "bold")
        ).grid(row=0, column=i)

    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("SELECT task_id, task_name, task_description, due_date FROM tasks")
        tasks = c.fetchall()

        for row_idx, task in enumerate(tasks, start=1):
            task_id, task_name, task_description, due_date = task

            c.execute("SELECT username FROM task_assignments WHERE task_id = ?", (task_id,))
            assignees = ', '.join([a[0].title() for a in c.fetchall()])

            c.execute("SELECT status FROM task_assignments WHERE task_id = ?", (task_id,))
            status_rows = c.fetchall()

            if not status_rows:
                status = "Not Started"
            elif any(row[0] == "Completed" for row in status_rows):
                status = "Completed"
            else:
                status = "In Progress"

            status_color = {
                "Completed": "#c7f2c4",
                "In Progress": "#fff4c2",
                "Not Started": "#fbcaca"
            }

            clickable_label = ttk.Label(
                table_container,
                text=task_name,
                foreground="blue",
                cursor="hand2",
                background="white",
                borderwidth=1,
                relief="solid",
                width=20,
                font=("Verdana", 10)
            )
            clickable_label.grid(row=row_idx, column=0)
            clickable_label.bind("<Button-1>", lambda e, tid=task_id: open_task_card(root, tid))

            ttk.Label(table_container, text=task_description, background="white", borderwidth=1, relief="solid", width=20, font=("Verdana", 10)).grid(row=row_idx, column=1)
            ttk.Label(table_container, text=status, background=status_color[status], borderwidth=1, relief="solid", width=20, font=("Verdana", 10)).grid(row=row_idx, column=2)
            ttk.Label(table_container, text=assignees, background="white", borderwidth=1, relief="solid", width=20, font=("Verdana", 10)).grid(row=row_idx, column=3)
            ttk.Label(table_container, text=due_date, background="white", borderwidth=1, relief="solid", width=20, font=("Verdana", 10)).grid(row=row_idx, column=4)

    ttk.Frame(root, height=30, style="TFrame").pack()  # spacer
    ttk.Button(root, text="⬅️ Back", command=lambda: display_admin(root, name, show_main_page_callback)).pack(pady=(20, 30), side="bottom")

def open_task_card(root, task_id):
    """Opens a detailed view of the selected task."""
    detail_win = tk.Toplevel(root)
    detail_win.title("Task Details")
    detail_win.configure(bg="#e6f0f5")
    detail_win.geometry("450x400")

    style = ttk.Style()
    style.configure("TButton", font=("Verdana", 12, "bold"), padding=10)

    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("SELECT task_name, task_description, due_date FROM tasks WHERE task_id = ?", (task_id,))
        task = c.fetchone()

    ttk.Label(detail_win, text="Task Details", font=("Verdana", 20, "bold"), background="#e6f0f5").pack(pady=(20, 10))

    info_frame = ttk.Frame(detail_win)
    info_frame.pack(pady=10)

    ttk.Label(info_frame, text=f"Task Name:\n{task[0]}", font=("Verdana", 12, "bold"), wraplength=400, justify="center").pack(pady=5)
    ttk.Label(info_frame, text=f"Description:\n{task[1]}", font=("Verdana", 12, "bold"), wraplength=400, justify="center").pack(pady=5)
    ttk.Label(info_frame, text=f"Due Date: {task[2]}", font=("Verdana", 12, "bold")).pack(pady=5)

    ttk.Button(detail_win, text="Edit Task", command=lambda: open_task_editor(root, task_id)).pack(pady=10)
    ttk.Button(detail_win, text="Close", command=detail_win.destroy).pack()

import tkinter.messagebox as messagebox

import tkinter.messagebox as messagebox

def delete_task(root, name, show_main_page_callback):
    clear_window(root)
    root.title("Delete Task")
    root.configure(bg="#e6f0f5")

    style = ttk.Style()
    style.configure("TButton", font=("Verdana", 12, "bold"), padding=10)

    # Centered main frame
    main_frame = ttk.Frame(root)
    main_frame.place(relx=0.5, rely=0.45, anchor="center")

    # Header
    ttk.Label(main_frame, text="Delete Task", font=("Verdana", 20, "bold")).pack(pady=(0, 10))

    container = ttk.Frame(main_frame)
    container.pack(pady=10)

    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("SELECT task_id, task_name, task_description FROM tasks")
        tasks = c.fetchall()

    if not tasks:
        ttk.Label(container, text="No tasks to delete.", foreground="red", font=("Verdana", 12, "bold")).pack(pady=10)
    else:
        for task_id, task_name, task_desc in tasks:
            frame = ttk.Frame(container)
            frame.pack(fill="x", pady=5, padx=10)

            ttk.Label(frame, text=f"{task_name}: {task_desc}", font=("Verdana", 11)).pack(side="left", padx=5)

            def make_delete_func(tid=task_id, title=task_name):
                def delete_this_task():
                    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the task: '{title}'?")
                    if confirm:
                        with sqlite3.connect('tasks.db') as conn:
                            c = conn.cursor()
                            c.execute("DELETE FROM tasks WHERE task_id = ?", (tid,))
                            c.execute("DELETE FROM task_assignments WHERE task_id = ?", (tid,))
                            conn.commit()
                        delete_task(root, name, show_main_page_callback)
                return delete_this_task

            ttk.Button(frame, text="❌ Delete", command=make_delete_func()).pack(side="right")

    # Back button outside, bottom centered
    ttk.Button(root, text="⬅️ Back", command=lambda: display_admin(root, name, show_main_page_callback)).place(relx=0.5, rely=0.95, anchor="center")


def open_task_editor(root, task_id):
    """Opens an edit window to modify task details & user assignments."""
    editor = tk.Toplevel(root)
    editor.title("Edit Task")
    editor.configure(bg="#e6f0f5")
    editor.geometry("500x600")

    style = ttk.Style()
    style.configure("TButton", font=("Verdana", 12, "bold"), padding=10)

    ttk.Label(editor, text="Edit Task", font=("Verdana", 20, "bold")).pack

    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("SELECT task_name, task_description, due_date FROM tasks WHERE task_id = ?", (task_id,))
        task = c.fetchone()

    task_name_var = tk.StringVar(value=task[0])
    task_desc_var = tk.StringVar(value=task[1])
    due_date_var = tk.StringVar(value=task[2])

    form_frame = ttk.Frame(editor)
    form_frame.pack(pady=10)

    ttk.Label(form_frame, text="Task Name", font=("Verdana", 12, "bold")).pack()
    ttk.Entry(form_frame, textvariable=task_name_var, width=40).pack()

    ttk.Label(form_frame, text="Task Description", font=("Verdana", 12, "bold")).pack(pady=(10, 0))
    ttk.Entry(form_frame, textvariable=task_desc_var, width=40).pack()

    ttk.Label(form_frame, text="Due Date (YYYY-MM-DD)", font=("Verdana", 12, "bold")).pack(pady=(10, 0))
    ttk.Entry(form_frame, textvariable=due_date_var, width=40).pack()

    ttk.Label(editor, text="Currently Assigned Users", font=("Verdana", 12, "bold")).pack(pady=(20, 5))
    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM task_assignments WHERE task_id = ?", (task_id,))
        assigned_users = {user[0]: tk.BooleanVar(value=True) for user in c.fetchall()}

    for user, var in assigned_users.items():
        ttk.Checkbutton(editor, text=user.title(), variable=var).pack(anchor="w")

    ttk.Label(editor, text="Add New Users", font=("Verdana", 12, "bold")).pack(pady=(20, 5))
    with sqlite3.connect('userData.db') as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE role = 'User'")
        all_users = {user[0]: tk.BooleanVar() for user in c.fetchall() if user[0] not in assigned_users}

    for user, var in all_users.items():
        ttk.Checkbutton(editor, text=user.title(), variable=var).pack(anchor="w")

    def save_edits():
        new_name = task_name_var.get().strip()
        new_desc = task_desc_var.get().strip()
        new_due = due_date_var.get().strip()

        with sqlite3.connect('tasks.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE tasks SET task_name = ?, task_description = ?, due_date = ? WHERE task_id = ?",
                      (new_name, new_desc, new_due, task_id))

            for user, var in assigned_users.items():
                if not var.get():
                    c.execute("DELETE FROM task_assignments WHERE task_id = ? AND username = ?", (task_id, user))

            for user, var in all_users.items():
                if var.get():
                    c.execute("INSERT INTO task_assignments (task_id, username) VALUES (?, ?)", (task_id, user))

            conn.commit()

        editor.destroy()
        view_all_tasks(root, "Admin", display_admin)

    ttk.Button(editor, text="💾 Save Changes", command=save_edits).pack(pady=15)
    ttk.Button(editor, text="❌ Cancel", command=editor.destroy).pack()
