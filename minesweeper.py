import random
import os


SIZE = 10
BOMBS = 10


# =========================
# Create board
# =========================

board = [
    [0 for _ in range(SIZE)]
    for _ in range(SIZE)
]


# =========================
# Place bombs
# =========================

bomb_count = 0

while bomb_count < BOMBS:
    row = random.randrange(SIZE)
    col = random.randrange(SIZE)

    if board[row][col] != 9:
        board[row][col] = 9
        bomb_count += 1


# =========================
# Calculate numbers
# =========================

for row in range(SIZE):
    for col in range(SIZE):

        if board[row][col] == 9:
            continue

        count = 0

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:

                if dr == 0 and dc == 0:
                    continue

                neighbor_row = row + dr
                neighbor_col = col + dc

                if 0 <= neighbor_row < SIZE and 0 <= neighbor_col < SIZE:

                    if board[neighbor_row][neighbor_col] == 9:
                        count += 1

        board[row][col] = count


# =========================
# Player's board
# =========================

display = [
    ["■" for _ in range(SIZE)]
    for _ in range(SIZE)
]


# =========================
# Reveal function
# =========================

def reveal(row, col):

    if not (0 <= row < SIZE and 0 <= col < SIZE):
        return

    # Already revealed
    if display[row][col] != "■":
        return

    # Reveal this cell
    display[row][col] = str(board[row][col])

    # If it isn't empty, stop here
    if board[row][col] != 0:
        return

    # Reveal neighbors
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:

            if dr == 0 and dc == 0:
                continue

            reveal(row + dr, col + dc)


# =========================
# Game loop
# =========================

while True:

    os.system("cls" if os.name == "nt" else "clear")

    for row in display:
        print(" ".join(row))

    print()

    try:
        row = int(input("Row (0-9): "))
        col = int(input("Column (0-9): "))

    except ValueError:
        print("Please enter numbers.")
        input("Press Enter...")
        continue

    if not (0 <= row < SIZE and 0 <= col < SIZE):
        print("Invalid position.")
        input("Press Enter...")
        continue


    # =====================
    # Bomb
    # =====================

    if board[row][col] == 9:

        os.system("cls" if os.name == "nt" else "clear")

        print("💥 BOOM!")
        print("You lose!")

        # Show bombs
        for r in range(SIZE):
            for c in range(SIZE):
                if board[r][c] == 9:
                    display[r][c] = "💣"

        for r in display:
            print(" ".join(r))

        break


    # =====================
    # Safe cell
    # =====================

    reveal(row, col)
