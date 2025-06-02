import pygame
import random
import sys
import os
import math

# 게임 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("용의 화산 슈팅 게임")

# 색상 정의
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
DARK_RED = (150, 0, 0)
BROWN = (139, 69, 19)
DARK_ORANGE = (200, 80, 0)
LIGHT_YELLOW = (255, 255, 150)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)

# 게임 클래스 및 함수
class Player:
    def __init__(self):
        self.width = 60
        self.height = 80
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 6
        self.bullets = []
        self.cooldown = 0
        self.health = 100
        self.score = 0
        self.wing_angle = 0
        self.wing_dir = 1

    def draw(self):
        # 용 몸체 (타원형)
        pygame.draw.ellipse(screen, ORANGE, (self.x, self.y + 15, self.width, self.height - 30))
        
        # 용 머리
        head_radius = 20
        pygame.draw.circle(screen, DARK_ORANGE, (self.x + self.width // 2, self.y + 10), head_radius)
        
        # 용 눈
        eye_radius = 5
        pygame.draw.circle(screen, WHITE, (self.x + self.width // 2 - 8, self.y + 5), eye_radius)
        pygame.draw.circle(screen, WHITE, (self.x + self.width // 2 + 8, self.y + 5), eye_radius)
        
        # 용 눈동자
        pupil_radius = 2
        pygame.draw.circle(screen, BLACK, (self.x + self.width // 2 - 8, self.y + 5), pupil_radius)
        pygame.draw.circle(screen, BLACK, (self.x + self.width // 2 + 8, self.y + 5), pupil_radius)
        
        # 용 뿔
        pygame.draw.polygon(screen, DARK_RED, [
            (self.x + self.width // 2 - 15, self.y + 5),
            (self.x + self.width // 2 - 20, self.y - 15),
            (self.x + self.width // 2 - 10, self.y)
        ])
        pygame.draw.polygon(screen, DARK_RED, [
            (self.x + self.width // 2 + 15, self.y + 5),
            (self.x + self.width // 2 + 20, self.y - 15),
            (self.x + self.width // 2 + 10, self.y)
        ])
        
        # 용 날개 (움직이는 효과)
        self.wing_angle += 0.2 * self.wing_dir
        if self.wing_angle > 20 or self.wing_angle < -20:
            self.wing_dir *= -1
            
        wing_offset = int(math.sin(self.wing_angle * 0.1) * 10)
        
        # 왼쪽 날개
        pygame.draw.polygon(screen, DARK_ORANGE, [
            (self.x, self.y + 30),
            (self.x - 30, self.y + 20 + wing_offset),
            (self.x - 20, self.y + 40),
            (self.x - 40, self.y + 50 + wing_offset),
            (self.x - 10, self.y + 60)
        ])
        
        # 오른쪽 날개
        pygame.draw.polygon(screen, DARK_ORANGE, [
            (self.x + self.width, self.y + 30),
            (self.x + self.width + 30, self.y + 20 + wing_offset),
            (self.x + self.width + 20, self.y + 40),
            (self.x + self.width + 40, self.y + 50 + wing_offset),
            (self.x + self.width + 10, self.y + 60)
        ])
        
        # 용 꼬리
        pygame.draw.polygon(screen, DARK_ORANGE, [
            (self.x + self.width // 2 - 10, self.y + self.height - 15),
            (self.x + self.width // 2, self.y + self.height + 20),
            (self.x + self.width // 2 + 10, self.y + self.height - 15)
        ])
        
        # 불 효과 (입에서 나오는)
        fire_colors = [YELLOW, ORANGE, RED]
        for i in range(3):
            fire_size = 10 - i * 3
            fire_offset = random.randint(-2, 2)
            pygame.draw.circle(screen, fire_colors[i], 
                              (self.x + self.width // 2 + fire_offset, self.y - 5 + i * 3), fire_size)

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += self.speed

    def shoot(self):
        if self.cooldown == 0:
            # 세 방향으로 불꽃 발사
            self.bullets.append(Bullet(self.x + self.width // 2, self.y - 10, 0, -10))
            self.bullets.append(Bullet(self.x + self.width // 2 - 5, self.y - 5, -1, -10))
            self.bullets.append(Bullet(self.x + self.width // 2 + 5, self.y - 5, 1, -10))
            self.cooldown = 15

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        
        # 총알 업데이트
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < 0 or bullet.x < 0 or bullet.x > WIDTH:
                self.bullets.remove(bullet)

class Enemy:
    def __init__(self):
        self.type = random.choice(["rock", "fireball", "spike"])
        self.width = 50 if self.type == "rock" else 45 if self.type == "fireball" else 40
        self.height = 50 if self.type == "rock" else 45 if self.type == "fireball" else 60
        self.x = random.randint(50, WIDTH - 50)
        self.y = -self.height
        self.speed_x = random.randint(-2, 2)
        self.speed_y = random.randint(3, 6)
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        self.health = 2 if self.type == "rock" else 1
        self.color = GRAY if self.type == "rock" else RED if self.type == "fireball" else DARK_RED
        self.animation_offset = 0
        self.animation_dir = 1

    def draw(self):
        # 애니메이션 효과
        self.animation_offset += 0.2 * self.animation_dir
        if abs(self.animation_offset) > 5:
            self.animation_dir *= -1

        if self.type == "rock":
            # 바위 그리기 (더 세밀한 불규칙한 다각형)
            points = []
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            # 더 많은 점으로 더 세밀한 바위 형태 생성
            for i in range(12):
                angle = math.radians(self.rotation + i * 30)
                # 더 불규칙한 형태를 위해 사인 함수 사용
                radius = self.width // 2 * (0.7 + 0.3 * math.sin(i * 1.5 + self.rotation * 0.01))
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.append((x, y))
            
            # 바위 그림자 (더 부드러운 그림자)
            shadow_points = [(p[0] + 4, p[1] + 4) for p in points]
            pygame.draw.polygon(screen, (40, 40, 40), shadow_points)
            
            # 바위 본체 (그라데이션 효과)
            pygame.draw.polygon(screen, self.color, points)
            
            # 바위 하이라이트 (빛 반사 효과)
            highlight_points = []
            for i in range(5):
                angle = math.radians(self.rotation + i * 72 + 30)
                radius = self.width // 2 * 0.6
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                highlight_points.append((x, y))
            
            pygame.draw.polygon(screen, (130, 130, 130), highlight_points)
            
            # 바위 균열 효과 (더 자연스러운 균열)
            crack_points = []
            crack_start = (center_x - self.width // 3, center_y - self.height // 3)
            crack_mid1 = (center_x - self.width // 6 + random.randint(-3, 3), 
                         center_y + random.randint(-3, 3))
            crack_mid2 = (center_x + self.width // 6 + random.randint(-3, 3), 
                         center_y + random.randint(-3, 3))
            crack_end = (center_x + self.width // 3, center_y + self.height // 3)
            
            pygame.draw.line(screen, (50, 50, 50), crack_start, crack_mid1, 2)
            pygame.draw.line(screen, (50, 50, 50), crack_mid1, crack_mid2, 2)
            pygame.draw.line(screen, (50, 50, 50), crack_mid2, crack_end, 2)
            
            # 두 번째 균열
            crack_start = (center_x + self.width // 3, center_y - self.height // 3)
            crack_mid1 = (center_x + self.width // 6 + random.randint(-3, 3), 
                         center_y - self.height // 6 + random.randint(-3, 3))
            crack_mid2 = (center_x - self.width // 6 + random.randint(-3, 3), 
                         center_y + self.height // 6 + random.randint(-3, 3))
            crack_end = (center_x - self.width // 3, center_y + self.height // 3)
            
            pygame.draw.line(screen, (50, 50, 50), crack_start, crack_mid1, 2)
            pygame.draw.line(screen, (50, 50, 50), crack_mid1, crack_mid2, 2)
            pygame.draw.line(screen, (50, 50, 50), crack_mid2, crack_end, 2)
            
            # 바위 질감 표현 (더 자연스러운 돌 질감)
            for _ in range(8):
                x1 = center_x + random.randint(-self.width//3, self.width//3)
                y1 = center_y + random.randint(-self.height//3, self.height//3)
                size = random.randint(2, 5)
                color = (70 + random.randint(-20, 20), 
                         70 + random.randint(-20, 20), 
                         70 + random.randint(-20, 20))
                pygame.draw.circle(screen, color, (x1, y1), size)
                
        elif self.type == "fireball":
            # 불덩이 그리기
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            # 불덩이 그림자
            pygame.draw.circle(screen, (100, 0, 0), 
                              (center_x + 3, center_y + 3), 
                              self.width // 2)
            
            # 불덩이 본체
            pygame.draw.circle(screen, self.color, 
                              (center_x, center_y), 
                              self.width // 2)
            
            # 불꽃 효과 (내부)
            pygame.draw.circle(screen, ORANGE, 
                              (center_x, center_y), 
                              self.width // 3)
            
            pygame.draw.circle(screen, YELLOW, 
                              (center_x, center_y), 
                              self.width // 5)
            
            # 불꽃 파티클
            for _ in range(5):
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(self.width // 3, self.width // 2)
                particle_x = center_x + distance * math.cos(angle)
                particle_y = center_y + distance * math.sin(angle)
                particle_size = random.randint(2, 5)
                pygame.draw.circle(screen, YELLOW, (int(particle_x), int(particle_y)), particle_size)
            
        else:  # spike
            # 가시 그리기 (더 정교하고 세밀한 디자인)
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            # 가시 그림자 (더 부드러운 그림자)
            shadow_points = [
                (center_x + 4, self.y + 4),
                (self.x - 8 + 4, self.y + self.height + 4),
                (self.x + self.width + 8 + 4, self.y + self.height + 4)
            ]
            pygame.draw.polygon(screen, (40, 0, 0), shadow_points)
            
            # 가시 본체 (더 날카로운 형태)
            spike_points = [
                (center_x, self.y),
                (self.x - 8, self.y + self.height),
                (self.x + self.width + 8, self.y + self.height)
            ]
            pygame.draw.polygon(screen, self.color, spike_points)
            
            # 가시 내부 디테일 (여러 층의 삼각형)
            layers = 4
            for i in range(1, layers):
                factor = i / layers
                inner_points = [
                    (center_x, self.y + self.height * factor * 0.7),
                    (center_x - self.width * (1-factor) * 0.7, self.y + self.height - 5 * i),
                    (center_x + self.width * (1-factor) * 0.7, self.y + self.height - 5 * i)
                ]
                layer_color = (180 - i * 20, 0, 0)
                pygame.draw.polygon(screen, layer_color, inner_points)
            
            # 가시 질감 표현 (더 세밀한 선)
            for i in range(-3, 4):
                if i == 0:
                    continue
                line_start = (center_x + i * 5, self.y + abs(i) * 10)
                line_end = (center_x + i * 10, self.y + self.height - 5)
                pygame.draw.line(screen, (150, 0, 0), line_start, line_end, 1)
                
            # 가시 하이라이트 (빛 반사 효과)
            highlight_points = [
                (center_x, self.y + 10),
                (center_x - 5, self.y + 25),
                (center_x + 5, self.y + 25)
            ]
            pygame.draw.polygon(screen, (220, 50, 50), highlight_points)

    def update(self):
        self.y += self.speed_y
        self.x += self.speed_x
        self.rotation += self.rotation_speed
        
        # 화면 경계에서 튕기기
        if self.x <= 0 or self.x >= WIDTH - self.width:
            self.speed_x *= -1
            
        return self.y > HEIGHT  # 화면 아래로 나갔는지 여부 반환

class HealthItem:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = random.randint(50, WIDTH - 50)
        self.y = -self.height
        self.speed_y = random.randint(2, 4)
        self.rotation = 0
        self.rotation_speed = 2
        self.pulse = 0
        self.pulse_dir = 1
        
    def draw(self):
        # 회전 및 맥동 효과
        self.rotation += self.rotation_speed
        self.pulse += 0.1 * self.pulse_dir
        if self.pulse > 1 or self.pulse < 0:
            self.pulse_dir *= -1
            
        pulse_size = int(5 * self.pulse)
        
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # 빛나는 효과 (배경)
        glow_radius = self.width // 2 + pulse_size
        pygame.draw.circle(screen, (255, 255, 200), (center_x, center_y), glow_radius)
        
        # 하트 모양 그리기
        heart_color = (255, 50, 50)
        
        # 하트 윗부분 (두 개의 원)
        circle_radius = self.width // 4
        left_center = (center_x - circle_radius, center_y - circle_radius // 2)
        right_center = (center_x + circle_radius, center_y - circle_radius // 2)
        
        pygame.draw.circle(screen, heart_color, left_center, circle_radius)
        pygame.draw.circle(screen, heart_color, right_center, circle_radius)
        
        # 하트 아랫부분 (삼각형)
        heart_bottom = [
            (center_x - self.width // 2, center_y - circle_radius // 2),
            (center_x + self.width // 2, center_y - circle_radius // 2),
            (center_x, center_y + self.height // 2)
        ]
        pygame.draw.polygon(screen, heart_color, heart_bottom)
        
        # 하트 내부 하이라이트
        pygame.draw.circle(screen, (255, 150, 150), 
                          (left_center[0] + 2, left_center[1] - 2), 
                          circle_radius // 2)
        
    def update(self):
        self.y += self.speed_y
        return self.y > HEIGHT  # 화면 아래로 나갔는지 여부 반환

class Bullet:
    def __init__(self, x, y, dx=0, dy=-10):
        self.x = x
        self.y = y
        self.radius = 8
        self.dx = dx
        self.dy = dy

    def draw(self):
        # 불꽃 효과
        inner_color = (255, 255, 0)  # 노란색 중심
        outer_color = (255, 100, 0)  # 주황색
        
        # 불꽃 효과 (여러 원의 조합)
        pygame.draw.circle(screen, outer_color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), self.radius // 2)
        
        # 불꽃 꼬리 효과
        for i in range(3):
            tail_radius = self.radius - i * 2
            if tail_radius > 0:
                tail_color = (255, max(0, int(200 - i * 70)), 0)
                pygame.draw.circle(screen, tail_color, 
                                 (int(self.x - self.dx * i), int(self.y - self.dy * i)), 
                                 tail_radius)

    def update(self):
        self.x += self.dx
        self.y += self.dy

class Volcano:
    def __init__(self):
        self.particles = []
        for _ in range(80):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.randint(2, 8),
                'speed': random.randint(1, 4),
                'color': (random.randint(200, 255), random.randint(0, 100), 0)
            })
        
        # 화산 형태를 위한 점들
        self.volcano_points = []
        base_width = WIDTH * 0.8
        for x in range(0, WIDTH, 10):
            height_factor = 1 - abs((x - WIDTH/2) / (base_width/2)) ** 2
            if height_factor > 0:
                y = HEIGHT - height_factor * 200
                self.volcano_points.append((x, y))
                
        # 화산 분화구 위치
        self.crater_center = (WIDTH // 2, HEIGHT - 180)
        self.crater_width = 200
        self.crater_height = 60
        
        # 용암 흐름 효과
        self.lava_flows = []
        for _ in range(5):
            self.lava_flows.append({
                'x': self.crater_center[0] + random.randint(-80, 80),
                'y': self.crater_center[1],
                'width': random.randint(10, 30),
                'height': random.randint(100, 200),
                'speed': random.uniform(0.2, 0.5),
                'progress': random.random()
            })

    def draw(self):
        # 배경 하늘 (그라데이션)
        for y in range(HEIGHT):
            # 위에서 아래로 어두워지는 그라데이션
            color_factor = 1 - (y / HEIGHT) * 0.7
            sky_color = (
                int(50 * color_factor), 
                int(50 * color_factor), 
                int(100 * color_factor)
            )
            pygame.draw.line(screen, sky_color, (0, y), (WIDTH, y))
        
        # 화산 그리기
        if len(self.volcano_points) > 2:
            # 화산 내부 (어두운 갈색)
            volcano_points_with_bottom = self.volcano_points + [(WIDTH, HEIGHT), (0, HEIGHT)]
            pygame.draw.polygon(screen, (80, 30, 0), volcano_points_with_bottom)
            
            # 화산 외곽선
            pygame.draw.lines(screen, (50, 20, 0), False, self.volcano_points, 3)
        
        # 화산 분화구
        pygame.draw.ellipse(screen, (50, 20, 0), (
            self.crater_center[0] - self.crater_width // 2,
            self.crater_center[1] - self.crater_height // 2,
            self.crater_width,
            self.crater_height
        ))
        
        # 용암 풀
        pygame.draw.ellipse(screen, (255, 80, 0), (
            self.crater_center[0] - self.crater_width // 2 + 10,
            self.crater_center[1] - self.crater_height // 2 + 10,
            self.crater_width - 20,
            self.crater_height - 20
        ))
        
        # 용암 흐름 효과
        for flow in self.lava_flows:
            flow['progress'] += flow['speed'] * 0.01
            if flow['progress'] > 1:
                flow['progress'] = 0
                flow['x'] = self.crater_center[0] + random.randint(-80, 80)
                
            height = flow['height'] * flow['progress']
            y_pos = flow['y']
            
            # 용암 흐름 그리기 (그라데이션 효과)
            for h in range(int(height)):
                color_factor = 1 - (h / height) * 0.5
                lava_color = (
                    255,
                    int(80 * color_factor),
                    0
                )
                
                width_factor = math.sin(h * 0.05) * 0.3 + 0.7
                current_width = flow['width'] * width_factor
                
                pygame.draw.line(
                    screen, 
                    lava_color, 
                    (flow['x'] - current_width // 2, y_pos + h),
                    (flow['x'] + current_width // 2, y_pos + h)
                )
        
        # 화산재 파티클
        for particle in self.particles:
            pygame.draw.circle(screen, particle['color'], 
                              (int(particle['x']), int(particle['y'])), 
                              particle['size'])

    def update(self):
        for particle in self.particles:
            particle['y'] -= particle['speed']
            if random.random() < 0.02:
                particle['x'] += random.randint(-3, 3)
            
            # 화면 위로 나가면 아래에서 다시 시작
            if particle['y'] < 0:
                particle['y'] = HEIGHT
                particle['x'] = random.randint(0, WIDTH)
                
                # 화산 근처에서 더 많은 파티클 생성
                if random.random() < 0.7:
                    particle['x'] = random.randint(WIDTH // 2 - 200, WIDTH // 2 + 200)

def check_collision(player, enemies, health_items):
    player_rect = pygame.Rect(player.x + 10, player.y + 10, player.width - 20, player.height - 20)
    
    # 총알과 적의 충돌 확인
    for bullet in player.bullets[:]:
        bullet_rect = pygame.Rect(bullet.x - bullet.radius, bullet.y - bullet.radius, 
                                 bullet.radius * 2, bullet.radius * 2)
        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            if bullet_rect.colliderect(enemy_rect):
                if bullet in player.bullets:
                    player.bullets.remove(bullet)
                
                enemy.health -= 1
                if enemy.health <= 0:
                    if enemy in enemies:
                        enemies.remove(enemy)
                        player.score += 10 if enemy.type == "rock" else 5
                break
    
    # 플레이어와 적의 충돌 확인
    for enemy in enemies[:]:
        enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
        if player_rect.colliderect(enemy_rect):
            player.health -= 10 if enemy.type == "rock" else 5
            enemies.remove(enemy)
            return True
            
    # 플레이어와 회복 아이템 충돌 확인
    for item in health_items[:]:
        item_rect = pygame.Rect(item.x, item.y, item.width, item.height)
        if player_rect.colliderect(item_rect):
            player.health = min(100, player.health + 20)  # 체력 20 회복, 최대 100
            health_items.remove(item)
            # 회복 효과음이나 시각 효과를 추가할 수 있음
            
    return False

def draw_health_bar(player):
    pygame.draw.rect(screen, BLACK, (10, 10, 104, 24))
    pygame.draw.rect(screen, RED, (12, 12, player.health, 20))

def draw_score(player):
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"점수: {player.score}", True, WHITE)
    screen.blit(score_text, (WIDTH - 150, 10))

def game_over_screen(player):
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 72)
    game_over_text = font.render("게임 오버", True, RED)
    score_text = font.render(f"최종 점수: {player.score}", True, WHITE)
    restart_text = font.render("R키를 눌러 재시작", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    clock = pygame.time.Clock()
    player = Player()
    enemies = []
    health_items = []
    volcano = Volcano()
    enemy_spawn_timer = 0
    health_item_spawn_timer = 0
    game_over = False
    
    while True:
        if game_over:
            game_over_screen(player)
            # 게임 재시작
            player = Player()
            enemies = []
            health_items = []
            enemy_spawn_timer = 0
            health_item_spawn_timer = 0
            game_over = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        # 배경 및 화산 업데이트 및 그리기
        volcano.update()
        volcano.draw()
        
        # 플레이어 업데이트
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.update()
        
        # 적 생성
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= 40:  # 약 0.7초마다
            enemies.append(Enemy())
            enemy_spawn_timer = 0
            
        # 회복 아이템 생성 (약 10초마다)
        health_item_spawn_timer += 1
        if health_item_spawn_timer >= 600:
            health_items.append(HealthItem())
            health_item_spawn_timer = 0
        
        # 적 업데이트
        for enemy in enemies[:]:
            if enemy.update():
                enemies.remove(enemy)
                
        # 회복 아이템 업데이트
        for item in health_items[:]:
            if item.update():
                health_items.remove(item)
        
        # 충돌 확인
        if check_collision(player, enemies, health_items):
            if player.health <= 0:
                game_over = True
        
        # 그리기
        for enemy in enemies:
            enemy.draw()
            
        for item in health_items:
            item.draw()
        
        for bullet in player.bullets:
            bullet.draw()
        
        player.draw()
        draw_health_bar(player)
        draw_score(player)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
