import tkinter as tk
import sqlite3
from utils import clear_window

def display_user(root, name, show_main_page_callback):
    clear_window(root)
    root.title(f"Welcome {name.title()}")
    root.configure(bg="#e6f0f5")

    style = tk.ttk.Style()
    style.configure("TButton", font=("Verdana", 11, "bold"), padding=8)

    header = tk.Label(root, text=f"Welcome, {name.title()}! Here are your tasks:", font=("Verdana", 18, "bold"), bg="#e6f0f5")
    header.pack(pady=(20, 10))

    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT tasks.task_id, tasks.task_name, tasks.task_description, tasks.due_date, task_assignments.status 
            FROM task_assignments 
            JOIN tasks ON task_assignments.task_id = tasks.task_id 
            WHERE task_assignments.username = ?;
        ''', (name,))
        task_info = c.fetchall()

        for task_id, task_name, task_desc, due_date, current_status in task_info:
            frame = tk.Frame(root, relief="raised", borderwidth=2, padx=15, pady=10, bg="white")
            frame.pack(pady=8, fill="x", padx=40)

            task_label = tk.Label(frame, text=task_name, font=("Verdana", 12, "bold"), fg="blue", cursor="hand2", bg="white")
            task_label.pack(anchor="w")
            task_label.bind("<Button-1>", lambda e, tid=task_id: open_task_details(root, tid, name, show_main_page_callback))

            tk.Label(frame, text=f"Due Date: {due_date}", bg="white", font=("Verdana", 10)).pack(anchor="w")
            tk.Label(frame, text=f"Description: {task_desc}", bg="white", font=("Verdana", 10)).pack(anchor="w")

            status_var = tk.StringVar(value=current_status)
            dropdown = tk.OptionMenu(frame, status_var, "Incomplete", "In Progress", "Completed")
            dropdown_button = dropdown.nametowidget(dropdown.menuname)
            dropdown.config(width=20, font=("Verdana", 10))

            def set_dropdown_color(status, widget):
                color = "#fbcaca"
                if status == "Completed":
                    color = "#c7f2c4"
                elif status == "In Progress":
                    color = "#fff4c2"
                widget.config(bg=color)

            def update_color_on_change(*args):
                set_dropdown_color(status_var.get(), dropdown)

            status_var.trace_add("write", update_color_on_change)
            set_dropdown_color(current_status, dropdown)
            dropdown.pack(anchor="w", pady=3)

            def update_status(tid=task_id, var=status_var, drop=dropdown):
                new_status = var.get()
                with sqlite3.connect('tasks.db') as conn:
                    c = conn.cursor()
                    c.execute("UPDATE task_assignments SET status = ? WHERE task_id = ?", (new_status, tid))
                    conn.commit()
                set_dropdown_color(new_status, drop)
                tk.Label(frame, text="✅ Status updated!", fg="green", bg="white", font=("Verdana", 9)).pack(anchor="w")

            tk.Button(frame, text="Update Status", command=update_status, bg="#003366", fg="white", font=("Verdana", 10, "bold")).pack(pady=5)

    tk.Button(root, text="Logout", command=lambda: show_main_page_callback(root), bg="#666", fg="white", font=("Verdana", 10, "bold")).pack(pady=20)


def open_task_details(root, task_id, username, show_main_page_callback):
    details_window = tk.Toplevel(root)
    details_window.title("Task Details")
    details_window.configure(bg="#e6f0f5")
    details_window.geometry("450x450")

    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("SELECT task_name, task_description, due_date FROM tasks WHERE task_id = ?", (task_id,))
        task = c.fetchone()

        c.execute("SELECT username, status FROM task_assignments WHERE task_id = ?", (task_id,))
        assigned_users = c.fetchall()

    tk.Label(details_window, text="Task Details", font=("Verdana", 20, "bold"), bg="#e6f0f5").pack(pady=(20, 10))

    info_frame = tk.Frame(details_window, bg="#e6f0f5")
    info_frame.pack(pady=10)

    tk.Label(info_frame, text=f"Task Name:\n{task[0]}", font=("Verdana", 11), bg="#e6f0f5", wraplength=400, justify="left").pack(pady=5)
    tk.Label(info_frame, text=f"Description:\n{task[1]}", font=("Verdana", 11), bg="#e6f0f5", wraplength=400, justify="left").pack(pady=5)
    tk.Label(info_frame, text=f"Due Date: {task[2]}", font=("Verdana", 11), bg="#e6f0f5").pack(pady=5)

    tk.Label(details_window, text="Assigned Users & Status:", font=("Verdana", 11, "bold"), bg="#e6f0f5").pack(pady=(15, 5))
    for user, status in assigned_users:
        tk.Label(details_window, text=f"{user.title()}: {status}", bg="#e6f0f5", font=("Verdana", 10)).pack(anchor="w", padx=20)

    tk.Label(details_window, text="Update Your Task Status:", font=("Verdana", 11, "bold"), bg="#e6f0f5").pack(pady=(20, 5))

    status_var = tk.StringVar()
    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("SELECT status FROM task_assignments WHERE task_id = ? AND username = ?", (task_id, username))
        current_status = c.fetchone()
        if current_status:
            status_var.set(current_status[0])

    dropdown = tk.OptionMenu(details_window, status_var, "Incomplete", "In Progress", "Completed")
    dropdown_button = dropdown.nametowidget(dropdown.menuname)
    dropdown.config(width=20, font=("Verdana", 10))

    def set_dropdown_color(status, widget):
        color = "#fbcaca"
        if status == "Completed":
            color = "#c7f2c4"
        elif status == "In Progress":
            color = "#fff4c2"
        widget.config(bg=color)

    def update_color_on_change(*args):
        set_dropdown_color(status_var.get(), dropdown)

    status_var.trace_add("write", update_color_on_change)
    if current_status:
        set_dropdown_color(current_status[0], dropdown)

    dropdown.pack()

    def save_status():
        new_status = status_var.get()
        with sqlite3.connect('tasks.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE task_assignments SET status = ? WHERE task_id = ? AND username = ?", (new_status, task_id, username))
            conn.commit()
        details_window.destroy()
        display_user(root, username, show_main_page_callback)

    tk.Button(details_window, text="Save Status", command=save_status, bg="#003366", fg="white", font=("Verdana", 10, "bold")).pack(pady=10)
    tk.Button(details_window, text="Back", command=details_window.destroy, bg="#666", fg="white", font=("Verdana", 10, "bold")).pack(pady=5)