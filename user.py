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

        # Fetch task details, including due_date and status
        query = """
        SELECT tasks.task_name, tasks.task_description, tasks.due_date, task_assignments.status 
        FROM task_assignments 
        JOIN tasks ON task_assignments.task_id = tasks.task_id 
        WHERE task_assignments.username = ?;
        """
        c.execute(query, (name,))
        task_info = c.fetchall()

        for task_name, task_desc, due_date, current_status in task_info:
            frame = tkinter.Frame(root, relief="ridge", borderwidth=2, padx=10, pady=10)
            frame.pack(pady=5, fill="x", padx=10)

            # Display task name, description, and due date
            label_text = f"{task_name}: {task_desc}\nDue Date: {due_date}"
            task_label = tkinter.Label(frame, text=label_text, font=("Arial", 10, "bold"))
            task_label.pack(anchor="w")

            # Apply strikethrough if status is "Completed"
            if current_status == "Completed":
                task_label.config(font=("Arial", 10, "bold", "italic"), fg="gray")
            
            # Status dropdown menu
            status_var = tkinter.StringVar(value=current_status)
            dropdown = tkinter.OptionMenu(frame, status_var, "Incomplete", "In Progress", "Completed")
            dropdown.pack(anchor="w")

            # Update status function specific to this task and label
            def update_status(sv=status_var, label=task_label):
                with sqlite3.connect('tasks.db') as conn2:
                    cur = conn2.cursor()
                    cur.execute("UPDATE task_assignments SET status = ? WHERE task_id = (SELECT task_id FROM tasks WHERE task_name = ? AND task_description = ?) AND username = ?",
                                (sv.get(), task_name, task_desc, name))
                    conn2.commit()

                # Apply or remove strikethrough based on updated status
                if sv.get() == "Completed":
                    label.config(font=("Arial", 10, "bold", "italic"), fg="gray")
                else:
                    label.config(font=("Arial", 10, "bold"), fg="black")

                tkinter.Label(frame, text="Status updated!", fg="green").pack(anchor="w")

            tkinter.Button(frame, text="Update Status", command=update_status).pack(anchor="w")
        tkinter.Button(root, text="Logout", command=lambda: show_main_page_callback(root)).pack(pady=10)

