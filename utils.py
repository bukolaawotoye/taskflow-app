def clear_window(root):
    for widget in root.winfo_children():
        widget.destroy()
