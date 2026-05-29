import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# DATABASE CONNECTION
conn = sqlite3.connect("database.db")
cur = conn.cursor()

# CREATE TABLES
cur.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    roll TEXT,
    branch TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS halls(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hall_name TEXT,
    capacity INTEGER
)
""")
conn.commit()


# ALGORITHMIC ENGINE: AI Constraint Placement
def intelligent_interleave(students):
    """
    Groups students by branch and interleaves them using a round-robin approach.
    This acts as a heuristic-based constraint solver to prevent adjacent
    students from having the same branch.
    """
    from collections import defaultdict, deque

    branch_map = defaultdict(deque)
    for s in students:
        branch_map[s[3]].append(s)

    allocated_list = []
    while branch_map:
        branches_to_remove = []
        for branch, q in branch_map.items():
            if q:
                allocated_list.append(q.popleft())
            if not q:
                branches_to_remove.append(branch)
        
        for branch in branches_to_remove:
            del branch_map[branch]
            
    return allocated_list


# FUNCTIONS
def add_student():
    name = student_name_entry.get().strip()
    roll = student_roll_entry.get().strip()
    branch = student_branch_entry.get().strip().upper()

    if not name or not roll or not branch:
        messagebox.showerror("Error", "Please fill all fields")
        return

    cur.execute(
        "INSERT INTO students(name, roll, branch) VALUES(?,?,?)",
        (name, roll, branch)
    )
    conn.commit()
    messagebox.showinfo("Success", f"Student '{name}' Added Successfully")

    student_name_entry.delete(0, tk.END)
    student_roll_entry.delete(0, tk.END)
    student_branch_entry.delete(0, tk.END)
    refresh_management_tables() # Refresh the view list


def add_hall():
    hall_name = hall_name_entry.get().strip()
    capacity_raw = hall_capacity_entry.get().strip()

    if not hall_name or not capacity_raw:
        messagebox.showerror("Error", "Please fill all fields")
        return

    try:
        capacity = int(capacity_raw)
    except ValueError:
        messagebox.showerror("Error", "Capacity must be an integer")
        return

    cur.execute(
        "INSERT INTO halls(hall_name, capacity) VALUES(?,?)",
        (hall_name, capacity)
    )
    conn.commit()
    messagebox.showinfo("Success", f"Hall '{hall_name}' Added Successfully")

    hall_name_entry.delete(0, tk.END)
    hall_capacity_entry.delete(0, tk.END)
    refresh_management_tables() # Refresh the view list


def generate_seating():
    output_text.delete(1.0, tk.END)

    raw_students = cur.execute("SELECT * FROM students").fetchall()
    halls = cur.execute("SELECT * FROM halls").fetchall()

    if not raw_students:
        messagebox.showerror("Error", "No students found in the database")
        return
    if not halls:
        messagebox.showerror("Error", "No halls found in the database")
        return

    smart_students = intelligent_interleave(raw_students)
    student_index = 0
    total_students = len(smart_students)

    output_text.insert(tk.END, "====== OPTIMIZED EXAMINATION SEATING ARRANGEMENT ======\n\n")

    for hall in halls:
        hall_name = hall[1]
        capacity = hall[2]

        output_text.insert(tk.END, f"----------------------------------------\n")
        output_text.insert(tk.END, f"  HALL: {hall_name} (Capacity: {capacity})\n")
        output_text.insert(tk.END, f"----------------------------------------\n")

        for seat in range(capacity):
            if student_index < total_students:
                student = smart_students[student_index]
                output_text.insert(
                    tk.END,
                    f"  Seat {seat+1:02d}  -->  [Roll: {student[2]}] {student[1]:<15} ({student[3]})\n"
                )
                student_index += 1
            else:
                output_text.insert(tk.END, f"  Seat {seat+1:02d}  -->  [VACANT]\n")
        
        output_text.insert(tk.END, "\n")

    if student_index < total_students:
        remaining = total_students - student_index
        messagebox.showwarning(
            "Capacity Warning", 
            f"Arrangement completed, but {remaining} student(s) could not fit. Add more halls!"
        )


# NEW FUNCTIONS FOR DELETING PAST INPUTS
def refresh_management_tables():
    """Fetches the latest data from the DB and updates the visible lists."""
    # Clear existing lists
    for item in student_tree.get_children():
        student_tree.delete(item)
    for item in hall_tree.get_children():
        hall_tree.delete(item)

    # Populate Students
    for row in cur.execute("SELECT id, roll, name, branch FROM students").fetchall():
        student_tree.insert("", tk.END, values=row)

    # Populate Halls
    for row in cur.execute("SELECT id, hall_name, capacity FROM halls").fetchall():
        hall_tree.insert("", tk.END, values=row)


def delete_selected_student():
    selected_item = student_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a student to delete from the list")
        return
    
    # Get the ID column value of the selected student
    student_values = student_tree.item(selected_item, "values")
    student_id = student_values[0]
    student_name = student_values[2]

    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student: {student_name}?")
    if confirm:
        cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        messagebox.showinfo("Deleted", f"Student '{student_name}' removed from database.")
        refresh_management_tables()


def delete_selected_hall():
    selected_item = hall_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a hall to delete from the list")
        return
    
    # Get the ID column value of the selected hall
    hall_values = hall_tree.item(selected_item, "values")
    hall_id = hall_values[0]
    hall_name = hall_values[1]

    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete hall: {hall_name}?")
    if confirm:
        cur.execute("DELETE FROM halls WHERE id = ?", (hall_id,))
        conn.commit()
        messagebox.showinfo("Deleted", f"Hall '{hall_name}' removed from database.")
        refresh_management_tables()


# MAIN WINDOW
root = tk.Tk()
root.title("AI-Powered Exam Seating Planner")
root.geometry("950x850") # Expanded slightly to fit management utilities

style = ttk.Style()
style.theme_use("clam")

main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill="both", expand=True)

title_label = ttk.Label(
    main_frame, 
    text="Exam Seating Arrangement System", 
    font=("Helvetica", 18, "bold")
)
title_label.pack(pady=(0, 15))

# Top Split Frame for Inputs
input_frame = ttk.Frame(main_frame)
input_frame.pack(fill="x", pady=5)

# Student Form Frame
sf = ttk.LabelFrame(input_frame, text=" Register Student ", padding="10")
sf.pack(side="left", fill="both", expand=True, padx=(0, 10))

ttk.Label(sf, text="Name:").grid(row=0, column=0, sticky="w", pady=2)
student_name_entry = ttk.Entry(sf, width=25)
student_name_entry.grid(row=0, column=1, pady=2, padx=5)

ttk.Label(sf, text="Roll No:").grid(row=1, column=0, sticky="w", pady=2)
student_roll_entry = ttk.Entry(sf, width=25)
student_roll_entry.grid(row=1, column=1, pady=2, padx=5)

ttk.Label(sf, text="Branch:").grid(row=2, column=0, sticky="w", pady=2)
student_branch_entry = ttk.Entry(sf, width=25)
student_branch_entry.grid(row=2, column=1, pady=2, padx=5)

btn_add_student = ttk.Button(sf, text="Add Student", command=add_student)
btn_add_student.grid(row=3, column=1, pady=10, sticky="e")

# Hall Form Frame
hf = ttk.LabelFrame(input_frame, text=" Register Hall ", padding="10")
hf.pack(side="right", fill="both", expand=True, padx=(10, 0))

ttk.Label(hf, text="Hall Name:").grid(row=0, column=0, sticky="w", pady=2)
hall_name_entry = ttk.Entry(hf, width=25)
hall_name_entry.grid(row=0, column=1, pady=2, padx=5)

ttk.Label(hf, text="Capacity:").grid(row=1, column=0, sticky="w", pady=2)
hall_capacity_entry = ttk.Entry(hf, width=25)
hall_capacity_entry.grid(row=1, column=1, pady=2, padx=5)

btn_add_hall = ttk.Button(hf, text="Add Hall", command=add_hall)
btn_add_hall.grid(row=2, column=1, pady=19, sticky="e")


# =========================================================================
# NEW SECTION: DATABASE DATA MANAGEMENT (VIEW & DELETE CORES)
# =========================================================================
manage_frame = ttk.LabelFrame(main_frame, text=" Manage Registered Data (Select to Delete) ", padding="10")
manage_frame.pack(fill="x", pady=10)

# Student List Panel
student_panel = ttk.Frame(manage_frame)
student_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

student_tree = ttk.Treeview(student_panel, columns=("ID", "Roll", "Name", "Branch"), show="headings", height=4)
student_tree.heading("ID", text="ID")
student_tree.heading("Roll", text="Roll No")
student_tree.heading("Name", text="Name")
student_tree.heading("Branch", text="Branch")
student_tree.column("ID", width=40, anchor="center")
student_tree.column("Roll", width=80)
student_tree.column("Name", width=120)
student_tree.column("Branch", width=70)
student_tree.pack(fill="both", expand=True)

btn_del_student = ttk.Button(student_panel, text="❌ Delete Selected Student", command=delete_selected_student)
btn_del_student.pack(anchor="e", pady=5)

# Hall List Panel
hall_panel = ttk.Frame(manage_frame)
hall_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))

hall_tree = ttk.Treeview(hall_panel, columns=("ID", "Name", "Capacity"), show="headings", height=4)
hall_tree.heading("ID", text="ID")
hall_tree.heading("Name", text="Hall Name")
hall_tree.heading("Capacity", text="Capacity")
hall_tree.column("ID", width=40, anchor="center")
hall_tree.column("Name", width=150)
hall_tree.column("Capacity", width=80, anchor="center")
hall_tree.pack(fill="both", expand=True)

btn_del_hall = ttk.Button(hall_panel, text="❌ Delete Selected Hall", command=delete_selected_hall)
btn_del_hall.pack(anchor="e", pady=5)
# =========================================================================


# Control Button
btn_generate = ttk.Button(
    main_frame, 
    text="⚡ Generate Optimized Seating Arrangement ⚡", 
    command=generate_seating
)
btn_generate.pack(fill="x", pady=5)

# Output Box Frame
output_frame = ttk.LabelFrame(main_frame, text=" Allocation Output ", padding="10")
output_frame.pack(fill="both", expand=True)

scrollbar = ttk.Scrollbar(output_frame)
scrollbar.pack(side="right", fill="y")

output_text = tk.Text(
    output_frame, 
    font=("Consolas", 10), 
    yscrollcommand=scrollbar.set,
    bg="#fcfcfc"
)
output_text.pack(fill="both", expand=True)
scrollbar.config(command=output_text.yview)

# Initialize data visibility into grids on startup
refresh_management_tables()

root.mainloop()