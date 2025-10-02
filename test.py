import tkinter as tk
from tkinter import Menu

def file_new_project():
    print("New Project")

def file_new_document():
    print("New Document")

def file_open():
    print("Open File")

def file_save():
    print("Save File")

def exit_app():
    root.destroy()

root = tk.Tk()
root.title("Menu Bar Example")

# Tạo một menu bar
menubar = Menu(root)
root.config(menu=menubar)

# Tạo menu File và thêm các lệnh con
file_menu = Menu(menubar, tearoff=0)

new_menu = Menu(file_menu, tearoff=0)
new_menu.add_command(label="New Project", command=file_new_project)
new_menu.add_command(label="New Document", command=file_new_document)

file_menu.add_cascade(label="New", menu=new_menu)
file_menu.add_command(label="Open", command=file_open)
file_menu.add_command(label="Save", command=file_save)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_app)

# Thêm menu File vào menu bar
menubar.add_cascade(label="File", menu=file_menu)

# Hiển thị cửa sổ
root.mainloop()
