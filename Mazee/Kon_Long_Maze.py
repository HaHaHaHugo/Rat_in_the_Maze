import pygame
import random
import sys
from collections import deque
import os

# --- ตั้งค่าเริ่มต้น ---
WIDTH, HEIGHT = 600, 650  # เพิ่มความสูงไว้สำหรับแสดง UI (เวลา, โหมด)
MAZE_SIZE = 600
COLS, ROWS = 30, 30
CELL_SIZE = MAZE_SIZE // COLS

# สีต่างๆ
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (50, 50, 50)
PATH_COLOR = (150, 255, 150)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("30x30 Maze - Mouse Edition")
font = pygame.font.SysFont("tahoma", 18, bold=True)
large_font = pygame.font.SysFont("tahoma", 36, bold=True)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# โหลดรูปภาพหนู (เตรียมไฟล์รูปภาพ mouse_up.png, mouse_down.png, mouse_left.png, mouse_right.png ไว้ในโฟลเดอร์เดียวกับโค้ด)
try:
    # ใช้ os.path.join เพื่อเชื่อมที่อยู่โฟลเดอร์เข้ากับชื่อไฟล์รูป
    mouse_up = pygame.image.load(os.path.join(BASE_DIR, "mouse_up.png"))
    mouse_down = pygame.image.load(os.path.join(BASE_DIR, "mouse_down.png"))
    mouse_left = pygame.image.load(os.path.join(BASE_DIR, "mouse_left.png"))
    mouse_right = pygame.image.load(os.path.join(BASE_DIR, "mouse_right.png"))
    
    # ปรับขนาดรูปภาพให้พอดีกับช่อง
    mouse_up = pygame.transform.scale(mouse_up, (CELL_SIZE, CELL_SIZE))
    mouse_down = pygame.transform.scale(mouse_down, (CELL_SIZE, CELL_SIZE))
    mouse_left = pygame.transform.scale(mouse_left, (CELL_SIZE, CELL_SIZE))
    mouse_right = pygame.transform.scale(mouse_right, (CELL_SIZE, CELL_SIZE))
except pygame.error as e:
    print(f"เกิดข้อผิดพลาดในการโหลดรูปภาพ: {e}")
    print("กรุณาตรวจสอบว่ามีไฟล์รูปหนูทั้ง 4 รูปอยู่ในโฟลเดอร์ 'Mazee' หรือไม่")
    sys.exit()

# --- คลาสสำหรับแต่ละช่อง (Cell) ---
class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self):
        x = self.x * CELL_SIZE
        y = self.y * CELL_SIZE + 50 # ขยับลงมา 50px เพื่อเว้นที่ให้ UI
        
        if self.visited:
            pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE))
            
        if self.walls['top']:
            pygame.draw.line(screen, WHITE, (x, y), (x + CELL_SIZE, y), 2)
        if self.walls['right']:
            pygame.draw.line(screen, WHITE, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls['bottom']:
            pygame.draw.line(screen, WHITE, (x + CELL_SIZE, y + CELL_SIZE), (x, y + CELL_SIZE), 2)
        if self.walls['left']:
            pygame.draw.line(screen, WHITE, (x, y + CELL_SIZE), (x, y), 2)

    def get_unvisited_neighbors(self, grid):
        neighbors = []
        top = grid[self.y - 1][self.x] if self.y > 0 else None
        right = grid[self.y][self.x + 1] if self.x < COLS - 1 else None
        bottom = grid[self.y + 1][self.x] if self.y < ROWS - 1 else None
        left = grid[self.y][self.x - 1] if self.x > 0 else None

        if top and not top.visited: neighbors.append(('top', top))
        if right and not right.visited: neighbors.append(('right', right))
        if bottom and not bottom.visited: neighbors.append(('bottom', bottom))
        if left and not left.visited: neighbors.append(('left', left))
        
        return neighbors

# --- ฟังก์ชันสร้างเขาวงกต (DFS) ---
def generate_maze():
    grid = [[Cell(x, y) for x in range(COLS)] for y in range(ROWS)]
    current = grid[0][0]
    current.visited = True
    stack = [current]

    while stack:
        current = stack[-1]
        neighbors = current.get_unvisited_neighbors(grid)
        
        if neighbors:
            direction, next_cell = random.choice(neighbors)
            # พังกำแพง
            if direction == 'top':
                current.walls['top'] = False
                next_cell.walls['bottom'] = False
            elif direction == 'right':
                current.walls['right'] = False
                next_cell.walls['left'] = False
            elif direction == 'bottom':
                current.walls['bottom'] = False
                next_cell.walls['top'] = False
            elif direction == 'left':
                current.walls['left'] = False
                next_cell.walls['right'] = False
                
            next_cell.visited = True
            stack.append(next_cell)
        else:
            stack.pop()
            
    # เจาะทางเข้า (ตรงกลางซ้าย) และทางออก (ตรงกลางขวา)
    start_y = ROWS // 2
    grid[start_y][0].walls['left'] = False
    grid[start_y][COLS - 1].walls['right'] = False
    
    return grid

# --- ฟังก์ชันค้นหาทางออกที่สั้นที่สุด (BFS) ---
def find_shortest_path(grid, start_x, start_y, end_x, end_y):
    queue = deque([(start_x, start_y, [])])
    visited = set()
    visited.add((start_x, start_y))
    
    while queue:
        x, y, path = queue.popleft()
        current_cell = grid[y][x]
        
        if x == end_x and y == end_y:
            return path + [(x, y)]
            
        # เช็คทิศทางที่ไปได้ (ไม่มีกำแพงและยังไม่เคยไป)
        directions = [
            ('top', x, y - 1),
            ('right', x + 1, y),
            ('bottom', x, y + 1),
            ('left', x - 1, y)
        ]
        
        for dir_name, nx, ny in directions:
            if not current_cell.walls[dir_name]:
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny, path + [(x, y)]))
    return []

# --- ฟังก์ชันวาด Player (หนู) ---
def draw_player(pos, direction):
    x = pos[0] * CELL_SIZE
    y = pos[1] * CELL_SIZE + 50
    
    if direction == 'up':
        screen.blit(mouse_up, (x, y))
    elif direction == 'down':
        screen.blit(mouse_down, (x, y))
    elif direction == 'left':
        screen.blit(mouse_left, (x, y))
    elif direction == 'right':
        screen.blit(mouse_right, (x, y))

# --- ตั้งค่าตัวแปรในเกม ---
grid = generate_maze()
start_pos = (0, ROWS // 2)
end_pos = (COLS - 1, ROWS // 2)
player_pos = list(start_pos)
player_direction = 'right' # ทิศทางเริ่มต้นของหนู

# เวลา
TIME_LIMIT = 180  # 3 นาที (180 วินาที)
start_ticks = pygame.time.get_ticks()

# โหมด
auto_mode = False
auto_path = []
auto_step_delay = 100  # ความเร็วเริ่มต้นในโหมด Auto (มิลลิวินาที/ช่อง)
last_auto_move = pygame.time.get_ticks()

running = True
game_over = False
win = False

while running:
    screen.fill(GRAY)
    
    # --- คำนวณเวลา ---
    seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
    time_left = max(0, TIME_LIMIT - seconds_passed)
    
    if time_left == 0 and not win:
        game_over = True
    
    # --- จัดการ Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN and not game_over:
            # สลับโหมด
            if event.key == pygame.K_SPACE:
                auto_mode = not auto_mode
                if auto_mode:
                    auto_path = find_shortest_path(grid, player_pos[0], player_pos[1], end_pos[0], end_pos[1])
            
            # ปรับความเร็ว Auto Mode (+ / -)
            if auto_mode:
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    auto_step_delay = max(10, auto_step_delay - 30) # เร็วขึ้น
                elif event.key == pygame.K_MINUS:
                    auto_step_delay = min(500, auto_step_delay + 30) # ช้าลง
            
            # ควบคุมเอง (Manual Mode)
            if not auto_mode:
                curr_cell = grid[player_pos[1]][player_pos[0]]
                if event.key == pygame.K_UP and not curr_cell.walls['top']:
                    player_pos[1] -= 1
                    player_direction = 'up'
                elif event.key == pygame.K_RIGHT and not curr_cell.walls['right']:
                    player_pos[0] += 1
                    player_direction = 'right'
                elif event.key == pygame.K_DOWN and not curr_cell.walls['bottom']:
                    player_pos[1] += 1
                    player_direction = 'down'
                elif event.key == pygame.K_LEFT and not curr_cell.walls['left']:
                    if player_pos[0] > 0: # ป้องกันเดินทะลุทางเข้าออกไปนอกจอ
                        player_pos[0] -= 1
                        player_direction = 'left'

    # --- อัปเดต Auto Mode ---
    if auto_mode and not game_over:
        current_time = pygame.time.get_ticks()
        if current_time - last_auto_move > auto_step_delay:
            if auto_path:
                next_pos = auto_path.pop(0)
                # อัปเดตทิศทางของหนูตามการเคลื่อนที่
                if next_pos[0] > player_pos[0]:
                    player_direction = 'right'
                elif next_pos[0] < player_pos[0]:
                    player_direction = 'left'
                elif next_pos[1] > player_pos[1]:
                    player_direction = 'down'
                elif next_pos[1] < player_pos[1]:
                    player_direction = 'up'
                player_pos = list(next_pos)
            last_auto_move = current_time

    # --- เช็คการชนะ ---
    if player_pos[0] == end_pos[0] and player_pos[1] == end_pos[1]:
        win = True
        game_over = True

    # --- วาดกราฟิก ---
    # 1. วาด Maze
    for row in grid:
        for cell in row:
            cell.draw()
            
    # 2. วาดทางเดิน Auto Mode (ระบายสีช่อง)
    if auto_mode and auto_path:
        for px, py in auto_path:
            rect_x = px * CELL_SIZE + 2
            rect_y = py * CELL_SIZE + 50 + 2
            pygame.draw.rect(screen, PATH_COLOR, (rect_x, rect_y, CELL_SIZE-4, CELL_SIZE-4))

    # 3. วาดทางเข้าและทางออก (ไฮไลท์สี)
    pygame.draw.rect(screen, YELLOW, (start_pos[0]*CELL_SIZE+2, start_pos[1]*CELL_SIZE+52, CELL_SIZE-4, CELL_SIZE-4))
    pygame.draw.rect(screen, GREEN, (end_pos[0]*CELL_SIZE+2, end_pos[1]*CELL_SIZE+52, CELL_SIZE-4, CELL_SIZE-4))

    # 4. วาด Player (หนู)
    draw_player(player_pos, player_direction)

    # 5. วาด UI (แถบด้านบน)
    mode_text = "Mode: AUTO (Press SPACE)" if auto_mode else "Mode: MANUAL (Press SPACE)"
    mins, secs = divmod(time_left, 60)
    timer_text = f"Time: {mins:02}:{secs:02}"
    speed_text = f"Speed (Auto): {1000//auto_step_delay} steps/s (+/- to change)" if auto_mode else "Use Arrow Keys to move"
    
    screen.blit(font.render(mode_text, True, YELLOW if auto_mode else WHITE), (10, 5))
    screen.blit(font.render(timer_text, True, RED if time_left < 30 else WHITE), (WIDTH - 120, 5))
    screen.blit(font.render(speed_text, True, WHITE), (10, 25))

    # 6. แจ้งเตือนเมื่อเกมจบ
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0,0))
        
        if win:
            msg = large_font.render("YOU ESCAPED!", True, GREEN)
        else:
            msg = large_font.render("TIME'S UP!", True, RED)
            
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 20))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()