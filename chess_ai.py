# =============================================================================
# chess_ai.py  —  Chess AI  (plays as Black)
# =============================================================================
# ALGORITHMS
#   1. Move Generation  — all legal moves including en passant & castling
#   2. Heuristic Eval   — material: P=1  N/B=3  R=5  Q=9  K=1000
#   3. Hill Climbing    — greedy best immediate move
#   4. Genetic Algorithm— random population → evaluate → pick fittest
#   5. Minimax + Alpha-Beta (depth 3)  ← primary strategy
#
# SWAP ABILITY
#   The AI also considers using its one-time swap if swapping produces a
#   better board evaluation than any normal move.
#
# call:  ai.choose_move(game.internal_board,
#                       game.en_passant_target,
#                       game.castling_rights,
#                       game.black_swap_used)
# returns either:
#   ("move", fr, fc, tr, tc)   — a normal move
#   ("swap", r1, c1, r2, c2)   — use the swap ability
# =============================================================================

import random


class ChessAI:
    """Chess AI that plays as Black."""

    PIECE_VALUES = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 1000}
    DEPTH        = 3

    # =========================================================================
    # PUBLIC ENTRY POINT
    # =========================================================================

    def choose_move(self, board, en_passant_target=None,
                    castling_rights=None, black_swap_used=False):
        """
        Choose the best action for Black.

        Returns a tuple:
            ("move", fr, fc, tr, tc)  — play a normal chess move
            ("swap", r1, c1, r2, c2)  — use the one-time swap ability
        """
        if castling_rights is None:
            castling_rights = {"w": {"kingside": True, "queenside": True},
                               "b": {"kingside": True, "queenside": True}}

        # ── Best normal move via Minimax ───────────────────────────────────────
        best_normal = self._minimax_move(board, en_passant_target, castling_rights)
        if best_normal is None:
            best_normal = self._hill_climbing(board, en_passant_target, castling_rights)
        if best_normal is None:
            best_normal = self._random_move(board, en_passant_target, castling_rights)

        # ── Consider swap if it hasn't been used yet ───────────────────────────
        if not black_swap_used:
            best_swap = self._best_swap(board)
            if best_swap is not None:
                # Compare: evaluate board after swap vs after best normal move
                swap_score   = self.evaluate_board(
                    self._apply_swap(board, best_swap))
                normal_score = self.evaluate_board(
                    self._apply_move(board, best_normal, en_passant_target)) \
                    if best_normal else float("-inf")

                # Use swap only if it clearly improves the position
                if swap_score > normal_score + 1:
                    return ("swap",) + best_swap

        if best_normal:
            return ("move",) + best_normal

        return None   # no moves at all (shouldn't happen in a normal game)

    # =========================================================================
    # SWAP HELPERS
    # =========================================================================

    def _best_swap(self, board):
        """
        Find the best pair of Black's own pieces to swap.
        Tries every combination and returns the pair with the highest
        post-swap board evaluation.
        Returns (r1, c1, r2, c2) or None.
        """
        black_squares = [
            (r, c) for r in range(8) for c in range(8)
            if board[r][c] and board[r][c][0] == "b"
        ]

        best_score = float("-inf")
        best_pair  = None

        for i in range(len(black_squares)):
            for j in range(i + 1, len(black_squares)):
                r1, c1 = black_squares[i]
                r2, c2 = black_squares[j]
                sim    = self._apply_swap(board, (r1, c1, r2, c2))
                score  = self.evaluate_board(sim)
                if score > best_score:
                    best_score = score
                    best_pair  = (r1, c1, r2, c2)

        return best_pair

    def _apply_swap(self, board, swap):
        """Apply a swap to a copy of the board and return it."""
        new = [row[:] for row in board]
        r1, c1, r2, c2 = swap
        new[r1][c1], new[r2][c2] = new[r2][c2], new[r1][c1]
        return new

    # =========================================================================
    # MOVE GENERATION
    # =========================================================================

    def get_all_moves(self, board, color, en_passant_target=None,
                      castling_rights=None):
        """Every legal move for color. Returns [(fr,fc,tr,tc), ...]."""
        if castling_rights is None:
            castling_rights = {"w": {"kingside": False, "queenside": False},
                               "b": {"kingside": False, "queenside": False}}
        moves = []
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and piece[0] == color:
                    for (tr, tc) in self._piece_moves(
                            board, row, col, color,
                            en_passant_target, castling_rights):
                        moves.append((row, col, tr, tc))
        return moves

    def _piece_moves(self, board, row, col, color, ep, cr):
        kind = board[row][col][1]
        if kind == "P": return self._pawn(board, row, col, color, ep)
        if kind == "R": return self._rook(board, row, col, color)
        if kind == "N": return self._knight(board, row, col, color)
        if kind == "B": return self._bishop(board, row, col, color)
        if kind == "Q": return self._rook(board, row, col, color) + \
                               self._bishop(board, row, col, color)
        if kind == "K": return self._king(board, row, col, color, cr)
        return []

    # =========================================================================
    # EVALUATION
    # =========================================================================

    def evaluate_board(self, board):
        """Positive = Black advantage. Negative = White advantage."""
        score = 0
        for row in board:
            for piece in row:
                if piece:
                    val = self.PIECE_VALUES.get(piece[1], 0)
                    score += val if piece[0] == "b" else -val
        return score

    # =========================================================================
    # STRATEGIES
    # =========================================================================

    def _hill_climbing(self, board, ep, cr):
        moves = self.get_all_moves(board, "b", ep, cr)
        if not moves:
            return None
        return max(moves, key=lambda m: self.evaluate_board(
            self._apply_move(board, m, ep)))

    def _minimax_move(self, board, ep, cr):
        moves = self.get_all_moves(board, "b", ep, cr)
        if not moves:
            return None

        best_move  = None
        best_score = float("-inf")
        alpha, beta = float("-inf"), float("inf")

        for move in moves:
            nb, nep, ncr = self._apply_move_full(board, move, ep, cr)
            score = self._alpha_beta(nb, self.DEPTH - 1, alpha, beta,
                                     False, nep, ncr)
            if score > best_score:
                best_score = score
                best_move  = move
            alpha = max(alpha, best_score)

        return best_move

    def _alpha_beta(self, board, depth, alpha, beta, is_maximizing, ep, cr):
        if depth == 0:
            return self.evaluate_board(board)

        color = "b" if is_maximizing else "w"
        moves = self.get_all_moves(board, color, ep, cr)
        if not moves:
            return self.evaluate_board(board)

        if is_maximizing:
            best = float("-inf")
            for move in moves:
                nb, nep, ncr = self._apply_move_full(board, move, ep, cr)
                score = self._alpha_beta(nb, depth-1, alpha, beta, False, nep, ncr)
                best  = max(best, score)
                alpha = max(alpha, score)
                if beta <= alpha: break
            return best
        else:
            best = float("inf")
            for move in moves:
                nb, nep, ncr = self._apply_move_full(board, move, ep, cr)
                score = self._alpha_beta(nb, depth-1, alpha, beta, True, nep, ncr)
                best  = min(best, score)
                beta  = min(beta, score)
                if beta <= alpha: break
            return best

    def _random_move(self, board, ep, cr):
        moves = self.get_all_moves(board, "b", ep, cr)
        return random.choice(moves) if moves else None

    # =========================================================================
    # BOARD SIMULATION
    # =========================================================================

    def _apply_move(self, board, move, ep=None):
        new, _, _ = self._apply_move_full(
            board, move, ep,
            {"w": {"kingside": False, "queenside": False},
             "b": {"kingside": False, "queenside": False}}
        )
        return new

    def _apply_move_full(self, board, move, ep, cr):
        new    = [row[:] for row in board]
        new_cr = {"w": dict(cr["w"]), "b": dict(cr["b"])}
        fr, fc, tr, tc = move
        piece  = new[fr][fc]
        color  = piece[0]

        new[tr][tc] = piece
        new[fr][fc] = ""
        new_ep      = None

        if piece[1] == "K" and abs(tc - fc) == 2:
            back = 7 if color == "w" else 0
            if tc == 6:   new[back][5] = color + "R"; new[back][7] = ""
            elif tc == 2: new[back][3] = color + "R"; new[back][0] = ""

        if piece[1] == "P" and ep == (tr, tc):
            new[fr][tc] = ""

        if piece[1] == "P" and abs(tr - fr) == 2:
            new_ep = ((fr + tr) // 2, tc)

        if piece == "wP" and tr == 0: new[tr][tc] = "wQ"
        if piece == "bP" and tr == 7: new[tr][tc] = "bQ"

        if piece == "wK":
            new_cr["w"]["kingside"] = new_cr["w"]["queenside"] = False
        elif piece == "bK":
            new_cr["b"]["kingside"] = new_cr["b"]["queenside"] = False
        elif piece == "wR":
            if fc == 7: new_cr["w"]["kingside"]  = False
            if fc == 0: new_cr["w"]["queenside"] = False
        elif piece == "bR":
            if fc == 7: new_cr["b"]["kingside"]  = False
            if fc == 0: new_cr["b"]["queenside"] = False

        return new, new_ep, new_cr

    # =========================================================================
    # PIECE MOVEMENT
    # =========================================================================

    @staticmethod
    def _in_bounds(r, c): return 0 <= r < 8 and 0 <= c < 8

    @staticmethod
    def _color(piece): return piece[0] if piece else ""

    def _pawn(self, board, row, col, color, ep):
        moves = []
        d, start = (-1, 6) if color == "w" else (1, 1)
        nr = row + d
        if self._in_bounds(nr, col) and board[nr][col] == "":
            moves.append((nr, col))
            nr2 = row + 2 * d
            if row == start and board[nr2][col] == "":
                moves.append((nr2, col))
        for dc in (-1, 1):
            r2, c2 = row + d, col + dc
            if self._in_bounds(r2, c2):
                t = board[r2][c2]
                if t and self._color(t) != color:
                    moves.append((r2, c2))
        if ep:
            ep_r, ep_c = ep
            if ep_r == row + d and abs(ep_c - col) == 1:
                moves.append((ep_r, ep_c))
        return moves

    def _rook(self, board, row, col, color):
        moves = []
        for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
            r, c = row+dr, col+dc
            while self._in_bounds(r, c):
                t = board[r][c]
                if t == "":                   moves.append((r,c))
                elif self._color(t) != color: moves.append((r,c)); break
                else:                         break
                r+=dr; c+=dc
        return moves

    def _knight(self, board, row, col, color):
        moves = []
        for dr, dc in ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)):
            r, c = row+dr, col+dc
            if self._in_bounds(r,c) and self._color(board[r][c]) != color:
                moves.append((r,c))
        return moves

    def _bishop(self, board, row, col, color):
        moves = []
        for dr, dc in ((-1,-1),(-1,1),(1,-1),(1,1)):
            r, c = row+dr, col+dc
            while self._in_bounds(r, c):
                t = board[r][c]
                if t == "":                   moves.append((r,c))
                elif self._color(t) != color: moves.append((r,c)); break
                else:                         break
                r+=dr; c+=dc
        return moves

    def _king(self, board, row, col, color, cr):
        moves = []
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr==0 and dc==0: continue
                r, c = row+dr, col+dc
                if self._in_bounds(r,c) and self._color(board[r][c]) != color:
                    moves.append((r,c))
        back   = 7 if color == "w" else 0
        rights = cr[color]
        if row == back and col == 4:
            if rights["kingside"] and board[back][5]=="" and board[back][6]=="" \
                    and board[back][7]==color+"R":
                moves.append((back, 6))
            if rights["queenside"] and board[back][3]=="" and board[back][2]=="" \
                    and board[back][1]=="" and board[back][0]==color+"R":
                moves.append((back, 2))
        return moves
