import tkinter
import sqlite3
import os
import sys
from utils import clear_window



def display_user(root, name, show_main_page_callback):
    """Displays tasks assigned to a user with real-time status syncing."""

    clear_window(root)
    root.title(f"Welcome {name}")
    
    tkinter.Label(root, text="Your Assigned Tasks", font=("Arial", 14, "bold"), fg="white", bg="#003366", padx=10, pady=5).pack(fill="x")

    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        query = """
        SELECT tasks.task_id, tasks.task_name, tasks.task_description, tasks.due_date, task_assignments.status 
        FROM task_assignments 
        JOIN tasks ON task_assignments.task_id = tasks.task_id 
        WHERE task_assignments.username = ?;
        """
        c.execute(query, (name,))
        task_info = c.fetchall()

        for task_id, task_name, task_desc, due_date, current_status in task_info:
            frame = tkinter.Frame(root, relief="ridge", borderwidth=2, padx=10, pady=10, bg="white")
            frame.pack(pady=5, fill="x", padx=10)

            # Clickable task label to open details
            task_label = tkinter.Label(frame, text=task_name, font=("Arial", 10, "bold"), fg="blue", cursor="hand2", bg="white")
            task_label.pack(anchor="w")
            task_label.bind("<Button-1>", lambda event, tid=task_id: open_task_details(root, tid, name, show_main_page_callback))  # Corrected

            tkinter.Label(frame, text=f"Due Date: {due_date}", bg="white").pack(anchor="w")
            
            # Status Dropdown
            status_var = tkinter.StringVar(value=current_status)
            dropdown = tkinter.OptionMenu(frame, status_var, "Incomplete", "In Progress", "Completed")
            dropdown.pack(anchor="w")

            # Update Status function (sync across all users)
            def update_status():
                with sqlite3.connect('tasks.db') as conn:
                    c = conn.cursor()
                    c.execute("UPDATE task_assignments SET status = ? WHERE task_id = ?", (status_var.get(), task_id))
                    conn.commit()
                tkinter.Label(frame, text="Status updated for all users!", fg="green", bg="white").pack(anchor="w")

            tkinter.Button(frame, text="Update Status", fg="white", bg="#003366", command=update_status).pack(pady=5)
    
    tkinter.Button(root, text="Logout", fg="white", bg="#666", command=lambda: show_main_page_callback(root)).pack(pady=10)
def open_task_details(root, task_id, username, show_main_page_callback):
    """Opens a detailed task view where the user can update their task status."""

    details_window = tkinter.Toplevel(root)
    details_window.title("Task Details")
    details_window.configure(bg="white")
    details_window.geometry("450x450")

    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("SELECT task_name, task_description, due_date FROM tasks WHERE task_id = ?", (task_id,))
        task = c.fetchone()

        c.execute("SELECT username, status FROM task_assignments WHERE task_id = ?", (task_id,))
        assigned_users = c.fetchall()

    # Styling header
    tkinter.Label(details_window, text="Task Details", font=("Arial", 14, "bold"), bg="#003366", fg="white", padx=10, pady=5).pack(fill="x")

    # Displaying task details
    tkinter.Label(details_window, text=f"Task Name:\n{task[0]}", font=("Arial", 12), bg="white", padx=10, pady=5).pack()
    tkinter.Label(details_window, text=f"Description:\n{task[1]}", font=("Arial", 12), bg="white", padx=10, pady=5).pack()
    tkinter.Label(details_window, text=f"Due Date:\n{task[2]}", font=("Arial", 12), bg="white", padx=10, pady=5).pack()

    # Display Assigned Users & Their Statuses
    tkinter.Label(details_window, text="Assigned Users & Status:", font=("Arial", 10, "bold"), bg="white").pack(pady=5)
    for user, status in assigned_users:
        tkinter.Label(details_window, text=f"{user}: {status}", bg="white").pack(anchor="w")

    # Status Dropdown (User updates only their own task status)
    tkinter.Label(details_window, text="Update Your Task Status:", font=("Arial", 10, "bold"), bg="white").pack(pady=5)
    status_var = tkinter.StringVar()
    
    with sqlite3.connect('tasks.db') as conn:
        c = conn.cursor()
        c.execute("SELECT status FROM task_assignments WHERE task_id = ? AND username = ?", (task_id, username))
        current_status = c.fetchone()
        if current_status:
            status_var.set(current_status[0])  # Set dropdown default to current status
    
    dropdown = tkinter.OptionMenu(details_window, status_var, "Incomplete", "In Progress", "Completed")
    dropdown.pack()

    # Save Status Function (Ensures UI Refresh After Saving)
    def save_status():
        new_status = status_var.get()
        with sqlite3.connect('tasks.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE task_assignments SET status = ? WHERE task_id = ? AND username = ?", (new_status, task_id, username))
            conn.commit()
        
        # Close details window and refresh user task view
        details_window.destroy()
        display_user(root, username, show_main_page_callback)

    tkinter.Button(details_window, text="Save Status", fg="white", bg="#003366", command=save_status).pack(pady=10)
    tkinter.Button(details_window, text="Back", fg="white", bg="#666", command=details_window.destroy).pack(pady=5)