import pygame
import sys
from chess_game import ChessGame
from chess_ai   import ChessAI

pygame.init()

# ══════════════════════════════════════════════════════════════
# LAYOUT CONSTANTS
# ══════════════════════════════════════════════════════════════
MENU_W, MENU_H = 640, 700

BORDER     = 50
BOARD_SIZE = 560
SQ_SIZE    = BOARD_SIZE // 8
BOARD_W    = BOARD_SIZE + BORDER * 2
BOARD_H    = BOARD_SIZE + BORDER * 2 + 60

SIDE_W = 210
WIN_W  = BOARD_W + SIDE_W

# RIGHT-CLICK on your own piece  → enter swap mode (piece becomes swap_first)
# RIGHT-CLICK again in swap mode → cancel swap
# LEFT-CLICK  in swap mode       → pick 2nd piece and execute swap

# ══════════════════════════════════════════════════════════════
# COLOURS
# ══════════════════════════════════════════════════════════════
BEIGE          = (235, 236, 208)
HIGHLIGHT      = (100, 200, 100)   # green  — normal selection
SWAP_HIGHLIGHT = (100, 160, 255)   # blue   — swap first-piece selection
BUTTON_COLOR   = ( 70, 130, 180)
WOOD_DARK      = ( 74,  46,  18)
WOOD_MID       = (101,  67,  33)
WOOD_LIGHT     = (119,  82,  42)
TEXT_COLOR     = (255, 255, 255)
SWAP_COLOR     = ( 80, 160, 255)
SIDE_BG        = ( 30,  20,  10)

MSG_COLORS = {
    "wins":    (255, 215,   0),
    "swap":    ( 80, 180, 255),
    "Illegal": (255,  80,  80),
    "turn":    (255, 220, 100),
    "No":      (255, 220, 100),
    "OK":      (180, 255, 180),
    "default": (220, 220, 220),
}

def msg_color(text):
    for keyword, color in MSG_COLORS.items():
        if keyword in text:
            return color
    return MSG_COLORS["default"]

# ══════════════════════════════════════════════════════════════
# FONTS
# ══════════════════════════════════════════════════════════════
title_font   = pygame.font.SysFont("Arial", 55)
button_font  = pygame.font.SysFont("Arial", 30)
font_label   = pygame.font.SysFont("Arial", 18, bold=True)
font_btn     = pygame.font.SysFont(None,    38)
font_side    = pygame.font.SysFont("Arial", 16, bold=True)
font_side_sm = pygame.font.SysFont("Arial", 14)

# ══════════════════════════════════════════════════════════════
# ASSETS
# ══════════════════════════════════════════════════════════════
screen = pygame.display.set_mode((MENU_W, MENU_H))
pygame.display.set_caption("Chess Game")

background = pygame.image.load("chessart/background.jpg")
background = pygame.transform.scale(background, (MENU_W, MENU_H))

pieces = {}
for name in [
    "white_pawn","white_rook","white_knight","white_bishop","white_queen","white_king",
    "black_pawn","black_rook","black_knight","black_bishop","black_queen","black_king",
]:
    img = pygame.image.load(f"chessart/{name}.png")
    pieces[name] = pygame.transform.scale(img, (SQ_SIZE, SQ_SIZE))

red_dot = pygame.image.load("chessart/Red_Dot.png")
red_dot = pygame.transform.scale(red_dot, (SQ_SIZE // 3, SQ_SIZE // 3))

# ── Menu buttons ──────────────────────────────────────────────
ai_button         = pygame.Rect( 40,             520, 200, 70)
two_player_button = pygame.Rect(400,             520, 200, 70)
exit_button       = pygame.Rect(MENU_W//2 - 100, 610, 200, 50)

# ── Board buttons (no swap button — swap is triggered by double-click) ───
restart_rect = pygame.Rect(BOARD_W//2 - 110, BOARD_H - 52, 220, 40)
back_rect    = pygame.Rect(10,               BOARD_H - 52, 100, 40)

# ══════════════════════════════════════════════════════════════
# GAME OBJECTS
# ══════════════════════════════════════════════════════════════
game = ChessGame()
ai   = ChessAI()

# ── Global state ──────────────────────────────────────────────
scene           = "menu"
mode            = None        # "AI" | "2P"
board           = game.board
selected_square = None
valid_hints     = []

# ── Swap mode ─────────────────────────────────────────────────
# Double-clicking your own piece enters swap mode with that piece
# as the first selection.  Then a single-click on another own piece
# completes the swap.
swap_mode  = False   # True while selecting the second piece for a swap
swap_first = None    # (row, col) of the first selected piece

message_log = []
MAX_LOG     = 12

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def resize_for_board():
    global screen
    screen = pygame.display.set_mode((WIN_W, BOARD_H))

def resize_for_menu():
    global screen
    screen = pygame.display.set_mode((MENU_W, MENU_H))

def _push_message(text):
    message_log.insert(0, text)
    del message_log[MAX_LOG:]

def _start_fresh():
    global board, selected_square, valid_hints, message_log
    global swap_mode, swap_first
    game.reset()
    board           = game.board
    selected_square = None
    valid_hints     = []
    swap_mode       = False
    swap_first      = None
    message_log     = []

def _cancel_swap():
    global swap_mode, swap_first, selected_square, valid_hints
    swap_mode       = False
    swap_first      = None
    selected_square = None
    valid_hints     = []

# ══════════════════════════════════════════════════════════════
# DRAW — menu
# ══════════════════════════════════════════════════════════════

def draw_text(text, font, color, x, y):
    surf = font.render(text, True, color)
    screen.blit(surf, surf.get_rect(center=(x, y)))

def draw_menu_button(rect, text):
    hover = WOOD_LIGHT if rect.collidepoint(pygame.mouse.get_pos()) else WOOD_MID
    pygame.draw.rect(screen, hover,     rect, border_radius=15)
    pygame.draw.rect(screen, WOOD_DARK, rect, width=3, border_radius=15)
    draw_text(text, button_font, TEXT_COLOR, rect.centerx, rect.centery)

def draw_menu():
    screen.blit(background, (0, 0))
    draw_text("CHESS GAME", title_font, TEXT_COLOR, MENU_W//2, 150)
    draw_menu_button(ai_button,         "Play vs AI")
    draw_menu_button(two_player_button, "2 Players")
    draw_menu_button(exit_button,       "Exit")

# ══════════════════════════════════════════════════════════════
# DRAW — board area
# ══════════════════════════════════════════════════════════════

def draw_wood_frame():
    pygame.draw.rect(screen, WOOD_DARK,  (0, 0, BOARD_W, BOARD_H - 60))
    pygame.draw.rect(screen, WOOD_MID,   pygame.Rect(8, 8, BOARD_W-16, BOARD_H-76))
    pygame.draw.rect(screen, WOOD_LIGHT, pygame.Rect(BORDER-6, BORDER-6, BOARD_SIZE+12, BOARD_SIZE+12), 3)
    for cx, cy in [(8,8),(BOARD_W-24,8),(8,BOARD_H-76),(BOARD_W-24,BOARD_H-76)]:
        pygame.draw.rect(screen, WOOD_DARK, (cx, cy, 16, 16), border_radius=3)

def draw_labels():
    for i, letter in enumerate("ABCDEFGH"):
        x = BORDER + i * SQ_SIZE + SQ_SIZE // 2
        surf = font_label.render(letter, True, BEIGE)
        screen.blit(surf, surf.get_rect(center=(x, BORDER // 2)))
        screen.blit(surf, surf.get_rect(center=(x, BORDER + BOARD_SIZE + BORDER // 2)))
    for i, num in enumerate(["8","7","6","5","4","3","2","1"]):
        y = BORDER + i * SQ_SIZE + SQ_SIZE // 2
        surf = font_label.render(num, True, BEIGE)
        screen.blit(surf, surf.get_rect(center=(BORDER // 2, y)))
        screen.blit(surf, surf.get_rect(center=(BORDER + BOARD_SIZE + BORDER // 2, y)))

def draw_squares():
    for row in range(8):
        for col in range(8):
            color = BEIGE if (row + col) % 2 == 0 else WOOD_DARK
            rect  = (BORDER + col*SQ_SIZE, BORDER + row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(screen, color, rect)

            # Normal move selection — green border
            if not swap_mode and selected_square == (row, col):
                pygame.draw.rect(screen, HIGHLIGHT, rect, 5)

            # Swap mode first-piece selection — blue border
            if swap_mode and swap_first == (row, col):
                pygame.draw.rect(screen, SWAP_HIGHLIGHT, rect, 5)

def draw_pieces():
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                screen.blit(pieces[piece],
                            (BORDER + col*SQ_SIZE, BORDER + row*SQ_SIZE))

def draw_move_hints():
    for (row, col) in valid_hints:
        cx = BORDER + col*SQ_SIZE + SQ_SIZE//2 - red_dot.get_width()//2
        cy = BORDER + row*SQ_SIZE + SQ_SIZE//2 - red_dot.get_height()//2
        screen.blit(red_dot, (cx, cy))

def draw_board_buttons():
    # Restart
    pygame.draw.rect(screen, BUTTON_COLOR, restart_rect, border_radius=8)
    lbl = font_btn.render("Restart", True, TEXT_COLOR)
    screen.blit(lbl, lbl.get_rect(center=restart_rect.center))
    # Menu
    pygame.draw.rect(screen, WOOD_MID, back_rect, border_radius=8)
    lbl = font_btn.render("Menu", True, TEXT_COLOR)
    screen.blit(lbl, lbl.get_rect(center=back_rect.center))

# ══════════════════════════════════════════════════════════════
# DRAW — sidebar
# ══════════════════════════════════════════════════════════════

def draw_sidebar():
    sx, sw, sh = BOARD_W, SIDE_W, BOARD_H
    pad = 12
    y   = 18

    pygame.draw.rect(screen, SIDE_BG, (sx, 0, sw, sh))
    pygame.draw.line(screen, WOOD_MID, (sx, 0), (sx, sh), 2)

    # ── Turn / mode indicator ─────────────────────────────────
    if game.game_over:
        turn_str, turn_color = "Game Over", MSG_COLORS["wins"]
    elif swap_mode:
        who = "White" if game.current_turn == "w" else "Black"
        turn_str   = f"{who}: pick 2nd piece"
        turn_color = SWAP_COLOR
    elif game.current_turn == "w":
        turn_str, turn_color = "White's turn", (240, 240, 240)
    else:
        turn_str, turn_color = "Black's turn", (160, 160, 255)

    surf = font_side.render(turn_str, True, turn_color)
    screen.blit(surf, (sx + pad, y))
    y += surf.get_height() + 6
    pygame.draw.line(screen, WOOD_MID, (sx+pad, y), (sx+sw-pad, y), 1)
    y += 10

    # ── Swap ability status ───────────────────────────────────
    surf = font_side.render("Swap Ability", True, SWAP_COLOR)
    screen.blit(surf, (sx + pad, y))
    y += surf.get_height() + 4

    for label, used in [("White", game.white_swap_used),
                        ("Black", game.black_swap_used)]:
        txt   = f"{label}: {'used' if used else 'available'}"
        color = (160, 160, 160) if used else (130, 210, 255)
        surf  = font_side_sm.render(txt, True, color)
        screen.blit(surf, (sx + pad, y))
        y += surf.get_height() + 3

    y += 5
    pygame.draw.line(screen, WOOD_MID, (sx+pad, y), (sx+sw-pad, y), 1)
    y += 10

    # ── Contextual swap instruction ───────────────────────────
    current_swap_used = (game.white_swap_used if game.current_turn == "w"
                         else game.black_swap_used)
    if swap_mode:
        hint = "Right-click 2nd piece  |  Left-click to cancel"
        color = SWAP_COLOR
    elif not current_swap_used and not game.game_over:
        hint = "Right-click a piece to swap"
        color = (160, 200, 255)
    else:
        hint = ""
        color = TEXT_COLOR

    if hint:
        # word-wrap the hint
        words, line = hint.split(), ""
        for word in words:
            test = line + (" " if line else "") + word
            if font_side_sm.size(test)[0] > sw - pad * 2:
                s = font_side_sm.render(line, True, color)
                screen.blit(s, (sx + pad, y)); y += s.get_height() + 2
                line = word
            else:
                line = test
        if line:
            s = font_side_sm.render(line, True, color)
            screen.blit(s, (sx + pad, y)); y += s.get_height() + 8
        pygame.draw.line(screen, WOOD_MID, (sx+pad, y), (sx+sw-pad, y), 1)
        y += 10

    # ── Message log ───────────────────────────────────────────
    surf = font_side.render("Messages", True, (200, 200, 200))
    screen.blit(surf, (sx + pad, y))
    y += surf.get_height() + 6

    for msg in message_log:
        color = msg_color(msg)
        words, line = msg.split(), ""
        for word in words:
            test = line + (" " if line else "") + word
            if font_side_sm.size(test)[0] > sw - pad * 2:
                s = font_side_sm.render(line, True, color)
                screen.blit(s, (sx + pad, y)); y += s.get_height() + 2
                line = word
            else:
                line = test
        if line:
            s = font_side_sm.render(line, True, color)
            screen.blit(s, (sx + pad, y)); y += s.get_height() + 4
        if y > sh - 20:
            break

# ══════════════════════════════════════════════════════════════
# CLICK HANDLERS
# ══════════════════════════════════════════════════════════════

def handle_menu_click(pos):
    global scene, mode
    if ai_button.collidepoint(pos):
        mode = "AI"; _start_fresh(); scene = "board"; resize_for_board()
    elif two_player_button.collidepoint(pos):
        mode = "2P"; _start_fresh(); scene = "board"; resize_for_board()
    elif exit_button.collidepoint(pos):
        pygame.quit(); sys.exit()

def handle_board_click(pos, is_right=False):
    """
    Routes every click on the board area.

    RIGHT-CLICK your own piece  → enter swap mode (piece becomes swap_first)
    While in swap mode:
        LEFT-CLICK  another own piece → execute swap
        RIGHT-CLICK anywhere          → cancel swap mode
    Outside swap mode:
        Normal two-click move flow (left-click only).
    """
    global board, selected_square, valid_hints, scene

    x, y = pos

    # ── Fixed buttons (left-click only) ───────────────────────
    if not is_right:
        if restart_rect.collidepoint(x, y):
            _start_fresh(); _push_message("Game restarted"); return
        if back_rect.collidepoint(x, y):
            _start_fresh(); scene = "menu"; resize_for_menu(); return

    # Ignore sidebar
    if x >= BOARD_W:
        return

    # ── Convert pixel → grid square ───────────────────────────
    bx, by = x - BORDER, y - BORDER
    if not (0 <= bx < BOARD_SIZE and 0 <= by < BOARD_SIZE):
        return

    clicked = (by // SQ_SIZE, bx // SQ_SIZE)

    if swap_mode:
        _handle_click_in_swap_mode(clicked, is_right)
    else:
        _handle_click_in_normal_mode(clicked, is_right)

# ── Normal mode ───────────────────────────────────────────────

def _handle_click_in_normal_mode(clicked, is_right):
    """
    Right-click on own piece → enter swap mode with that piece pre-selected.
    Left-click               → standard select / move flow.
    """
    global board, selected_square, valid_hints, swap_mode, swap_first

    row, col = clicked
    piece    = game.internal_board[row][col]
    color    = game.current_turn

    # ── Right-click: enter swap mode ──────────────────────────
    if is_right:
        current_swap_used = (game.white_swap_used if color == "w"
                             else game.black_swap_used)
        if current_swap_used:
            _push_message("Swap already used!")
            return
        if not piece or piece[0] != color:
            _push_message("Right-click one of your own pieces to swap")
            return

        swap_mode       = True
        swap_first      = (row, col)
        selected_square = None
        valid_hints     = []
        who = "White" if color == "w" else "Black"
        _push_message(f"{who}: right-click the 2nd piece to swap with")
        return

    # ── Left-click: normal two-click move flow ─────────────────
    if selected_square is None:
        selected_square = clicked
        valid_hints     = game.get_valid_moves_for_square(*clicked)
    else:
        fr, fc = selected_square
        tr, tc = clicked

        result = game.make_move(fr, fc, tr, tc)
        board  = result["board"]

        if result["message"] != "OK":
            _push_message(result["message"])

        if result["success"]:
            selected_square = None
            valid_hints     = []
            if mode == "AI" and not game.game_over and game.current_turn == "b":
                _do_ai_move()
        else:
            selected_square = clicked
            valid_hints     = game.get_valid_moves_for_square(*clicked)

# ── Swap mode ─────────────────────────────────────────────────

def _handle_click_in_swap_mode(clicked, is_right):
    """
    While in swap mode:
      Right-click own piece → complete the swap.
      Left-click anywhere   → cancel swap mode.
    """
    global board, swap_mode, swap_first

    # Left-click cancels swap mode
    if not is_right:
        _cancel_swap()
        _push_message("Swap cancelled")
        return

    # Right-click: pick the second piece and execute
    row, col = clicked
    piece    = game.internal_board[row][col]
    color    = game.current_turn

    if not piece or piece[0] != color:
        _push_message("Right-click one of your own pieces as the 2nd swap target")
        return

    r1, c1 = swap_first
    r2, c2 = row, col

    if (r1, c1) == (r2, c2):
        _push_message("Pick a different piece — can't swap with itself")
        return

    result = game.make_swap(r1, c1, r2, c2)
    board  = result["board"]
    _push_message(result["message"])

    swap_mode  = False
    swap_first = None

    if mode == "AI" and not game.game_over and game.current_turn == "b":
        _do_ai_move()

# ── AI ────────────────────────────────────────────────────────

def _do_ai_move():
    global board
    action = ai.choose_move(
        game.internal_board,
        game.en_passant_target,
        game.castling_rights,
        game.black_swap_used,
    )
    if action is None:
        return
    if action[0] == "swap":
        _, r1, c1, r2, c2 = action
        result = game.make_swap(r1, c1, r2, c2)
    else:
        _, fr, fc, tr, tc = action
        result = game.make_move(fr, fc, tr, tc)
    board = result["board"]
    if result["message"] != "OK":
        _push_message(f"AI: {result['message']}")

# ══════════════════════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════════════════════

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if scene == "menu":
                if event.button == 1:          # left-click only on menu
                    handle_menu_click(event.pos)
            else:
                if event.button in (1, 3):     # left or right click on board
                    handle_board_click(event.pos, is_right=(event.button == 3))

    if scene == "menu":
        draw_menu()
    else:
        screen.fill(WOOD_DARK)
        draw_wood_frame()
        draw_labels()
        draw_squares()
        draw_pieces()
        draw_move_hints()
        draw_board_buttons()
        draw_sidebar()

    pygame.display.update()
    clock.tick(60)
