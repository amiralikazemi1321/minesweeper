# Minesweeper

A small collection of Minesweeper implementations in Python:

- `minesweeper.py` — a simple command-line (CLI) version.
- `minesweeper_ui.py` — a basic GUI built with Tkinter.
- `minesweeper_pygame.py` — a more polished, animated version built with Pygame (neon-style visuals, particles, timer, difficulty selection).

This repository is intended for learning and experimentation. Each implementation demonstrates the core game logic (board generation, bomb placement, neighbor counts, and flood-fill reveal) and a different user interface.

---

## Features

- Three separate front-ends (CLI, Tkinter, Pygame) sharing the same Minesweeper rules.
- First-move safety in GUI versions (the first selected cell will never be a bomb, and Pygame keeps the immediate neighbors safe).
- Flood-fill reveal for empty cells (recursive or iterative revealing of neighboring empty cells).
- Pygame version includes animations, particle effects, difficulty buttons, timer, and automatic flagging on win.

---

## Requirements

- Python 3.10+ recommended.
- For the Pygame version: `pygame` (see `requirements.txt`).
- For the Tkinter version: `tkinter` is part of the standard library on most platforms, but on some Linux distributions you may need to install a separate package (for example `python3-tk` on Debian/Ubuntu).

`requirements.txt` in this repo contains the suggested dependency for the Pygame build.

---

## Installation

It is recommended to use a virtual environment:

```bash
python -m venv .venv
# Activate the environment:
# On Windows
.\.venv\Scripts\activate
# On macOS / Linux
source .venv/bin/activate

# Install dependencies (only required for Pygame version)
pip install -r requirements.txt
```

If you don't want to use a virtual environment, installing `pygame` globally will also work:

```bash
pip install pygame
```

---

## Usage

Run the version you want from the repository root.

CLI version (text):

```bash
python minesweeper.py
```

Tkinter GUI version:

```bash
python minesweeper_ui.py
```

Pygame version (neon visuals):

```bash
python minesweeper_pygame.py
```

Notes:
- The CLI version uses a 10x10 board with 10 bombs by default. Enter row and column numbers when prompted (0-based indices).
- The Tkinter and Pygame versions support left-click to reveal and right-click to toggle flags. The Pygame version also supports keyboard shortcuts (R to restart, ESC to quit) and difficulty selection.

---

## Controls

CLI
- Enter row and column numbers when prompted (e.g. `Row (0-9): 3` and `Column (0-9): 4`).

Tkinter
- Left-click: reveal cell
- Right-click: toggle flag (🚩)
- Restart button to start a new game

Pygame
- Left-click: reveal cell
- Right-click: toggle flag
- R: restart
- ESC: quit
- Click difficulty buttons (EASY, NORMAL, HARD) in the UI to change board size and bomb count

---

## Project structure

```
minesweeper/
├── minesweeper.py            # CLI implementation
├── minesweeper_ui.py         # Tkinter GUI implementation
├── minesweeper_pygame.py     # Pygame implementation (more advanced)
├── requirements.txt          # Suggested dependency for Pygame
├── README.md                 # This file
└── LICENSE
```

---

## Notes, limitations and suggestions

- CLI version:
  - Does not currently support flagging or an explicit win message. It is a compact, educational implementation of the core logic.
  - Uses recursion for flood-fill; for very large boards this could hit Python's recursion limit — consider converting to an iterative BFS if you need larger boards.

- Tkinter version:
  - Works cross-platform but on some Linux systems you may need to install `python3-tk` separately.
  - Right-click bindings may behave differently on some platforms; consider adding alternative bindings (Ctrl+click) for compatibility.

- Pygame version:
  - Recommended for the best visual experience; requires `pygame` and a display.
  - If running on a headless server, the Pygame UI will not work without a virtual display.
  - Consider adding sound effects, configurable particle counts, and a local high-score storage for a nicer user experience.

---

## How it works (brief)

1. The board is initialized with all zeros.
2. Random bomb placement is done until the required bomb count is reached.
3. For each non-bomb cell, the number of adjacent bombs is calculated and stored.
4. When the player reveals a cell, if the value is 0, a flood-fill reveals connected empty cells and their border numbers.
5. The game ends when a bomb is revealed (loss) or when all safe cells are revealed (win).

---

## Contributing

Contributions, bug reports and improvements are welcome. A few ideas if you'd like to contribute:

- Add flagging and win message to CLI version.
- Replace recursive reveal in CLI with iterative approach.
- Add screenshots/GIF demo in README.
- Add unit tests for the board generation and reveal logic.

If you'd like, open an issue or submit a PR with your changes.

---

## License

This project is licensed under the MIT License — see the `LICENSE` file for details.
