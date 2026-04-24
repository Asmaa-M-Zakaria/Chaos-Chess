# =============================================================================
# chess_game.py  —  Chess Logic + Castling + En Passant + Swap Ability
# =============================================================================
# NOTATION
#   "wP" "wR" "wN" "wB" "wQ" "wK"  — white pieces
#   "bP" "bR" "bN" "bB" "bQ" "bK"  — black pieces
#   ""                               — empty square
#
# SPECIAL MECHANIC — SWAP ABILITY
#   Once per game, instead of making a normal move, a player may swap
#   the positions of any two of their own pieces.
#   This counts as their full turn.
#   Call:  game.make_swap(r1, c1, r2, c2)
# =============================================================================


class ChessGame:

    # ── Notation → pygame sprite name ────────────────────────────────────────
    _TO_UI = {
        "wP": "white_pawn",   "wR": "white_rook",   "wN": "white_knight",
        "wB": "white_bishop", "wQ": "white_queen",  "wK": "white_king",
        "bP": "black_pawn",   "bR": "black_rook",   "bN": "black_knight",
        "bB": "black_bishop", "bQ": "black_queen",  "bK": "black_king",
        "":   "",
    }

    # =========================================================================
    # INITIALISATION
    # =========================================================================

    def __init__(self):
        self.internal_board = self._starting_board()
        self.current_turn   = "w"
        self.game_over      = False
        self.winner         = None

        # ── En passant ───────────────────────────────────────────────────────
        self.en_passant_target = None

        # ── Castling rights ──────────────────────────────────────────────────
        self.castling_rights = {
            "w": {"kingside": True, "queenside": True},
            "b": {"kingside": True, "queenside": True},
        }

        # ── Swap ability ─────────────────────────────────────────────────────
        # Each player gets ONE swap per game.
        # False = still available,  True = already used.
        self.white_swap_used = False
        self.black_swap_used = False

    # =========================================================================
    # BOARD SETUP
    # =========================================================================

    @staticmethod
    def _starting_board():
        return [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],  # row 0 — black back rank
            ["bP","bP","bP","bP","bP","bP","bP","bP"],  # row 1
            ["",  "",  "",  "",  "",  "",  "",  "" ],
            ["",  "",  "",  "",  "",  "",  "",  "" ],
            ["",  "",  "",  "",  "",  "",  "",  "" ],
            ["",  "",  "",  "",  "",  "",  "",  "" ],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],  # row 6
            ["wR","wN","wB","wQ","wK","wB","wN","wR"],  # row 7 — white back rank
        ]

    # =========================================================================
    # PUBLIC PROPERTY
    # =========================================================================

    @property
    def board(self):
        """Board converted to pygame-friendly sprite names for drawing."""
        return [
            [self._TO_UI[sq] for sq in row]
            for row in self.internal_board
        ]

    # =========================================================================
    # PUBLIC API — NORMAL MOVE
    # =========================================================================

    def make_move(self, from_row, from_col, to_row, to_col):
        """
        Attempt to move the piece at (from_row, from_col) to (to_row, to_col).
        Returns dict: success, board, message, current_turn
        """
        if self.game_over:
            return self._result(False, f"Game over — {self.winner} won!")

        piece = self.internal_board[from_row][from_col]

        if not piece:
            return self._result(False, "No piece on that square.")

        if self._color(piece) != self.current_turn:
            who = "White" if self.current_turn == "w" else "Black"
            return self._result(False, f"It is {who}'s turn.")

        if (to_row, to_col) not in self._legal_moves(from_row, from_col):
            return self._result(False, "Illegal move.")

        # ── Execute ───────────────────────────────────────────────────────────
        mover_color = self._color(piece)
        captured    = self.internal_board[to_row][to_col]

        self.internal_board[to_row][to_col]     = piece
        self.internal_board[from_row][from_col] = ""

        # ── Castling — move the rook when king slides 2 squares ───────────────
        if piece[1] == "K" and abs(to_col - from_col) == 2:
            back_rank = 7 if mover_color == "w" else 0
            if to_col == 6:    # kingside
                self.internal_board[back_rank][5] = mover_color + "R"
                self.internal_board[back_rank][7] = ""
            elif to_col == 2:  # queenside
                self.internal_board[back_rank][3] = mover_color + "R"
                self.internal_board[back_rank][0] = ""

        # ── En passant capture — remove the skipped pawn ──────────────────────
        if piece[1] == "P" and self.en_passant_target == (to_row, to_col):
            self.internal_board[from_row][to_col] = ""

        # ── Update en-passant target for next move ────────────────────────────
        if piece[1] == "P" and abs(to_row - from_row) == 2:
            self.en_passant_target = ((from_row + to_row) // 2, to_col)
        else:
            self.en_passant_target = None

        # ── Update castling rights ────────────────────────────────────────────
        if piece == "wK":
            self.castling_rights["w"]["kingside"]  = False
            self.castling_rights["w"]["queenside"] = False
        elif piece == "bK":
            self.castling_rights["b"]["kingside"]  = False
            self.castling_rights["b"]["queenside"] = False
        elif piece == "wR":
            if from_col == 7: self.castling_rights["w"]["kingside"]  = False
            if from_col == 0: self.castling_rights["w"]["queenside"] = False
        elif piece == "bR":
            if from_col == 7: self.castling_rights["b"]["kingside"]  = False
            if from_col == 0: self.castling_rights["b"]["queenside"] = False

        # ── Pawn promotion → auto Queen ───────────────────────────────────────
        if piece == "wP" and to_row == 0:
            self.internal_board[to_row][to_col] = "wQ"
        elif piece == "bP" and to_row == 7:
            self.internal_board[to_row][to_col] = "bQ"

        # ── Win condition ─────────────────────────────────────────────────────
        message = "OK"
        if captured == "wK":
            self.game_over = True
            self.winner    = "b"
            message        = "Black wins!"
        elif captured == "bK":
            self.game_over = True
            self.winner    = "w"
            message        = "White wins!"
        else:
            self.current_turn = "b" if self.current_turn == "w" else "w"

        return self._result(True, message)

    # =========================================================================
    # PUBLIC API — SWAP ABILITY
    # =========================================================================

    def make_swap(self, r1, c1, r2, c2):
        """
        Swap the positions of the two pieces at (r1,c1) and (r2,c2).

        Rules
        -----
        • Both squares must contain pieces belonging to the current player.
        • The two squares must be different.
        • Each player can only use this ability ONCE per game.
        • Counts as the player's full turn — no move is also made.

        Returns dict: success, board, message, current_turn
        """
        if self.game_over:
            return self._result(False, f"Game over — {self.winner} won!")

        color = self.current_turn

        # Check swap hasn't been used already
        if color == "w" and self.white_swap_used:
            return self._result(False, "White already used their swap.")
        if color == "b" and self.black_swap_used:
            return self._result(False, "Black already used their swap.")

        # Both squares must be different
        if (r1, c1) == (r2, c2):
            return self._result(False, "Choose two different squares.")

        p1 = self.internal_board[r1][c1]
        p2 = self.internal_board[r2][c2]

        # Both squares must have the current player's pieces
        if not p1 or self._color(p1) != color:
            return self._result(False, "First square must have your own piece.")
        if not p2 or self._color(p2) != color:
            return self._result(False, "Second square must have your own piece.")

        # ── Execute the swap ──────────────────────────────────────────────────
        self.internal_board[r1][c1] = p2
        self.internal_board[r2][c2] = p1

        # Mark swap as used for this player
        if color == "w":
            self.white_swap_used = True
        else:
            self.black_swap_used = True

        # En passant window is lost when a swap is played
        self.en_passant_target = None

        # Switch turn
        self.current_turn = "b" if color == "w" else "w"

        who = "White" if color == "w" else "Black"
        return self._result(True, f"{who} used their swap!")

    # =========================================================================
    # HELPERS
    # =========================================================================

    def get_valid_moves_for_square(self, row, col):
        """Legal destinations for (row, col). Used by board.py for move hints."""
        piece = self.internal_board[row][col]
        if not piece or self._color(piece) != self.current_turn:
            return []
        return self._legal_moves(row, col)

    def reset(self):
        self.__init__()

    # =========================================================================
    # LEGAL MOVE GENERATION
    # =========================================================================

    def _legal_moves(self, row, col):
        piece = self.internal_board[row][col]
        if not piece:
            return []
        color = self._color(piece)
        kind  = piece[1]

        if kind == "P": return self._pawn_moves(row, col, color)
        if kind == "R": return self._rook_moves(row, col, color)
        if kind == "N": return self._knight_moves(row, col, color)
        if kind == "B": return self._bishop_moves(row, col, color)
        if kind == "Q": return self._rook_moves(row, col, color) + \
                               self._bishop_moves(row, col, color)
        if kind == "K": return self._king_moves(row, col, color)
        return []

    # =========================================================================
    # PIECE MOVEMENT RULES
    # =========================================================================

    def _pawn_moves(self, row, col, color):
        moves = []
        d, start = (-1, 6) if color == "w" else (1, 1)

        nr = row + d
        if self._in_bounds(nr, col) and self.internal_board[nr][col] == "":
            moves.append((nr, col))
            nr2 = row + 2 * d
            if row == start and self.internal_board[nr2][col] == "":
                moves.append((nr2, col))

        for dc in (-1, 1):
            r2, c2 = row + d, col + dc
            if self._in_bounds(r2, c2):
                t = self.internal_board[r2][c2]
                if t and self._color(t) != color:
                    moves.append((r2, c2))

        # En passant
        if self.en_passant_target:
            ep_r, ep_c = self.en_passant_target
            if ep_r == row + d and abs(ep_c - col) == 1:
                moves.append((ep_r, ep_c))

        return moves

    def _rook_moves(self, row, col, color):
        moves = []
        for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
            r, c = row + dr, col + dc
            while self._in_bounds(r, c):
                t = self.internal_board[r][c]
                if t == "":                         moves.append((r, c))
                elif self._color(t) != color:       moves.append((r, c)); break
                else:                               break
                r += dr; c += dc
        return moves

    def _knight_moves(self, row, col, color):
        moves = []
        for dr, dc in ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)):
            r, c = row + dr, col + dc
            if self._in_bounds(r, c) and self._color(self.internal_board[r][c]) != color:
                moves.append((r, c))
        return moves

    def _bishop_moves(self, row, col, color):
        moves = []
        for dr, dc in ((-1,-1),(-1,1),(1,-1),(1,1)):
            r, c = row + dr, col + dc
            while self._in_bounds(r, c):
                t = self.internal_board[r][c]
                if t == "":                         moves.append((r, c))
                elif self._color(t) != color:       moves.append((r, c)); break
                else:                               break
                r += dr; c += dc
        return moves

    def _king_moves(self, row, col, color):
        moves = []

        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if self._in_bounds(r, c) and self._color(self.internal_board[r][c]) != color:
                    moves.append((r, c))

        # Castling
        rights    = self.castling_rights[color]
        back_rank = 7 if color == "w" else 0

        if row == back_rank and col == 4:
            if rights["kingside"]:
                if (self.internal_board[back_rank][5] == "" and
                        self.internal_board[back_rank][6] == "" and
                        self.internal_board[back_rank][7] == color + "R"):
                    moves.append((back_rank, 6))
            if rights["queenside"]:
                if (self.internal_board[back_rank][3] == "" and
                        self.internal_board[back_rank][2] == "" and
                        self.internal_board[back_rank][1] == "" and
                        self.internal_board[back_rank][0] == color + "R"):
                    moves.append((back_rank, 2))

        return moves

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================

    def _result(self, success, message):
        return {
            "success":      success,
            "board":        self.board,
            "message":      message,
            "current_turn": self.current_turn,
        }

    @staticmethod
    def _color(piece):
        return piece[0] if piece else ""

    @staticmethod
    def _in_bounds(r, c):
        return 0 <= r < 8 and 0 <= c < 8
