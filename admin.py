import tkinter
import sqlite3
from utils import clear_window
def display_admin(root, name, show_main_page_callback):
    clear_window(root)
    root.title(f"Welcome Admin: {name}")

    tkinter.Label(root, text=f"Logged in as: {name}").pack(pady=5)
    tkinter.Button(root, text="Create Task", command=lambda: create_task(root, name, show_main_page_callback)).pack()
    tkinter.Button(root, text="Delete Task", command=lambda: delete_task(root, name, show_main_page_callback)).pack()
    tkinter.Button(root, text="View All Tasks", command=lambda: view_all_tasks(root, name, show_main_page_callback)).pack()
    tkinter.Button(root, text="Logout", command=lambda: show_main_page_callback(root)).pack(pady=10)

def create_task(root, name, show_main_page_callback):
    clear_window(root)
    root.title("Create Task")

    tkinter.Label(root, text="Task Name").pack()
    task_name_entry = tkinter.Entry(root)
    task_name_entry.pack()

    tkinter.Label(root, text="Task Description").pack()
    task_description_entry = tkinter.Entry(root)
    task_description_entry.pack()

    tkinter.Label(root, text="Due Date (YYYY-MM-DD)").pack()
    due_date_entry = tkinter.Entry(root)
    due_date_entry.pack()

    with sqlite3.connect('userData.db') as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE role = 'User'")
        users = c.fetchall()

    tkinter.Label(root, text="Assign to Users:").pack()
    user_vars = {}
    for user in users:
        var = tkinter.BooleanVar()
        user_vars[user[0]] = var
        tkinter.Checkbutton(root, text=user[0], variable=var).pack()



    def save_task():
        task_name = task_name_entry.get()
        task_description = task_description_entry.get()
        due_date = due_date_entry.get()
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
            tkinter.Label(root, text="Task created and assigned successfully!", fg="green").pack()
        else:
            tkinter.Label(root, text="All fields, including due date and at least one user, are required!", fg="red").pack()

    tkinter.Button(root, text="Save", command=save_task).pack()
    tkinter.Button(root, text="Back", command=lambda: display_admin(root, name, show_main_page_callback)).pack()

def truncate_text(text, max_length=20):
    """Truncate long text with '...' for table display."""
    return text if len(text) <= max_length else text[:max_length] + "..."

def view_all_tasks(root, name, show_main_page_callback):
    clear_window(root)
    root.title("All Tasks Overview")

    table_frame = tkinter.Frame(root)
    table_frame.pack(pady=10)

    headers = ["Task Name", "Description", "Status", "Assigned To", "Due Date"]
    for i, h in enumerate(headers):
        tkinter.Label(table_frame, text=h, borderwidth=2, relief="groove", width=20, bg="#cce6ff", font=("Arial", 10, "bold")).grid(row=0, column=i)

    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("SELECT task_id, task_name, task_description, due_date FROM tasks")
        tasks = c.fetchall()

        for row_idx, task in enumerate(tasks, start=1):
            task_id, task_name, task_description, due_date = task

            # Fetch assigned users
            c.execute("SELECT username FROM task_assignments WHERE task_id = ?", (task_id,))
            assignees = ', '.join([a[0] for a in c.fetchall()])

            # Determine task status
            c.execute("SELECT status FROM task_assignments WHERE task_id = ?", (task_id,))
            status_rows = c.fetchall()

            if not status_rows:
                status = "Not Started"
            elif any(row[0] == "Completed" for row in status_rows):
                status = "Completed"
            else:
                status = "In Progress"

            # Color coding for status
            status_color = {"Completed": "#4CAF50", "In Progress": "#FFC107", "Not Started": "#FF5733"}

            # Create clickable task label (opens details page)
            task_label = tkinter.Label(table_frame, text=truncate_text(task_name), fg="blue", cursor="hand2", borderwidth=1, relief="solid", width=20)
            task_label.grid(row=row_idx, column=0)
            task_label.bind("<Button-1>", lambda event, tid=task_id: open_task_card(root, tid))  # Click event

            # Truncated description
            tkinter.Label(table_frame, text=truncate_text(task_description), borderwidth=1, relief="solid", width=20).grid(row=row_idx, column=1)

            # Status with color
            tkinter.Label(table_frame, text=status, bg=status_color[status], borderwidth=1, relief="solid", width=20).grid(row=row_idx, column=2)

            tkinter.Label(table_frame, text=assignees, borderwidth=1, relief="solid", width=20).grid(row=row_idx, column=3)
            tkinter.Label(table_frame, text=due_date, borderwidth=1, relief="solid", width=20).grid(row=row_idx, column=4)

    tkinter.Button(root, text="Back", command=lambda: display_admin(root, name, show_main_page_callback)).pack(pady=10)
def open_task_card(root, task_id):
    """Opens a detailed view of the selected task."""
    card_window = tkinter.Toplevel(root)
    card_window.title("Task Details")
    card_window.configure(bg="white")
    card_window.geometry("400x350")

    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("SELECT task_name, task_description, due_date FROM tasks WHERE task_id = ?", (task_id,))
        task = c.fetchone()

    # Task information
    tkinter.Label(card_window, text="Task Details", font=("Arial", 14, "bold"), bg="#003366", fg="white", padx=10, pady=5).pack(fill="x")
    tkinter.Label(card_window, text=f"Task Name:\n{task[0]}", font=("Arial", 12), bg="white", padx=10, pady=5).pack()
    tkinter.Label(card_window, text=f"Description:\n{task[1]}", font=("Arial", 12), bg="white", padx=10, pady=5).pack()
    tkinter.Label(card_window, text=f"Due Date:\n{task[2]}", font=("Arial", 12), bg="white", padx=10, pady=5).pack()

    # Buttons
    tkinter.Button(card_window, text="Edit Task", fg="white", bg="#003366", command=lambda: open_task_editor(root, task_id)).pack(pady=5)
    tkinter.Button(card_window, text="Back", fg="white", bg="#666", command=card_window.destroy).pack(pady=5)

def delete_task(root, name, show_main_page_callback):
    clear_window(root)
    root.title("Delete Task")

    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS tasks (task_id INTEGER PRIMARY KEY AUTOINCREMENT, task_name TEXT, task_description TEXT, due_date TEXT)")
        c.execute("SELECT task_id, task_name, task_description FROM tasks")
        tasks = c.fetchall()

    if not tasks:
        tkinter.Label(root, text="No tasks to delete.").pack(pady=10)
    else:
        for task_id, task_name, task_desc in tasks:
            frame = tkinter.Frame(root, pady=5)
            frame.pack(fill="x", padx=10)
            tkinter.Label(frame, text=f"{task_name} - {task_desc}", anchor="w").pack(side="left", fill="x", expand=True)

            def make_delete_func(tid=task_id):
                def delete_this_task():
                    with sqlite3.connect('tasks.db') as conn:
                        c = conn.cursor()
                        c.execute("DELETE FROM tasks WHERE task_id = ?", (tid,))
                        c.execute("DELETE FROM task_assignments WHERE task_id = ?", (tid,))
                        conn.commit()
                    delete_task(root, name, show_main_page_callback)  # Refresh list after delete
                return delete_this_task

            tkinter.Button(frame, text="Delete", fg="red", command=make_delete_func()).pack(side="right")

    tkinter.Button(root, text="Back", command=lambda: display_admin(root, name, show_main_page_callback)).pack(pady=10)
def open_task_editor(root, task_id):
    """Opens an edit window to modify task details & user assignments."""

    # Create the edit window
    edit_window = tkinter.Toplevel(root)
    edit_window.title("Edit Task")
    edit_window.configure(bg="white")
    edit_window.geometry("450x550")

    # Fetch task details
    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("SELECT task_name, task_description, due_date FROM tasks WHERE task_id = ?", (task_id,))
        task = c.fetchone()

    # Task Variables
    task_name_var = tkinter.StringVar(value=task[0])
    task_desc_var = tkinter.StringVar(value=task[1])
    due_date_var = tkinter.StringVar(value=task[2])

    # Header Styling
    tkinter.Label(edit_window, text="Edit Task", font=("Arial", 14, "bold"), bg="#003366", fg="white", padx=10, pady=5).pack(fill="x")

    # Task Name
    tkinter.Label(edit_window, text="Task Name:", bg="white").pack(pady=3)
    task_name_entry = tkinter.Entry(edit_window, textvariable=task_name_var, width=40)
    task_name_entry.pack()

    # Task Description
    tkinter.Label(edit_window, text="Task Description:", bg="white").pack(pady=3)
    task_desc_entry = tkinter.Entry(edit_window, textvariable=task_desc_var, width=40)
    task_desc_entry.pack()

    # Due Date
    tkinter.Label(edit_window, text="Due Date (YYYY-MM-DD):", bg="white").pack(pady=3)
    due_date_entry = tkinter.Entry(edit_window, textvariable=due_date_var, width=40)
    due_date_entry.pack()

    # Fetch Assigned Users
    tkinter.Label(edit_window, text="Assigned Users:", font=("Arial", 10, "bold"), bg="white").pack(pady=5)
    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM task_assignments WHERE task_id = ?", (task_id,))
        assigned_users = {user[0]: tkinter.BooleanVar(value=True) for user in c.fetchall()}

    # Display assigned users with checkboxes
    for user, var in assigned_users.items():
        tkinter.Checkbutton(edit_window, text=user, variable=var, bg="white").pack()

    # Fetch all users for adding new ones
    tkinter.Label(edit_window, text="Add Users to Task:", font=("Arial", 10, "bold"), bg="white").pack(pady=5)
    with sqlite3.connect('userData.db') as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE role = 'User'")
        all_users = {user[0]: tkinter.BooleanVar() for user in c.fetchall() if user[0] not in assigned_users}

    # Display available users to add
    for user, var in all_users.items():
        tkinter.Checkbutton(edit_window, text=user, variable=var, bg="white").pack()

    # Save Changes
    def save_edits():
        new_name = task_name_var.get()
        new_desc = task_desc_var.get()
        new_due = due_date_var.get()

        with sqlite3.connect('tasks.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE tasks SET task_name = ?, task_description = ?, due_date = ? WHERE task_id = ?", (new_name, new_desc, new_due, task_id))

            # Remove users who were unchecked
            for user, var in assigned_users.items():
                if not var.get():
                    c.execute("DELETE FROM task_assignments WHERE task_id = ? AND username = ?", (task_id, user))

            # Add newly selected users
            for user, var in all_users.items():
                if var.get():
                    c.execute("INSERT INTO task_assignments (task_id, username) VALUES (?, ?)", (task_id, user))

            conn.commit()

        edit_window.destroy()
        view_all_tasks(root, "Admin", display_admin)  # Refresh task list

    tkinter.Button(edit_window, text="Save Changes", fg="white", bg="#003366", command=save_edits).pack(pady=10)
    tkinter.Button(edit_window, text="Back", fg="white", bg="#666", command=edit_window.destroy).pack(pady=5)