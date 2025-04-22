import tkinter
from auth import show_login_page, show_signup_page, show_main_page
from utils import clear_window

def clear_window(root):
    for widget in root.winfo_children():
        widget.destroy()

root = tkinter.Tk()
root.geometry("600x600")
show_main_page(root)
root.mainloop()