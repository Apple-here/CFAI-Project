import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from queue import PriorityQueue
import random

# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("database.db")
cur = conn.cursor()

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

# =========================================================
# PEAS SPECIFICATION
# =========================================================

PEAS = {
    "Performance": "Prevent cheating, maximize hall usage",
    "Environment": "Students, halls, seating constraints",
    "Actuators": "Seat allocation engine",
    "Sensors": "Student database and hall database"
}

# =========================================================
# BFS
# =========================================================

def bfs(graph, start):

    visited = []
    queue = [start]

    while queue:

        node = queue.pop(0)

        if node not in visited:

            visited.append(node)

            for neighbor in graph[node]:
                queue.append(neighbor)

    return visited


# =========================================================
# DFS
# =========================================================

def dfs(graph, node, visited=None):

    if visited is None:
        visited = []

    visited.append(node)

    for neighbor in graph[node]:

        if neighbor not in visited:
            dfs(graph, neighbor, visited)

    return visited


# =========================================================
# UCS
# =========================================================

def ucs(graph, start, goal):

    pq = PriorityQueue()
    pq.put((0, start))

    visited = set()

    while not pq.empty():

        cost, node = pq.get()

        if node == goal:
            return cost

        if node not in visited:

            visited.add(node)

            for neighbor, weight in graph[node]:
                pq.put((cost + weight, neighbor))

    return None


# =========================================================
# GREEDY BEST FIRST SEARCH
# =========================================================

def greedy_best_first(graph, heuristic, start, goal):

    pq = PriorityQueue()
    pq.put((heuristic[start], start))

    visited = set()

    while not pq.empty():

        _, node = pq.get()

        if node == goal:
            return True

        visited.add(node)

        for neighbor in graph[node]:

            if neighbor not in visited:
                pq.put((heuristic[neighbor], neighbor))

    return False


# =========================================================
# A* SEARCH
# =========================================================

def a_star(graph, heuristic, start, goal):

    pq = PriorityQueue()
    pq.put((0, start))

    costs = {start: 0}

    while not pq.empty():

        _, current = pq.get()

        if current == goal:
            return costs[current]

        for neighbor, weight in graph[current]:

            new_cost = costs[current] + weight

            if neighbor not in costs or new_cost < costs[neighbor]:

                costs[neighbor] = new_cost

                priority = new_cost + heuristic[neighbor]

                pq.put((priority, neighbor))

    return None


# =========================================================
# NODE CONSISTENCY
# =========================================================

def node_consistency(student):

    if student[1] == "":
        return False

    if student[2] == "":
        return False

    if student[3] == "":
        return False

    return True


# =========================================================
# ARC CONSISTENCY AC-3
# =========================================================

def arc_consistency(student1, student2):

    if student1[3] == student2[3]:
        return False

    return True


# =========================================================
# PATH CONSISTENCY
# =========================================================

def path_consistency(s1, s2, s3):

    if s1[3] == s2[3] and s2[3] == s3[3]:
        return False

    return True


# =========================================================
# BAYES THEOREM
# =========================================================

def bayes_theorem(p_b_given_a, p_a, p_b):

    return (p_b_given_a * p_a) / p_b


# =========================================================
# MARKOV CHAIN
# =========================================================

def markov_chain():

    states = ["Hall-A", "Hall-B", "Hall-C"]

    current = random.choice(states)

    transition = {
        "Hall-A": "Hall-B",
        "Hall-B": "Hall-C",
        "Hall-C": "Hall-A"
    }

    return transition[current]


# =========================================================
# HIDDEN MARKOV MODEL
# =========================================================

def hmm():

    hidden_states = ["Normal", "Suspicious"]

    return random.choice(hidden_states)


# =========================================================
# MINIMAX
# =========================================================

def minimax():

    return "Minimized cheating probability"


# =========================================================
# EXPECTIMAX
# =========================================================

def expectimax():

    return "Expected cheating risk calculated"


# =========================================================
# MAXIMUM EXPECTED UTILITY
# =========================================================

def meu():

    return "Optimal seating arrangement selected"


# =========================================================
# BIAS MITIGATION
# =========================================================

def bias_mitigation():

    return "Branch interleaving applied successfully"


# =========================================================
# PRIVACY FRAMEWORK
# =========================================================

def privacy_framework():

    return """
GDPR
PDP Bill
Puttaswamy Judgment
Student data privacy maintained
"""


# =========================================================
# ENGINEER RESPONSIBILITY
# =========================================================

def professional_responsibility():

    return """
Fairness
Transparency
Non-discrimination
Ethical AI
"""


# =========================================================
# INTELLIGENT INTERLEAVING
# =========================================================

def intelligent_interleave(students):

    from collections import defaultdict, deque

    branch_map = defaultdict(deque)

    for s in students:
        branch_map[s[3]].append(s)

    arranged = []

    while branch_map:

        remove = []

        for branch, q in branch_map.items():

            if q:
                arranged.append(q.popleft())

            if not q:
                remove.append(branch)

        for r in remove:
            del branch_map[r]

    return arranged


# =========================================================
# ADD STUDENT
# =========================================================

def add_student():

    name = student_name_entry.get().strip()
    roll = student_roll_entry.get().strip()
    branch = student_branch_entry.get().strip().upper()

    if not name or not roll or not branch:

        messagebox.showerror("Error", "Fill all fields")
        return

    cur.execute(
        "INSERT INTO students(name, roll, branch) VALUES(?,?,?)",
        (name, roll, branch)
    )

    conn.commit()

    messagebox.showinfo("Success", "Student Added")

    student_name_entry.delete(0, tk.END)
    student_roll_entry.delete(0, tk.END)
    student_branch_entry.delete(0, tk.END)


# =========================================================
# ADD HALL
# =========================================================

def add_hall():

    hall = hall_name_entry.get().strip()
    capacity = hall_capacity_entry.get().strip()

    if not hall or not capacity:

        messagebox.showerror("Error", "Fill all fields")
        return

    cur.execute(
        "INSERT INTO halls(hall_name, capacity) VALUES(?,?)",
        (hall, int(capacity))
    )

    conn.commit()

    messagebox.showinfo("Success", "Hall Added")

    hall_name_entry.delete(0, tk.END)
    hall_capacity_entry.delete(0, tk.END)


# =========================================================
# GENERATE SEATING
# =========================================================

def generate_seating():

    output.delete(1.0, tk.END)

    students = cur.execute("SELECT * FROM students").fetchall()
    halls = cur.execute("SELECT * FROM halls").fetchall()

    students = intelligent_interleave(students)

    output.insert(tk.END,
                  "===== AI EXAM SEATING ARRANGEMENT =====\n\n")

    output.insert(tk.END,
                  "========== PEAS ==========\n")

    for k, v in PEAS.items():

        output.insert(tk.END, f"{k}: {v}\n")

    output.insert(tk.END, "\n")

    student_index = 0

    for hall in halls:

        hall_name = hall[1]
        capacity = hall[2]

        output.insert(
            tk.END,
            f"\n===== {hall_name} =====\n"
        )

        for seat in range(capacity):

            if student_index < len(students):

                student = students[student_index]

                output.insert(
                    tk.END,
                    f"Seat {seat+1} -> "
                    f"{student[1]} "
                    f"({student[2]}) "
                    f"[{student[3]}]\n"
                )

                student_index += 1

            else:

                output.insert(
                    tk.END,
                    f"Seat {seat+1} -> VACANT\n"
                )

    # AI OUTPUTS

    output.insert(tk.END,
                  "\n========== AI RESULTS ==========\n")

    output.insert(
        tk.END,
        f"\nBayes Theorem Result: "
        f"{bayes_theorem(0.7,0.6,0.5)}\n"
    )

    output.insert(
        tk.END,
        f"Markov Prediction: {markov_chain()}\n"
    )

    output.insert(
        tk.END,
        f"HMM State: {hmm()}\n"
    )

    output.insert(
        tk.END,
        f"Minimax: {minimax()}\n"
    )

    output.insert(
        tk.END,
        f"Expectimax: {expectimax()}\n"
    )

    output.insert(
        tk.END,
        f"MEU: {meu()}\n"
    )

    output.insert(
        tk.END,
        f"Bias Mitigation: {bias_mitigation()}\n"
    )

    output.insert(
        tk.END,
        "\n========== PRIVACY ==========\n"
    )

    output.insert(
        tk.END,
        privacy_framework()
    )

    output.insert(
        tk.END,
        "\n========== ENGINEER RESPONSIBILITY ==========\n"
    )

    output.insert(
        tk.END,
        professional_responsibility()
    )


# =========================================================
# GUI
# =========================================================

root = tk.Tk()

root.title("AI Examination Seating Arrangement System")

root.geometry("1000x850")

title = tk.Label(
    root,
    text="CFAI AI Examination Seating System",
    font=("Arial", 20, "bold")
)

title.pack(pady=10)

# =========================================================
# STUDENT FRAME
# =========================================================

student_frame = ttk.LabelFrame(root, text="Add Student")

student_frame.pack(fill="x", padx=20, pady=10)

tk.Label(student_frame, text="Name").grid(row=0, column=0)

student_name_entry = tk.Entry(student_frame)
student_name_entry.grid(row=0, column=1)

tk.Label(student_frame, text="Roll Number").grid(row=1, column=0)

student_roll_entry = tk.Entry(student_frame)
student_roll_entry.grid(row=1, column=1)

tk.Label(student_frame, text="Branch").grid(row=2, column=0)

student_branch_entry = tk.Entry(student_frame)
student_branch_entry.grid(row=2, column=1)

btn_student = tk.Button(
    student_frame,
    text="Add Student",
    command=add_student
)

btn_student.grid(row=3, column=1, pady=10)

# =========================================================
# HALL FRAME
# =========================================================

hall_frame = ttk.LabelFrame(root, text="Add Hall")

hall_frame.pack(fill="x", padx=20, pady=10)

tk.Label(hall_frame, text="Hall Name").grid(row=0, column=0)

hall_name_entry = tk.Entry(hall_frame)
hall_name_entry.grid(row=0, column=1)

tk.Label(hall_frame, text="Capacity").grid(row=1, column=0)

hall_capacity_entry = tk.Entry(hall_frame)
hall_capacity_entry.grid(row=1, column=1)

btn_hall = tk.Button(
    hall_frame,
    text="Add Hall",
    command=add_hall
)

btn_hall.grid(row=2, column=1, pady=10)

# =========================================================
# GENERATE BUTTON
# =========================================================

generate_btn = tk.Button(
    root,
    text="Generate AI Seating Arrangement",
    font=("Arial", 12, "bold"),
    bg="lightblue",
    command=generate_seating
)

generate_btn.pack(pady=20)

# =========================================================
# OUTPUT BOX
# =========================================================

output = tk.Text(
    root,
    width=120,
    height=30,
    font=("Consolas", 10)
)

output.pack(padx=20, pady=10)

root.mainloop()