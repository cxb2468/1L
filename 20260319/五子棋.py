import pygame
import sys
import os
import json
import tkinter as tk
from tkinter import filedialog, colorchooser

# 初始化 Pygame
pygame.init()
WINDOW_SIZE = (960, 660)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("五子棋专业版2.0")
clock = pygame.time.Clock()


# ---------- 字体加载 ----------
def load_fonts_from_file():
    """尝试从文件加载方正黑体简体"""
    font_path = os.path.join(os.path.dirname(__file__), "方正黑体简体.TTF")
    if os.path.exists(font_path):
        try:
            font_24 = pygame.font.Font(font_path, 24)
            font_20 = pygame.font.Font(font_path, 20)
            font_18 = pygame.font.Font(font_path, 18)
            font_16 = pygame.font.Font(font_path, 16)
            font_14 = pygame.font.Font(font_path, 14)
            return font_24, font_20, font_18, font_16, font_14
        except Exception as e:
            print(f"字体文件加载失败: {e}")
    return None, None, None, None, None


# 尝试加载字体文件
FONT_24, FONT_20, FONT_18, FONT_16, FONT_14 = load_fonts_from_file()

if FONT_24 is not None:
    USE_CHINESE = True
else:
    # 字体文件加载失败，尝试使用系统字体
    def load_chinese_font(size):
        """尝试加载系统支持中文的字体，返回字体对象或None"""
        # 扩充的系统字体列表，覆盖 Windows、macOS、Linux 常见中文字体
        font_names = [
            'SimHei', 'Microsoft YaHei', 'SimSun',
            'PingFang SC', 'STHeiti', 'Arial Unicode MS',
            'WenQuanYi Zen Hei', 'Noto Sans CJK SC', 'Noto Sans CJK TC',
            'Droid Sans Fallback', 'LiHei Pro', 'Apple LiGothic',
            'STSong', 'NSimSun', 'FangSong', 'KaiTi', 'MingLiU',
        ]
        for name in font_names:
            try:
                font = pygame.font.SysFont(name, size)
                # 测试是否能渲染中文字符（这里用空字符串测试不会触发错误，但需要确保字体存在）
                # 更准确的测试：尝试渲染一个中文字符，如果报错则说明不支持
                font.render('中', True, (0, 0, 0))
                return font
            except:
                continue
        return None


    # 为不同字号尝试加载字体
    ch_font_24 = load_chinese_font(24)
    ch_font_20 = load_chinese_font(20)
    ch_font_18 = load_chinese_font(18)
    ch_font_16 = load_chinese_font(16)
    ch_font_14 = load_chinese_font(14)

    if ch_font_24 is not None:
        USE_CHINESE = True
        FONT_24 = ch_font_24
        FONT_20 = ch_font_20 or pygame.font.Font(None, 20)
        FONT_18 = ch_font_18 or pygame.font.Font(None, 18)
        FONT_16 = ch_font_16 or pygame.font.Font(None, 16)
        FONT_14 = ch_font_14 or pygame.font.Font(None, 14)
    else:
        # 没有任何中文字体可用，回退到默认字体（英文）
        USE_CHINESE = False
        FONT_24 = pygame.font.Font(None, 24)
        FONT_20 = pygame.font.Font(None, 20)
        FONT_18 = pygame.font.Font(None, 18)
        FONT_16 = pygame.font.Font(None, 16)
        FONT_14 = pygame.font.Font(None, 14)

# ---------- 颜色 ----------
BG_COLOR = (128, 0, 128)  # 窗口背景色
PANEL_COLOR = BG_COLOR  # 面板背景与窗口背景相同（无边框）
BOARD_COLOR = (240, 190, 120)
LINE_COLOR = (0, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
TEXT_COLOR = (220, 220, 220)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER = (100, 100, 100)
BUTTON_BORDER = (150, 150, 150)
ACTIVE_COLOR = (0, 150, 200)
GROUP_TITLE_COLOR = (180, 180, 180)

# ---------- 棋盘参数 ----------
BOARD_SIZE = 15
CELL_SIZE = 38
BOARD_LEFT = 60
BOARD_TOP = 60
PIECE_RADIUS = CELL_SIZE // 2 - 3

# 右侧面板
PANEL_WIDTH = 280
PANEL_LEFT = BOARD_LEFT + (BOARD_SIZE - 1) * CELL_SIZE + 50
PANEL_TOP = 60  # 将动态计算垂直居中
PANEL_BUTTON_WIDTH = 260
PANEL_BUTTON_HEIGHT = 35
PANEL_SPACING = 8
GROUP_SPACING = 15


# ---------- 游戏状态类 ----------
class Game:
    def __init__(self):
        self.mode = 'pve'
        self.difficulty = '中等'
        self.board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.turn = 1
        self.history = []
        self.winner = 0
        self.ai_thinking = False
        self.show_coords = True
        self.player1_color = (0, 0, 0)
        self.player2_color = (255, 255, 255)
        self.review_mode = False
        self.review_step = -1
        self.review_history = []

    def reset(self):
        self.board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.history.clear()
        self.turn = 1
        self.winner = 0
        self.review_mode = False
        self.review_step = -1
        self.review_history.clear()

    def place_piece(self, row, col):
        if self.board[row][col] != 0 or self.winner != 0 or self.review_mode:
            return False
        self.board[row][col] = self.turn
        self.history.append((row, col, self.turn))
        if self.check_win(row, col):
            self.winner = self.turn
        self.turn = 2 if self.turn == 1 else 1
        return True

    def undo(self):
        if not self.history or self.review_mode:
            return False
        row, col, player = self.history.pop()
        self.board[row][col] = 0
        self.winner = 0
        self.turn = player
        return True

    def check_win(self, row, col):
        player = self.board[row][col]
        dirs = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in dirs:
            count = 1
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            r, c = row - dr, col - dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            if count >= 5:
                return True
        return False

    # ---------- AI 函数 ----------
    def ai_move_easy(self):
        weights = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        dirs = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != 0:
                    continue
                score = 0
                for dr, dc in dirs:
                    count = 1
                    rr, cc = r + dr, c + dc
                    while 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE and self.board[rr][cc] == 2:
                        count += 1
                        rr += dr
                        cc += dc
                    rr, cc = r - dr, c - dc
                    while 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE and self.board[rr][cc] == 2:
                        count += 1
                        rr -= dr
                        cc -= dc
                    if count >= 5:
                        score += 10000
                    else:
                        score += count * count
                for dr, dc in dirs:
                    count = 1
                    rr, cc = r + dr, c + dc
                    while 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE and self.board[rr][cc] == 1:
                        count += 1
                        rr += dr
                        cc += dc
                    rr, cc = r - dr, c - dc
                    while 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE and self.board[rr][cc] == 1:
                        count += 1
                        rr -= dr
                        cc -= dc
                    if count >= 5:
                        score += 8000
                    else:
                        score += count * count * 0.8
                weights[r][c] = score
        max_score = -1
        best = None
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if weights[r][c] > max_score:
                    max_score = weights[r][c]
                    best = (r, c)
        return best

    def evaluate_move(self, r, c, color):
        if self.board[r][c] != 0:
            return 0
        score_map = {
            (5, True): 1000000, (5, False): 1000000,
            (4, True): 100000, (4, False): 10000,
            (3, True): 5000, (3, False): 1000,
            (2, True): 500, (2, False): 100,
            (1, True): 10, (1, False): 1,
        }
        total_score = 0
        dirs = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in dirs:
            cnt1 = 0
            rr, cc = r + dr, c + dc
            while 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE and self.board[rr][cc] == color:
                cnt1 += 1
                rr += dr
                cc += dc
            cnt2 = 0
            rr, cc = r - dr, c - dc
            while 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE and self.board[rr][cc] == color:
                cnt2 += 1
                rr -= dr
                cc -= dc
            total_len = 1 + cnt1 + cnt2
            left_open = True
            right_open = True
            rr, cc = r + (cnt1 + 1) * dr, c + (cnt1 + 1) * dc
            if 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE and self.board[rr][cc] != 0:
                right_open = False
            rr, cc = r - (cnt2 + 1) * dr, c - (cnt2 + 1) * dc
            if 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE and self.board[rr][cc] != 0:
                left_open = False
            is_live = left_open and right_open
            if total_len >= 5:
                return 1000000
            key = (min(total_len, 5), is_live)
            if key in score_map:
                total_score += score_map[key]
        return total_score

    def ai_move_medium(self, defense_weight=0.8):
        best_score = -1
        best_move = None
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != 0:
                    continue
                attack = self.evaluate_move(r, c, 2)
                defense = self.evaluate_move(r, c, 1)
                total = attack + defense * defense_weight
                if total > best_score:
                    best_score = total
                    best_move = (r, c)
        return best_move

    # ---------- 棋谱保存与加载 ----------
    def save_sgf(self, filename):
        data = {
            'board_size': BOARD_SIZE,
            'player1_color': self.player1_color,
            'player2_color': self.player2_color,
            'history': self.history,
            'mode': self.mode,
            'difficulty': self.difficulty
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True

    def load_sgf(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('board_size') != BOARD_SIZE:
                print("棋盘大小不匹配")
                return False
            self.reset()
            self.player1_color = tuple(data['player1_color'])
            self.player2_color = tuple(data['player2_color'])
            self.review_history = data['history']
            self.mode = data.get('mode', 'pve')
            self.difficulty = data.get('difficulty', '简单')
            self.review_mode = True
            self.review_step = -1
            self.board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
            self.turn = 1
            self.winner = 0
            return True
        except Exception as e:
            print(f"加载棋谱失败: {e}")
            return False

    def review_step_forward(self):
        if not self.review_mode:
            return
        if self.review_step + 1 < len(self.review_history):
            self.review_step += 1
            row, col, player = self.review_history[self.review_step]
            self.board[row][col] = player
            self.turn = 2 if player == 1 else 1
            if self.check_win(row, col):
                self.winner = player

    def review_step_backward(self):
        if not self.review_mode or self.review_step < 0:
            return
        row, col, player = self.review_history[self.review_step]
        self.board[row][col] = 0
        self.review_step -= 1
        if self.review_step >= 0:
            _, _, last_player = self.review_history[self.review_step]
            self.turn = 2 if last_player == 1 else 1
            self.winner = 0
        else:
            self.turn = 1
            self.winner = 0

    def exit_review(self):
        self.review_mode = False
        self.review_step = -1
        self.review_history.clear()
        self.reset()


# ---------- 绘制辅助函数 ----------
def draw_rect(surface, color, rect, border=0):
    if border:
        pygame.draw.rect(surface, color, rect, border)
    else:
        pygame.draw.rect(surface, color, rect)


def draw_button(surface, rect, text, font, hover=False, active=False):
    bg_color = ACTIVE_COLOR if active else (BUTTON_HOVER if hover else BUTTON_COLOR)
    draw_rect(surface, bg_color, rect)
    draw_rect(surface, BUTTON_BORDER, rect, 2)
    text_surf = font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)


def draw_group_title(surface, text, x, y):
    """绘制组标题"""
    surf = FONT_14.render(text, True, GROUP_TITLE_COLOR)
    surface.blit(surf, (x, y))


# ---------- 棋盘绘制 ----------
def draw_board(game):
    board_rect = pygame.Rect(BOARD_LEFT - 10, BOARD_TOP - 10,
                             (BOARD_SIZE - 1) * CELL_SIZE + 20, (BOARD_SIZE - 1) * CELL_SIZE + 20)
    draw_rect(screen, BOARD_COLOR, board_rect)
    for i in range(BOARD_SIZE):
        start = (BOARD_LEFT, BOARD_TOP + i * CELL_SIZE)
        end = (BOARD_LEFT + (BOARD_SIZE - 1) * CELL_SIZE, BOARD_TOP + i * CELL_SIZE)
        pygame.draw.line(screen, LINE_COLOR, start, end, 2)
        start = (BOARD_LEFT + i * CELL_SIZE, BOARD_TOP)
        end = (BOARD_LEFT + i * CELL_SIZE, BOARD_TOP + (BOARD_SIZE - 1) * CELL_SIZE)
        pygame.draw.line(screen, LINE_COLOR, start, end, 2)
    stars = [(7, 7), (3, 3), (11, 3), (3, 11), (11, 11)]
    for r, c in stars:
        x = BOARD_LEFT + c * CELL_SIZE
        y = BOARD_TOP + r * CELL_SIZE
        pygame.draw.circle(screen, LINE_COLOR, (x, y), 5)
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if game.board[r][c] == 0:
                continue
            x = BOARD_LEFT + c * CELL_SIZE
            y = BOARD_TOP + r * CELL_SIZE
            color = game.player1_color if game.board[r][c] == 1 else game.player2_color
            pygame.draw.circle(screen, color, (x, y), PIECE_RADIUS)
            pygame.draw.circle(screen, (100, 100, 100), (x, y), PIECE_RADIUS, 2)
    if game.show_coords:
        for i in range(BOARD_SIZE):
            text = FONT_14.render(str(i + 1), True, TEXT_COLOR)
            screen.blit(text, (BOARD_LEFT - 25, BOARD_TOP + i * CELL_SIZE - 10))
            text = FONT_14.render(chr(ord('A') + i), True, TEXT_COLOR)
            screen.blit(text, (BOARD_LEFT + i * CELL_SIZE - 8, BOARD_TOP + (BOARD_SIZE - 1) * CELL_SIZE + 12))
    if game.review_mode:
        review_text = f"复盘模式 第 {game.review_step + 1}/{len(game.review_history)} 步"
        if len(game.review_history) == 0:
            review_text = "复盘模式（无棋谱）"
        text_surf = FONT_18.render(review_text, True, (255, 200, 0))
        screen.blit(text_surf, (BOARD_LEFT, BOARD_TOP - 30))


# ---------- 计算面板垂直位置使内容居中 ----------
def calculate_panel_top(game):
    """计算面板顶部位置，使所有按钮组垂直居中"""
    y = 0
    y += 40  # 标题
    if game.review_mode:
        y += PANEL_BUTTON_HEIGHT + PANEL_SPACING  # 上一步/下一步行
        y += PANEL_BUTTON_HEIGHT + 20  # 退出复盘
    else:
        # 游戏模式组
        y += 15  # 组标题
        y += PANEL_BUTTON_HEIGHT + PANEL_SPACING
        # 难度组
        y += 15 + PANEL_BUTTON_HEIGHT + PANEL_SPACING
        # 状态显示
        y += 30
        # 控制组
        y += 15 + PANEL_BUTTON_HEIGHT + PANEL_SPACING
        # 颜色组（两行）
        y += 15 + 2 * (PANEL_BUTTON_HEIGHT + PANEL_SPACING)
        # 棋谱组
        y += 15 + PANEL_BUTTON_HEIGHT
        # 组间距
        y += 4 * GROUP_SPACING
    available_height = WINDOW_SIZE[1] - 120
    top_offset = max(60, 60 + (available_height - y) // 2)
    return top_offset


# ---------- 面板绘制 ----------
def draw_panel(game, mouse_pos):
    panel_top = calculate_panel_top(game)

    # 面板背景（与窗口背景相同，无边框）
    panel_rect = pygame.Rect(PANEL_LEFT - 10, panel_top - 10, PANEL_WIDTH, 620)
    draw_rect(screen, BG_COLOR, panel_rect)  # 使用窗口背景色，不绘制边框

    y = panel_top
    title = FONT_24.render("五子棋控制台", True, TEXT_COLOR)
    screen.blit(title, (PANEL_LEFT + (PANEL_WIDTH - title.get_width()) // 2, y))
    y += 40

    if game.review_mode:
        btn_w = (PANEL_WIDTH - 30) // 2
        btn_prev = pygame.Rect(PANEL_LEFT + 10, y, btn_w, PANEL_BUTTON_HEIGHT)
        btn_next = pygame.Rect(PANEL_LEFT + 20 + btn_w, y, btn_w, PANEL_BUTTON_HEIGHT)
        draw_button(screen, btn_prev, "上一步" if USE_CHINESE else "Prev", FONT_18,
                    hover=btn_prev.collidepoint(mouse_pos))
        draw_button(screen, btn_next, "下一步" if USE_CHINESE else "Next", FONT_18,
                    hover=btn_next.collidepoint(mouse_pos))
        y += PANEL_BUTTON_HEIGHT + PANEL_SPACING
        btn_exit = pygame.Rect(PANEL_LEFT + 10, y, PANEL_BUTTON_WIDTH, PANEL_BUTTON_HEIGHT)
        draw_button(screen, btn_exit, "退出复盘" if USE_CHINESE else "Exit Review", FONT_18,
                    hover=btn_exit.collidepoint(mouse_pos))
    else:
        # 1. 游戏模式组
        draw_group_title(screen, "游戏模式" if USE_CHINESE else "GAME MODE", PANEL_LEFT + 10, y)
        y += 15
        btn_w = (PANEL_WIDTH - 30) // 2
        btn1 = pygame.Rect(PANEL_LEFT + 10, y, btn_w, PANEL_BUTTON_HEIGHT)
        btn2 = pygame.Rect(PANEL_LEFT + 20 + btn_w, y, btn_w, PANEL_BUTTON_HEIGHT)
        draw_button(screen, btn1, "人机" if USE_CHINESE else "AI", FONT_18,
                    hover=btn1.collidepoint(mouse_pos), active=(game.mode == 'pve'))
        draw_button(screen, btn2, "人人" if USE_CHINESE else "2P", FONT_18,
                    hover=btn2.collidepoint(mouse_pos), active=(game.mode == 'pvp'))
        y += PANEL_BUTTON_HEIGHT + PANEL_SPACING + GROUP_SPACING

        # 2. 难度组
        draw_group_title(screen, "难度" if USE_CHINESE else "DIFFICULTY", PANEL_LEFT + 10, y)
        y += 15
        btn_w_small = 80
        spacing_small = 5
        total_width = 3 * btn_w_small + 2 * spacing_small
        start_x = PANEL_LEFT + (PANEL_WIDTH - total_width) // 2
        difficulties = ['简单', '中等', '困难'] if USE_CHINESE else ['Easy', 'Medium', 'Hard']
        for i, diff in enumerate(difficulties):
            btn = pygame.Rect(start_x + i * (btn_w_small + spacing_small), y, btn_w_small, PANEL_BUTTON_HEIGHT)
            active = (game.difficulty == diff or
                      (not USE_CHINESE and ((diff == 'Easy' and game.difficulty == '简单') or
                                            (diff == 'Medium' and game.difficulty == '中等') or
                                            (diff == 'Hard' and game.difficulty == '困难'))))
            draw_button(screen, btn, diff, FONT_16,
                        hover=btn.collidepoint(mouse_pos), active=active)
        y += PANEL_BUTTON_HEIGHT + PANEL_SPACING + GROUP_SPACING

        # 3. 状态显示
        if game.winner != 0:
            status = ("黑胜" if game.winner == 1 else "白胜") if USE_CHINESE else (
                "Black wins" if game.winner == 1 else "White wins")
        else:
            status = ("黑棋走" if game.turn == 1 else "白棋走") if USE_CHINESE else (
                "Black's turn" if game.turn == 1 else "White's turn")
        screen.blit(FONT_20.render(status, True, TEXT_COLOR), (PANEL_LEFT + 10, y))
        y += 40

        # 4. 控制组
        draw_group_title(screen, "控制" if USE_CHINESE else "CONTROL", PANEL_LEFT + 10, y)
        y += 15
        btn_w_func = 80
        spacing_func = 8
        total_func = 3 * btn_w_func + 2 * spacing_func
        start_x = PANEL_LEFT + (PANEL_WIDTH - total_func) // 2
        func_labels = []
        if USE_CHINESE:
            func_labels = [("重新开始", 'reset'), ("悔棋", 'undo'), ("坐标", 'toggle_coords')]
        else:
            func_labels = [("Restart", 'reset'), ("Undo", 'undo'), ("Coords", 'toggle_coords')]
        for i, (label, action) in enumerate(func_labels):
            btn = pygame.Rect(start_x + i * (btn_w_func + spacing_func), y, btn_w_func, PANEL_BUTTON_HEIGHT)
            draw_button(screen, btn, label, FONT_16, hover=btn.collidepoint(mouse_pos))
        y += PANEL_BUTTON_HEIGHT + PANEL_SPACING + GROUP_SPACING

        # 5. 颜色组
        draw_group_title(screen, "颜色" if USE_CHINESE else "COLOR", PANEL_LEFT + 10, y)
        y += 15
        btn_w_color = (PANEL_WIDTH - 30) // 2
        # 第一行
        btn_color1 = pygame.Rect(PANEL_LEFT + 10, y, btn_w_color, PANEL_BUTTON_HEIGHT)
        btn_color2 = pygame.Rect(PANEL_LEFT + 20 + btn_w_color, y, btn_w_color, PANEL_BUTTON_HEIGHT)
        draw_button(screen, btn_color1, "黑棋颜色" if USE_CHINESE else "Black", FONT_16,
                    hover=btn_color1.collidepoint(mouse_pos))
        draw_button(screen, btn_color2, "白棋颜色" if USE_CHINESE else "White", FONT_16,
                    hover=btn_color2.collidepoint(mouse_pos))
        y += PANEL_BUTTON_HEIGHT + PANEL_SPACING
        # 第二行
        btn_bg_board = pygame.Rect(PANEL_LEFT + 10, y, btn_w_color, PANEL_BUTTON_HEIGHT)
        btn_bg_window = pygame.Rect(PANEL_LEFT + 20 + btn_w_color, y, btn_w_color, PANEL_BUTTON_HEIGHT)
        draw_button(screen, btn_bg_board, "棋盘背景" if USE_CHINESE else "BoardBg", FONT_16,
                    hover=btn_bg_board.collidepoint(mouse_pos))
        draw_button(screen, btn_bg_window, "窗口背景" if USE_CHINESE else "WinBg", FONT_16,
                    hover=btn_bg_window.collidepoint(mouse_pos))
        y += PANEL_BUTTON_HEIGHT + PANEL_SPACING + GROUP_SPACING

        # 6. 棋谱组
        draw_group_title(screen, "棋谱" if USE_CHINESE else "GAME RECORD", PANEL_LEFT + 10, y)
        y += 15
        btn_save = pygame.Rect(PANEL_LEFT + 10, y, btn_w_color, PANEL_BUTTON_HEIGHT)
        btn_load = pygame.Rect(PANEL_LEFT + 20 + btn_w_color, y, btn_w_color, PANEL_BUTTON_HEIGHT)
        draw_button(screen, btn_save, "保存棋谱" if USE_CHINESE else "Save", FONT_16,
                    hover=btn_save.collidepoint(mouse_pos))
        draw_button(screen, btn_load, "加载棋谱" if USE_CHINESE else "Load", FONT_16,
                    hover=btn_load.collidepoint(mouse_pos))


# ---------- 坐标转换 ----------
def mouse_to_board(pos):
    x, y = pos
    if (BOARD_LEFT <= x <= BOARD_LEFT + (BOARD_SIZE - 1) * CELL_SIZE and
            BOARD_TOP <= y <= BOARD_TOP + (BOARD_SIZE - 1) * CELL_SIZE):
        col = round((x - BOARD_LEFT) / CELL_SIZE)
        row = round((y - BOARD_TOP) / CELL_SIZE)
        row = max(0, min(BOARD_SIZE - 1, row))
        col = max(0, min(BOARD_SIZE - 1, col))
        return row, col
    return None


# ---------- 颜色选择器 ----------
def choose_color(initial_color):
    root = tk.Tk()
    root.withdraw()
    color_code = colorchooser.askcolor(color=initial_color, title="选择颜色")
    root.destroy()
    if color_code[0]:
        return tuple(map(int, color_code[0]))
    return initial_color


# ---------- 文件选择器 ----------
def choose_save_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                             filetypes=[("JSON files", "*.json")])
    root.destroy()
    return file_path


def choose_load_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    root.destroy()
    return file_path


# ---------- 主循环 ----------
def main():
    global BG_COLOR, BOARD_COLOR
    game = Game()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        panel_top = calculate_panel_top(game)

        # 生成按钮区域列表
        def get_button_rects():
            rects = []
            y = panel_top + 40
            if game.review_mode:
                btn_w = (PANEL_WIDTH - 30) // 2
                rects.append(('review_prev', pygame.Rect(PANEL_LEFT + 10, y, btn_w, PANEL_BUTTON_HEIGHT)))
                rects.append(('review_next', pygame.Rect(PANEL_LEFT + 20 + btn_w, y, btn_w, PANEL_BUTTON_HEIGHT)))
                y += PANEL_BUTTON_HEIGHT + PANEL_SPACING
                rects.append(('review_exit', pygame.Rect(PANEL_LEFT + 10, y, PANEL_BUTTON_WIDTH, PANEL_BUTTON_HEIGHT)))
            else:
                # 模式组
                y += 15
                btn_w = (PANEL_WIDTH - 30) // 2
                rects.append(('mode_pve', pygame.Rect(PANEL_LEFT + 10, y, btn_w, PANEL_BUTTON_HEIGHT)))
                rects.append(('mode_pvp', pygame.Rect(PANEL_LEFT + 20 + btn_w, y, btn_w, PANEL_BUTTON_HEIGHT)))
                y += PANEL_BUTTON_HEIGHT + PANEL_SPACING + GROUP_SPACING

                # 难度组
                y += 15
                btn_w_small = 80
                spacing_small = 8
                total_width = 3 * btn_w_small + 2 * spacing_small
                start_x = PANEL_LEFT + (PANEL_WIDTH - total_width) // 2
                for i in range(3):
                    rects.append((f'diff_{i}', pygame.Rect(start_x + i * (btn_w_small + spacing_small), y, btn_w_small,
                                                           PANEL_BUTTON_HEIGHT)))
                y += PANEL_BUTTON_HEIGHT + PANEL_SPACING + GROUP_SPACING

                # 状态文字（无按钮）
                y += 40

                # 控制组
                y += 15
                btn_w_func = 70
                spacing_func = 2
                total_func = 3 * btn_w_func + 2 * spacing_func
                start_x = PANEL_LEFT + (PANEL_WIDTH - total_func) // 2
                actions = ['reset', 'undo', 'toggle_coords']
                for i, action in enumerate(actions):
                    rects.append((action, pygame.Rect(start_x + i * (btn_w_func + spacing_func), y, btn_w_func,
                                                      PANEL_BUTTON_HEIGHT)))
                y += PANEL_BUTTON_HEIGHT + PANEL_SPACING + GROUP_SPACING

                # 颜色组（两行）
                y += 15
                btn_w_color = (PANEL_WIDTH - 30) // 2
                rects.append(('color1', pygame.Rect(PANEL_LEFT + 10, y, btn_w_color, PANEL_BUTTON_HEIGHT)))
                rects.append(
                    ('color2', pygame.Rect(PANEL_LEFT + 20 + btn_w_color, y, btn_w_color, PANEL_BUTTON_HEIGHT)))
                y += PANEL_BUTTON_HEIGHT + PANEL_SPACING
                rects.append(('bg_board', pygame.Rect(PANEL_LEFT + 10, y, btn_w_color, PANEL_BUTTON_HEIGHT)))
                rects.append(
                    ('bg_window', pygame.Rect(PANEL_LEFT + 20 + btn_w_color, y, btn_w_color, PANEL_BUTTON_HEIGHT)))
                y += PANEL_BUTTON_HEIGHT + PANEL_SPACING + GROUP_SPACING

                # 棋谱组
                y += 15
                rects.append(('save', pygame.Rect(PANEL_LEFT + 10, y, btn_w_color, PANEL_BUTTON_HEIGHT)))
                rects.append(('load', pygame.Rect(PANEL_LEFT + 20 + btn_w_color, y, btn_w_color, PANEL_BUTTON_HEIGHT)))
            return rects

        button_rects = get_button_rects()

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                clicked = False
                for action, rect in button_rects:
                    if rect.collidepoint(pos):
                        clicked = True
                        if action == 'reset':
                            game.reset()
                        elif action == 'undo':
                            game.undo()
                        elif action == 'toggle_coords':
                            game.show_coords = not game.show_coords
                        elif action == 'mode_pve':
                            if game.mode != 'pve' and not game.review_mode:
                                game.mode = 'pve'
                                game.reset()
                        elif action == 'mode_pvp':
                            if game.mode != 'pvp' and not game.review_mode:
                                game.mode = 'pvp'
                                game.reset()
                        elif action.startswith('diff_'):
                            idx = int(action.split('_')[1])
                            if idx == 0:
                                game.difficulty = '简单' if USE_CHINESE else 'Easy'
                            elif idx == 1:
                                game.difficulty = '中等' if USE_CHINESE else 'Medium'
                            else:
                                game.difficulty = '困难' if USE_CHINESE else 'Hard'
                        elif action == 'color1':
                            new_color = choose_color(game.player1_color)
                            game.player1_color = new_color
                        elif action == 'color2':
                            new_color = choose_color(game.player2_color)
                            game.player2_color = new_color
                        elif action == 'bg_board':
                            new_color = choose_color(BOARD_COLOR)
                            BOARD_COLOR = new_color
                        elif action == 'bg_window':
                            new_color = choose_color(BG_COLOR)
                            BG_COLOR = new_color
                        elif action == 'save':
                            if not game.review_mode and game.history:
                                filename = choose_save_file()
                                if filename:
                                    game.save_sgf(filename)
                        elif action == 'load':
                            filename = choose_load_file()
                            if filename:
                                game.load_sgf(filename)
                        elif action == 'review_prev':
                            game.review_step_backward()
                        elif action == 'review_next':
                            game.review_step_forward()
                        elif action == 'review_exit':
                            game.exit_review()
                        break
                if not clicked and not game.review_mode:
                    rc = mouse_to_board(pos)
                    if rc:
                        row, col = rc
                        if game.mode == 'pve':
                            if game.turn == 1 and game.winner == 0:
                                game.place_piece(row, col)
                        else:
                            if game.winner == 0:
                                game.place_piece(row, col)

        # AI 下棋
        if not game.review_mode and game.mode == 'pve' and game.turn == 2 and game.winner == 0 and not game.ai_thinking:
            game.ai_thinking = True
            if game.difficulty in ['简单', 'Easy']:
                best = game.ai_move_easy()
            else:
                defense_weight = 0.8 if game.difficulty in ['中等', 'Medium'] else 0.9
                best = game.ai_move_medium(defense_weight=defense_weight)
            if best:
                row, col = best
                game.place_piece(row, col)
            game.ai_thinking = False

        screen.fill(BG_COLOR)
        draw_board(game)
        draw_panel(game, mouse_pos)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()