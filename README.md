# ♟️ Chess Game with AI & Swap Ability

A fully functional chess game built with Python and Pygame featuring complete chess rules, an AI opponent powered by Minimax with Alpha-Beta pruning, and a unique **Swap Ability** mechanic that lets each player teleport two of their own pieces once per game.

---

## 📸 Preview

```
┌─────────────────────────────────┬──────────────┐
│                                 │ White's turn │
│      ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜          │              │
│      ♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟          │ Swap Ability │
│      . . . . . . . .           │ White: avail │
│      . . . . . . . .           │ Black: avail │
│      . . . . ♙ . . .           │              │
│      . . . . . . . .           │ Messages     │
│      ♙ ♙ ♙ ♙ . ♙ ♙ ♙          │ OK           │
│      ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖          │              │
│  [ Menu ]  [ Restart ]         │              │
└─────────────────────────────────┴──────────────┘
```

---

## 📁 Project Structure

```
chess-game/
│
├── board.py          # UI — Pygame window, drawing, mouse input
├── chess_game.py     # Game logic — rules, moves, swap ability
├── chess_ai.py       # AI — Minimax, Alpha-Beta, Hill Climbing
│
└── chessart/         # Assets folder (required)
    ├── background.jpg
    ├── white_pawn.png
    ├── white_rook.png
    ├── white_knight.png
    ├── white_bishop.png
    ├── white_queen.png
    ├── white_king.png
    ├── black_pawn.png
    ├── black_rook.png
    ├── black_knight.png
    ├── black_bishop.png
    ├── black_queen.png
    ├── black_king.png
    └── Red_Dot.png
```

---

## ⚙️ Requirements

- Python 3.8+
- Pygame

Install Pygame with:

```bash
pip install pygame
```

---

## ▶️ How to Run

```bash
python board.py
```

---

## 🎮 How to Play

### Game Modes
| Button | Mode |
|---|---|
| **2 Players** | Two humans play on the same screen |
| **Play vs AI** | You play White, AI plays Black |

### Making a Move
1. **Left-click** a piece to select it — green dots appear on legal squares
2. **Left-click** a destination square to move

### Swap Ability ♻️
Each player has **one swap per game** — swap the positions of any two of your own pieces instead of making a normal move. This counts as your full turn.

1. **Right-click** your first piece → it turns blue (swap mode activated)
2. **Right-click** your second piece → the swap executes
3. **Left-click** anywhere to cancel swap mode

> The swap ability is shown in the sidebar. Once used it cannot be used again.

### Special Moves
| Move | How to trigger |
|---|---|
| **Castling** | Move your king 2 squares toward a rook — the rook moves automatically |
| **En Passant** | Move your pawn diagonally to the square skipped by the opponent's double-advance pawn |
| **Pawn Promotion** | Move a pawn to the last rank — it auto-promotes to a Queen |

---

## 🤖 AI Algorithms

The AI plays as Black and uses the following algorithms in priority order:

### 1. Minimax + Alpha-Beta Pruning *(Primary)*
Builds a decision tree 3 levels deep. Black maximises the score, White minimises it. Alpha-Beta pruning cuts branches that cannot affect the final decision, making it significantly faster without losing quality.

```
Depth 3 → Black move → White response → Black response
```

### 2. Heuristic Evaluation
Scores every board state using material values:

| Piece | Value |
|---|---|
| Pawn | 1 |
| Knight / Bishop | 3 |
| Rook | 5 |
| Queen | 9 |
| King | 1000 |

Positive score = Black winning. Negative = White winning.

### 3. Hill Climbing *(Fallback)*
Evaluates all legal moves one step ahead and picks the one with the highest immediate score. Used if Minimax fails.

### 4. Genetic Algorithm *(Alternative)*
Samples 12 random legal moves (population), evaluates each one (fitness), and returns the best (selection). Inspired by natural selection.

### 5. Swap Evaluation
On every turn, the AI also evaluates the best possible swap. It uses the swap only if the resulting board score is **more than 1 point better** than the best normal move.

### Decision Flow

```
choose_move()
    │
    ├──► Minimax + Alpha-Beta   (primary)
    │         if fails ↓
    ├──► Hill Climbing           (fallback)
    │         if fails ↓
    ├──► Random Legal Move       (last resort)
    │
    └──► Swap Evaluation         (runs in parallel, overrides if better)
```

---

## 🧠 Architecture

The project is split into three files with strict separation of concerns:

| File | Responsibility |
|---|---|
| `board.py` | Draws the board, handles mouse input, manages scenes |
| `chess_game.py` | Enforces chess rules, validates moves, manages game state |
| `chess_ai.py` | Chooses Black's move using search algorithms |

The UI never directly modifies the board. It always calls `game.make_move()` or `game.make_swap()` and reads back `result["board"]` to redraw.

```
board.py  ──calls──►  chess_game.py  ──reads──►  chess_ai.py
   │                       │
   │◄── result["board"] ───┘
```

---

## 🔑 Key Functions

### chess_game.py
| Function | Description |
|---|---|
| `make_move(fr, fc, tr, tc)` | Validate and execute a normal move |
| `make_swap(r1, c1, r2, c2)` | Swap two of the current player's pieces |
| `get_valid_moves_for_square(row, col)` | Returns legal destinations for hint dots |
| `reset()` | Restart the game from scratch |

### chess_ai.py
| Function | Description |
|---|---|
| `choose_move(board, ep, cr, swap_used)` | Returns best action as `("move",...)` or `("swap",...)` |
| `evaluate_board(board)` | Scores the board by material count |
| `get_all_moves(board, color, ep, cr)` | Lists every legal move for a color |

---

## 🌍 Environment Properties (ODESA)

| Property | Value |
|---|---|
| Observable | Fully Observable |
| Deterministic | Deterministic |
| Episodic / Sequential | Sequential |
| Static / Dynamic | Static |
| Agents | Multi-Agent (Competitive) |

---

## 📋 PEAS

| | Description |
|---|---|
| **Performance** | Win the game + maximise material score + smart swap usage |
| **Environment** | 8×8 board, piece positions, castling rights, en passant, swap flag |
| **Actuators** | Move, Swap, Castle, En Passant, Promote |
| **Sensors** | Full board state, turn indicator, all game flags |

---

## 📌 Notes

- The king **cannot** be moved into check in a future version — check/checkmate detection is planned as an improvement
- Pawn promotion is **auto-queen** — manual piece selection is a planned improvement
- The AI thinks at **depth 3** — increasing to depth 4 will improve play quality but increase response time

---

## 👤 Author

Built as an academic AI project demonstrating game-playing agents, adversarial search, and local search algorithms using Python and Pygame.
