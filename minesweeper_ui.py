import tkinter as tk
import random


SIZE = 10
BOMBS = 10


class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper")

        self.board = []
        self.buttons = []
        self.first_move = True
        self.game_over = False
        self.flags = 0
        self.revealed = 0

        self.create_ui()

    def create_ui(self):
        self.info = tk.Label(
            self.root,
            text=f"💣 Bombs: {BOMBS}"
        )
        self.info.pack(pady=5)

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        for row in range(SIZE):
            button_row = []

            for col in range(SIZE):
                button = tk.Button(
                    self.frame,
                    width=3,
                    height=1,
                    font=("Arial", 12, "bold")
                )

                button.grid(row=row, column=col)

                # Left click
                button.bind(
                    "<Button-1>",
                    lambda event, r=row, c=col:
                    self.left_click(r, c)
                )

                # Right click
                button.bind(
                    "<Button-3>",
                    lambda event, r=row, c=col:
                    self.right_click(r, c)
                )

                button_row.append(button)

            self.buttons.append(button_row)

        self.restart_button = tk.Button(
            self.root,
            text="Restart",
            command=self.restart
        )

        self.restart_button.pack(pady=8)

    def create_board(self, safe_row, safe_col):
        self.board = [
            [0 for _ in range(SIZE)]
            for _ in range(SIZE)
        ]

        bombs = 0

        while bombs < BOMBS:
            row = random.randrange(SIZE)
            col = random.randrange(SIZE)

            # First selected cell can never be a bomb
            if (row, col) == (safe_row, safe_col):
                continue

            if self.board[row][col] != 9:
                self.board[row][col] = 9
                bombs += 1

        # Calculate numbers
        for row in range(SIZE):
            for col in range(SIZE):

                if self.board[row][col] == 9:
                    continue

                count = 0

                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):

                        if dr == 0 and dc == 0:
                            continue

                        nr = row + dr
                        nc = col + dc

                        if 0 <= nr < SIZE and 0 <= nc < SIZE:
                            if self.board[nr][nc] == 9:
                                count += 1

                self.board[row][col] = count

    def left_click(self, row, col):

        if self.game_over:
            return

        button = self.buttons[row][col]

        # Don't open flagged cells
        if button["text"] == "🚩":
            return

        # First move
        if self.first_move:
            self.create_board(row, col)
            self.first_move = False

        # Bomb
        if self.board[row][col] == 9:
            self.lose()
            return

        self.reveal(row, col)

        if self.revealed == SIZE * SIZE - BOMBS:
            self.win()

    def reveal(self, row, col):

        if not (0 <= row < SIZE and 0 <= col < SIZE):
            return

        button = self.buttons[row][col]

        # Already opened
        if button["state"] == "disabled":
            return

        # Don't reveal flags
        if button["text"] == "🚩":
            return

        value = self.board[row][col]

        button.config(
            state="disabled",
            relief=tk.SUNKEN
        )

        self.revealed += 1

        if value != 0:
            button.config(text=str(value))
            return

        # Empty cell
        button.config(text="")

        # Reveal neighbors
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):

                if dr == 0 and dc == 0:
                    continue

                self.reveal(
                    row + dr,
                    col + dc
                )

    def right_click(self, row, col):

        if self.game_over:
            return

        button = self.buttons[row][col]

        if button["state"] == "disabled":
            return

        if button["text"] == "":
            button.config(text="🚩")
            self.flags += 1

        elif button["text"] == "🚩":
            button.config(text="")
            self.flags -= 1

        self.info.config(
            text=f"💣 Bombs: {BOMBS - self.flags}"
        )

    def lose(self):

        self.game_over = True

        # Show all bombs
        for row in range(SIZE):
            for col in range(SIZE):

                if self.board[row][col] == 9:
                    self.buttons[row][col].config(
                        text="💣"
                    )

        self.info.config(text="💥 You lost!")

    def win(self):

        self.game_over = True
        self.info.config(text="🏆 You won!")

    def restart(self):

        self.board = []
        self.first_move = True
        self.game_over = False
        self.flags = 0
        self.revealed = 0

        self.info.config(
            text=f"💣 Bombs: {BOMBS}"
        )

        for row in range(SIZE):
            for col in range(SIZE):

                self.buttons[row][col].config(
                    text="",
                    state="normal",
                    relief=tk.RAISED
                )


root = tk.Tk()

game = Minesweeper(root)

root.mainloop()