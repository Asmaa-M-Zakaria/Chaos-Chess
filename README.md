# ♟️ Chaos Chess — AI Chess Game

A fully functional chess game built with Python and Pygame, featuring complete chess rules, an AI opponent powered by **Minimax with Alpha-Beta Pruning**, **Hill Climbing**, and a unique **Swap Ability** mechanic.

> Course project — Artificial Intelligence, Computer Science Department

---

## 🎮 About the Game

Chaos Chess enhances classical chess by introducing a strategic extension — the **Swap Ability**. Once per game, each player can swap the positions of any two of their own pieces instead of making a normal move. This counts as their full turn.

The game supports both human vs human and human vs AI modes.

| Classic Chess | Chaos Chess |
|---|---|
| Standard movement only | Standard movement + Swap Ability |
| No special powers | One swap per player per game |
| Human vs Human only | Human vs Human or Human vs AI |
| Normal turn flow | Right-click to activate swap |

---

## 🤖 AI Algorithms

The AI plays as Black and uses the following layers, tried in order each turn:

### Layer 1 — Minimax with Alpha-Beta Pruning

The primary algorithm. Searches **3 levels deep** into all possible futures.

- **Maximising**: Black tries to maximise the board score
- **Minimising**: White tries to minimise the board score
- **Pruning**: Branches are cut when `beta <= alpha` — they can never affect the final decision

```
Black move → White response → Black response → evaluate
```

### Layer 2 — Heuristic Evaluation

Used at every leaf node to score the board without playing the full game:

```
score = sum(black piece values) - sum(white piece values)
```

| Piece | Value |
|---|---|
| Pawn | 1 |
| Knight / Bishop | 3 |
| Rook | 5 |
| Queen | 9 |
| King | 1000 |

Positive score = Black winning. Negative = White winning.

### Layer 3 — Hill Climbing

Activated only when Minimax fails. Evaluates all legal moves one step ahead and picks the move with the highest immediate score:

1. Generate all legal Black moves
2. Simulate each move on a copy of the board
3. Score each result using the heuristic
4. Return the move with the **highest score**

```
Minimax (primary) → stuck → Hill Climbing (best immediate score)
```

### Layer 4 — Swap Evaluation

Runs in parallel on every turn. Tries every possible combination of two Black pieces, scores each swap result, then compares against the best normal move:

- If `swap_score > normal_score + 1` → **use the swap**
- Otherwise → play the normal move

---

## 🧠 AI Agent Design

| Property | Value |
|---|---|
| Agent type | Goal-based agent |
| Observability | Fully observable |
| Environment | Deterministic, sequential, static, discrete |
| Performance measure | Win the game + preserve king safety + minimise piece loss + optimal swap timing |
| Sensors | Board state, current player turn, skill usage status, opponent moves |
| Actuators | Mouse — move pieces, activate swap ability, display screen — board updates |

---

## 📋 PEAS

**P — Performance Measure**
- Winning the game
- Preserving own king safety
- Minimizing unnecessary piece loss
- Optimal swap timing

**E — Environment**
- The chess board
- All pieces on the board
- The human player and the AI

**A — Actuators**
- **Mouse** — move pieces on the board, activate the one-time swap ability
- **Display screen** — showing moves and board updates

**S — Sensors**
- Board state (positions of all pieces)
- Current player turn
- Skill usage status (used / unused)
- Opponent moves

---

## 🌍 ODESDA

| Property | Value |
|---|---|
| **O** — Observation | Fully observable |
| **D** — Deterministic | Deterministic |
| **E** — Episodic | Sequential |
| **S** — Static | Static |
| **D** — Discrete | Discrete |
| **A** — Agent | Multi-agent (Competitive) |

---

## 🛠️ Installation

**Requirements**: Python 3.8+ and Pygame

```
pip install pygame
```

**Run the game:**

```
python board.py
```

---

## 🕹️ Controls

| Input | Action |
|---|---|
| Left-click (1st) | Select a piece — green dots show legal moves |
| Left-click (2nd) | Move the selected piece to that square |
| Right-click (1st) | Select first piece for swap — piece turns blue |
| Right-click (2nd) | Select second piece — swap executes |
| Left-click during swap | Cancel swap mode |
| Restart button | Reset game and start fresh |
| Menu button | Return to main menu |

> Each player can only use the Swap Ability **once** per game. Once used, it cannot be used again.

---

## 📁 Project Structure

```
chess-game/
│
├── board.py          # UI — Pygame window, drawing, mouse input
├── chess_game.py     # Game logic — rules, moves, swap ability
├── chess_ai.py       # AI — Minimax, Alpha-Beta, Hill Climbing
├── README.md
│
└── chessart/
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

**Key classes:**

- `ChessGame` — board representation, move validation, castling, en passant, swap ability
- `ChessAI` — Minimax + Alpha-Beta, Hill Climbing, heuristic evaluation, swap evaluation
- `board.py` — Pygame rendering, mouse input routing, sidebar, message log

---

## 🎨 Features

- Two game modes — Human vs Human and Human vs AI
- Full chess rules including castling and en passant
- Pawn auto-promotion to Queen on reaching the last rank
- One-time Swap Ability per player activated by right-click
- Green move-hint dots on all legal destination squares
- Sidebar showing turn indicator, swap status, and colour-coded message log
- Restart returns to a fresh game state immediately

