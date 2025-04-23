import tkinter
import sqlite3
import os
import sys
from utils import clear_window

def restart_app():
    root.destroy()
    os.execl(sys.executable, sys.executable, *sys.argv)

def display_user(root, name, show_main_page_callback):
    clear_window(root)
    root.title(f"Welcome {name}")
    tkinter.Label(root, text="Your Assigned Tasks").pack(pady=5)

    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()

        # Add status column if not already present
        try:
            c.execute("ALTER TABLE task_assignments ADD COLUMN status TEXT DEFAULT 'Incomplete'")
        except sqlite3.OperationalError:
            pass

        c.execute("CREATE TABLE IF NOT EXISTS tasks (task_id INTEGER PRIMARY KEY AUTOINCREMENT, task_name TEXT, task_description TEXT)")
        c.execute("SELECT task_id, status FROM task_assignments WHERE username = ?", (name,))
        task_info = c.fetchall()

        for task_id, current_status in task_info:
            c.execute("SELECT task_name, task_description FROM tasks WHERE task_id = ?", (task_id,))
            task = c.fetchone()
            if task:
                frame = tkinter.Frame(root, relief="ridge", borderwidth=2, padx=10, pady=10)
                frame.pack(pady=5, fill="x", padx=10)

                task_name, task_desc = task
                tkinter.Label(frame, text=f"{task_name}: {task_desc}", font=("Arial", 10, "bold")).pack(anchor="w")

                status_var = tkinter.StringVar(value=current_status)
                dropdown = tkinter.OptionMenu(frame, status_var, "Incomplete", "In Progress", "Completed")
                dropdown.pack(anchor="w")

                def update_status(tid=task_id, sv=status_var):
                    with sqlite3.connect('tasks.db') as conn2:
                        cur = conn2.cursor()
                        cur.execute("UPDATE task_assignments SET status = ? WHERE task_id = ? AND username = ?", (sv.get(), tid, name))
                        conn2.commit()
                        tkinter.Label(frame, text="Status updated!", fg="green").pack(anchor="w")

                tkinter.Button(frame, text="Update Status", command=update_status).pack(anchor="w")

    # Simple logout 
    tkinter.Button(root, text="Logout", command=lambda: show_main_page_callback(root)).pack(pady=10)

    # OR, use this line if you want it to restart:
    # tkinter.Button(root, text="Logout", command=restart_app).pack(pady=10)
