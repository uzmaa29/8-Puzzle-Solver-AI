import tkinter as tk
from tkinter import messagebox
import random
from queue import PriorityQueue
import threading

GOAL_STATE = ((1,2,3),(4,5,6),(7,8,0))

def manhattan(state):
    distance = 0
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            if value != 0:
                goal_x = (value - 1) // 3
                goal_y = (value - 1) % 3
                distance += abs(goal_x - i) + abs(goal_y - j)
    return distance

def get_neighbors(state):
    neighbors = []
    state_list = [list(row) for row in state]

    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                x, y = i, j

    directions = [(1,0), (-1,0), (0,1), (0,-1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            new_state = [row[:] for row in state_list]
            new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
            neighbors.append(tuple(tuple(row) for row in new_state))

    return neighbors

def a_star(start):
    pq = PriorityQueue()
    pq.put((0, start))
    came_from = {}
    g_score = {start: 0}

    while not pq.empty():
        _, current = pq.get()

        if current == GOAL_STATE:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current):
            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + manhattan(neighbor)
                pq.put((f_score, neighbor))

    return None

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver")
        self.root.configure(bg="#d8cce6")
        self.root.geometry("400x600")

        self.moves = 0
        self.state = [1,2,3,4,5,6,7,8,0]

        self.create_widgets()
        self.update_board()

    def create_widgets(self):
        title = tk.Label(self.root, text="✨ 8-Puzzle Solver",
                         font=("Arial", 20, "bold"),
                         bg="#d8cce6", fg="#5e17eb")
        title.pack(pady=10)

        subtitle = tk.Label(self.root, text="Slide tiles to solve the puzzle",
                            font=("Arial", 10),
                            bg="#d8cce6", fg="#7b2cbf")
        subtitle.pack()

        self.frame = tk.Frame(self.root, bg="#e6e1f0")
        self.frame.pack(pady=20)

        self.buttons = []
        for i in range(9):
            btn = tk.Button(self.frame, text="",
                            font=("Arial", 18, "bold"),
                            width=4, height=2,
                            bg="#8e44ad", fg="white",
                            activebackground="#6c3483",
                            command=lambda i=i: self.tile_click(i))
            btn.grid(row=i//3, column=i%3, padx=8, pady=8)
            self.buttons.append(btn)

        self.info_frame = tk.Frame(self.root, bg="#d8cce6")
        self.info_frame.pack()

        self.move_label = tk.Label(self.info_frame,
                                   text="Moves: 0",
                                   font=("Arial", 12),
                                   bg="#d8cce6",
                                   fg="#5e17eb")
        self.move_label.pack(side="left", padx=20)

        self.status_label = tk.Label(self.info_frame,
                                     text="",
                                     font=("Arial", 10, "bold"),
                                     bg="#d8cce6",
                                     fg="green")
        self.status_label.pack(side="right", padx=20)

        control_frame = tk.Frame(self.root, bg="#d8cce6")
        control_frame.pack(pady=15)

        tk.Button(control_frame, text="Shuffle",
                  command=self.shuffle,
                  bg="#b185db", fg="white",
                  width=8).grid(row=0, column=0, padx=10)

        tk.Button(control_frame, text="Solve",
                  command=self.solve_thread,
                  bg="#9d4edd", fg="white",
                  width=8).grid(row=0, column=1, padx=10)

        tk.Button(control_frame, text="Reset",
                  command=self.reset,
                  bg="#c77dff", fg="white",
                  width=8).grid(row=0, column=2, padx=10)

    def update_board(self):
        for i in range(9):
            value = self.state[i]
            if value == 0:
                self.buttons[i].config(text="", bg="#d3d3d3")
            else:
                self.buttons[i].config(text=str(value), bg="#8e44ad")

    def tile_click(self, index):
        empty_index = self.state.index(0)
        if self.is_adjacent(index, empty_index):
            self.state[empty_index], self.state[index] = self.state[index], self.state[empty_index]
            self.moves += 1
            self.move_label.config(text=f"Moves: {self.moves}")
            self.update_board()
            self.check_solved()

    def is_adjacent(self, i, j):
        return (abs(i-j) == 1 and i//3 == j//3) or abs(i-j) == 3

    def shuffle(self):
        random.shuffle(self.state)
        self.moves = 0
        self.move_label.config(text="Moves: 0")
        self.status_label.config(text="")
        self.update_board()

    def reset(self):
        self.state = [1,2,3,4,5,6,7,8,0]
        self.moves = 0
        self.move_label.config(text="Moves: 0")
        self.status_label.config(text="")
        self.update_board()

    def check_solved(self):
        if tuple(tuple(self.state[i:i+3]) for i in range(0,9,3)) == GOAL_STATE:
            self.status_label.config(text="✨ Solved!")

    def solve_thread(self):
        threading.Thread(target=self.solve).start()

    def solve(self):
        start = tuple(tuple(self.state[i:i+3]) for i in range(0,9,3))
        path = a_star(start)

        if path:
            for state in path:
                self.state = [num for row in state for num in row]
                self.update_board()
                self.root.update()
                self.root.after(400)
            self.status_label.config(text="✨ Solved!")

root = tk.Tk()
app = PuzzleApp(root)
root.mainloop()