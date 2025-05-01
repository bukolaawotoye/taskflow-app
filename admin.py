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

def view_all_tasks(root, name, show_main_page_callback):
    # Clear the window and set the title
    clear_window(root)
    root.title("All Tasks Overview")
    
    # Create a frame for the table
    table_frame = tkinter.Frame(root)
    table_frame.pack(pady=10)

    # Add table headers
    headers = ["Task Name", "Description", "Status", "Assigned To", "Due Date"]
    for i, h in enumerate(headers):
        tkinter.Label(
            table_frame, 
            text=h, 
            borderwidth=2, 
            relief="groove", 
            width=30, 
            bg="#cce6ff", 
            font=("Arial", 10, "bold")
        ).grid(row=0, column=i)

    # Connect to the database and retrieve tasks and assignments
    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        
        # Fetch tasks along with descriptions
        c.execute("SELECT task_id, task_name, task_description, due_date FROM tasks")
        tasks = c.fetchall()

        # Populate table with task data
        for row_idx, task in enumerate(tasks, start=1):
            task_id, task_name, task_description, due_date = task
            
            # Fetch usernames assigned to the task
            c.execute("SELECT username FROM task_assignments WHERE task_id = ?", (task_id,))
            assignees = c.fetchall()
            
            # Fetch statuses for the task
            c.execute("SELECT status FROM task_assignments WHERE task_id = ?", (task_id,))
            status_rows = c.fetchall()
            
            # Determine the task status
            if not assignees:
                status = "Not Started"
            elif any(row[0] == "Completed" for row in status_rows):
                status = "Completed"
            else:
                status = "In Progress"

            # Format assignee list
            assignee_list = ', '.join([a[0] for a in assignees]) if assignees else 'No one assigned'

            # Display task data in the table
            tkinter.Label(
                table_frame, 
                text=task_name, 
                borderwidth=1, 
                relief="solid", 
                width=30
            ).grid(row=row_idx, column=0)
            tkinter.Label(
                table_frame, 
                text=task_description, 
                borderwidth=1, 
                relief="solid", 
                width=30
            ).grid(row=row_idx, column=1)
            tkinter.Label(
                table_frame, 
                text=status, 
                borderwidth=1, 
                relief="solid", 
                width=30
            ).grid(row=row_idx, column=2)
            tkinter.Label(
                table_frame, 
                text=assignee_list, 
                borderwidth=1, 
                relief="solid", 
                width=30
            ).grid(row=row_idx, column=3)
            tkinter.Label(
                table_frame, 
                text=due_date, 
                borderwidth=1, 
                relief="solid", 
                width=30
            ).grid(row=row_idx, column=4)

    tkinter.Button(root, text="Back", command=lambda: display_admin(root, name, show_main_page_callback)).pack(pady=10)


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

