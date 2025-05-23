import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import sqlite3

DB_FILE = "tasks.db"

# ------------------ DATABASE FUNCTIONS ------------------ #
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_tasks():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, task, completed FROM tasks ORDER BY id')
    tasks = c.fetchall()
    conn.close()
    return tasks

def add_task_db(task_text):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO tasks (task) VALUES (?)', (task_text,))
    conn.commit()
    conn.close()

def delete_task_db(task_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def update_task_db(task_id, new_text):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE tasks SET task = ? WHERE id = ?', (new_text, task_id))
    conn.commit()
    conn.close()

def update_task_status_db(task_id, completed):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE tasks SET completed = ? WHERE id = ?', (completed, task_id))
    conn.commit()
    conn.close()

def clear_all_tasks_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM tasks')
    conn.commit()
    conn.close()

# ------------------ GUI FUNCTIONS ------------------ #
def refresh_tasks():
    listbox_tasks.delete(0, tk.END)
    global tasks_list
    tasks_list = get_tasks()
    for tid, task, completed in tasks_list:
        display_text = "✔️ " + task if completed else task
        listbox_tasks.insert(tk.END, display_text)
    status_var.set(f"Tasks loaded: {len(tasks_list)}")

def add_task():
    task = entry_task.get().strip()
    if not task:
        status_var.set("⚠️ Please enter a task.")
        return
    add_task_db(task)
    entry_task.delete(0, tk.END)
    refresh_tasks()
    status_var.set(f"✅ Task added: {task}")

def delete_task():
    try:
        selected_index = listbox_tasks.curselection()[0]
        task_id, task_text, completed = tasks_list[selected_index]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the task?\n\n{task_text}"):
            delete_task_db(task_id)
            refresh_tasks()
            status_var.set(f"🗑️ Task deleted: {task_text}")
    except IndexError:
        status_var.set("⚠️ Please select a task to delete.")

def mark_complete():
    try:
        selected_index = listbox_tasks.curselection()[0]
        task_id, task_text, completed = tasks_list[selected_index]
        new_status = 0 if completed else 1
        update_task_status_db(task_id, new_status)
        refresh_tasks()
        if new_status:
            status_var.set(f"✔️ Task marked complete: {task_text}")
        else:
            status_var.set(f"❌ Task marked incomplete: {task_text}")
        listbox_tasks.select_set(selected_index)
    except IndexError:
        status_var.set("⚠️ Please select a task to mark complete.")

def edit_task():
    try:
        selected_index = listbox_tasks.curselection()[0]
        task_id, old_task, completed = tasks_list[selected_index]
        new_task = simpledialog.askstring("Edit Task", "Modify the task:", initialvalue=old_task)
        if new_task:
            new_task = new_task.strip()
            if not new_task:
                status_var.set("⚠️ Task cannot be empty.")
                return
            update_task_db(task_id, new_task)
            refresh_tasks()
            listbox_tasks.select_set(selected_index)
            status_var.set(f"✏️ Task edited: {new_task}")
    except IndexError:
        status_var.set("⚠️ Please select a task to edit.")

def clear_all_tasks():
    if messagebox.askyesno("Clear All", "Are you sure you want to delete ALL tasks?"):
        clear_all_tasks_db()
        refresh_tasks()
        status_var.set("🗑️ All tasks cleared.")

def save_tasks_to_file():
    tasks = get_tasks()
    if not tasks:
        messagebox.showinfo("No Tasks", "There are no tasks to save.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
        title="Save Tasks As"
    )
    if not file_path:
        return

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for _, task, completed in tasks:
                status = "[✔]" if completed else "[ ]"
                f.write(f"{status} {task}\n")
        status_var.set(f"💾 Tasks saved to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save tasks:\n{e}")

def about_app():
    messagebox.showinfo("About", "To-Do List App + Text Editor\nCreated by Sonakshi\nVersion 1.0")

def toggle_fullscreen(event=None):
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))

# ------------------ TEXT EDITOR ------------------ #
def open_text_editor():
    editor_win = tk.Toplevel(root)
    editor_win.title("📝 Text Editor")
    editor_win.geometry("600x400")

    text_area = tk.Text(editor_win, wrap="word", font=("Segoe UI", 12))
    text_area.pack(fill="both", expand=True)

    def save_text():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save Note As"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text_area.get(1.0, tk.END))
                messagebox.showinfo("Saved", f"✅ Note saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving note:\n{e}")

    save_button = tk.Button(editor_win, text="💾 Save Note", command=save_text, bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"))
    save_button.pack(fill="x")

# ------------------ MAIN WINDOW SETUP ------------------ #
init_db()

root = tk.Tk()
root.title("📝 To-Do List + Text Editor")
root.geometry("480x550")
root.minsize(480, 550)
root.configure(padx=20, pady=20)
root.resizable(True, True)
root.bind("<F11>", toggle_fullscreen)

# ------------------ MENU ------------------ #
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open Text Editor", command=open_text_editor)
file_menu.add_command(label="Save Tasks to File", command=save_tasks_to_file)
file_menu.add_command(label="Clear All Tasks", command=clear_all_tasks)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About", command=about_app)
menu_bar.add_cascade(label="Help", menu=help_menu)

# ------------------ ENTRY + BUTTON ------------------ #
frame_entry = tk.Frame(root)
frame_entry.pack(fill='x', pady=(0, 10))

entry_task = tk.Entry(frame_entry, font=("Segoe UI", 14))
entry_task.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 10))
entry_task.focus()

btn_add = tk.Button(frame_entry, text="Add Task", command=add_task, bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"))
btn_add.pack(side=tk.LEFT)

# ------------------ TASK LIST ------------------ #
frame_tasks = tk.Frame(root)
frame_tasks.pack(fill='both', expand=True)

scrollbar = tk.Scrollbar(frame_tasks)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox_tasks = tk.Listbox(frame_tasks, font=("Segoe UI", 14), yscrollcommand=scrollbar.set, selectmode=tk.SINGLE, activestyle='none')
listbox_tasks.pack(fill='both', expand=True)
scrollbar.config(command=listbox_tasks.yview)

# ------------------ ACTION BUTTONS ------------------ #
frame_buttons = tk.Frame(root)
frame_buttons.pack(fill='x', pady=15)

btn_edit = tk.Button(frame_buttons, text="Edit Task", command=edit_task, bg="#FF9800", fg="white", font=("Segoe UI", 12, "bold"))
btn_edit.pack(side=tk.LEFT, expand=True, fill='x', padx=5)

btn_complete = tk.Button(frame_buttons, text="Mark Complete", command=mark_complete, bg="#2196F3", fg="white", font=("Segoe UI", 12, "bold"))
btn_complete.pack(side=tk.LEFT, expand=True, fill='x', padx=5)

btn_delete = tk.Button(frame_buttons, text="Delete Task", command=delete_task, bg="#f44336", fg="white", font=("Segoe UI", 12, "bold"))
btn_delete.pack(side=tk.LEFT, expand=True, fill='x', padx=5)

# ------------------ STATUS BAR ------------------ #
status_var = tk.StringVar()
status_var.set("Welcome! Add your first task.")
status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Segoe UI", 10, "italic"))
status_bar.pack(side=tk.BOTTOM, fill='x')

# ------------------ LOAD TASKS & RUN ------------------ #
root.bind('<Return>', lambda event: add_task())
tasks_list = []
refresh_tasks()

root.mainloop()
