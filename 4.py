import pygame
import sys
import random
import math

# Инициализация Pygame
pygame.init()

# Параметры окна
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)  # Розовый цвет для хрупких платформ

# Размеры персонажа и объектов
PLAYER_SIZE = 50
PLAYER_BORDER_THICKNESS = 2
OBJECT_SIZE = 50
WALL_THICKNESS = 5
ATTACK_SIZE = 100
PLATFORM_WIDTH = 120
PLATFORM_HEIGHT = 20
FRAGILE_WIDTH = PLAYER_SIZE
TRAP_WIDTH = 25  # Ширина шипа
TRAP_HEIGHT = 20 # Высота шипа

# Скорость движения персонажа и физика
PLAYER_SPEED = 5
JUMP_FORCE = -15
GRAVITY = 1

# Шкала здоровья
MAX_HEALTH = 100
player_health = MAX_HEALTH
# Время мерцания
BLINK_DURATION = 10
player_blink_timer = 0

# Инициализация окна и часов
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("2D-игра с двойным прыжком, ловушками и платформами")
clock = pygame.time.Clock()

# Инициализация персонажа
def get_valid_starting_position(excluded_objects):
    while True:
        x = random.randint(WALL_THICKNESS, WINDOW_WIDTH - PLAYER_SIZE - WALL_THICKNESS)
        y = random.randint(WALL_THICKNESS, WINDOW_HEIGHT - PLAYER_SIZE - WALL_THICKNESS)
        rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        if not any(rect.colliderect(obj) for obj in excluded_objects):
            return [x, y]

player_x, player_y = get_valid_starting_position([])
player_dx = 0
player_dy = 0
is_jumping = False
jumps_left = 2
respawn_position = [player_x, player_y]

# Инициализация неподвижных объектов (врагов)
objects = [
    pygame.Rect(200, 150, OBJECT_SIZE, OBJECT_SIZE),
    pygame.Rect(400, 300, OBJECT_SIZE, OBJECT_SIZE),
    pygame.Rect(600, 450, OBJECT_SIZE, OBJECT_SIZE)
]

# Проверка столкновений персонажа с врагами
def check_collision_with_objects(new_rect, objects):
    return any(new_rect.colliderect(obj) for obj in objects)

# Периодическое появление врагов
def spawn_enemy():
    if len(objects) >= 10:
        return
    while True:
        x = random.randint(WALL_THICKNESS, WINDOW_WIDTH - OBJECT_SIZE - WALL_THICKNESS)
        y = random.randint(WALL_THICKNESS, WINDOW_HEIGHT - OBJECT_SIZE - WALL_THICKNESS)
        new_enemy = pygame.Rect(x, y, OBJECT_SIZE, OBJECT_SIZE)
        if not new_enemy.colliderect(pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)) and \
                not any(new_enemy.colliderect(obj) for obj in objects):
            objects.append(new_enemy)
            break

SPAWN_INTERVAL = 3000
time_since_last_spawn = 0
show_attack_zone = False

# Создание платформ и ловушек
def create_platforms():
    platforms = []
    fragile_platforms = []
    traps = []
    y_offset = 500
    for _ in range(7):
        x_pos = random.randint(WALL_THICKNESS, WINDOW_WIDTH - PLATFORM_WIDTH - WALL_THICKNESS)
        platforms.append(pygame.Rect(x_pos, y_offset, PLATFORM_WIDTH, PLATFORM_HEIGHT))
        if random.choice([True, False]):
            fragile_x = x_pos - FRAGILE_WIDTH
        else:
            fragile_x = x_pos + PLATFORM_WIDTH
        if WALL_THICKNESS <= fragile_x <= WINDOW_WIDTH - FRAGILE_WIDTH - WALL_THICKNESS:
            fragile_platforms.append(pygame.Rect(fragile_x, y_offset, FRAGILE_WIDTH, PLATFORM_HEIGHT))
        trap_x = x_pos + (PLATFORM_WIDTH - TRAP_WIDTH) // 2
        trap_y = y_offset - TRAP_HEIGHT
        traps.append(pygame.Rect(trap_x, trap_y, TRAP_WIDTH, TRAP_HEIGHT))
        y_offset -= 80
    return platforms, fragile_platforms, traps

platforms, fragile_platforms, traps = create_platforms()
fragile_timers = {tuple(p.topleft): 0 for p in fragile_platforms}
fragile_surfaces = {tuple(p.topleft): pygame.Surface((FRAGILE_WIDTH, PLATFORM_HEIGHT), pygame.SRCALPHA) for p in
                    fragile_platforms}
for surf in fragile_surfaces.values():
    surf.fill(PINK)

# Добавляем флаги для управления движением
moving_left = False
moving_right = False

# Основной игровой цикл
running = True
while running:
    delta_time = clock.tick(FPS)
    time_since_last_spawn += delta_time

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left = True
                player_dx = -PLAYER_SPEED
            elif event.key == pygame.K_RIGHT:
                moving_right = True
                player_dx = PLAYER_SPEED
            elif event.key == pygame.K_SPACE and jumps_left > 0:
                player_dy = JUMP_FORCE
                is_jumping = True
                jumps_left -= 1
            elif event.key == pygame.K_LSHIFT:
                attack_zone_center_x = player_x + PLAYER_SIZE // 2
                attack_zone_center_y = player_y + PLAYER_SIZE // 2
                objects = [obj for obj in objects if not math.hypot(attack_zone_center_x - obj.centerx, attack_zone_center_y - obj.centery) <= ATTACK_SIZE // 2]
                show_attack_zone = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
                if not moving_right:
                    player_dx = 0
            elif event.key == pygame.K_RIGHT:
                moving_right = False
                if not moving_left:
                    player_dx = 0

    # Появление нового врага
    if time_since_last_spawn >= SPAWN_INTERVAL:
        spawn_enemy()
        time_since_last_spawn = 0

    # Обновление вертикальной скорости под действием гравитации
    player_dy += GRAVITY

    # Обновление позиции персонажа
    new_pos_x = player_x + player_dx
    new_pos_y = player_y + player_dy

    # Проверка на столкновение с низом экрана
    if new_pos_y + PLAYER_SIZE >= WINDOW_HEIGHT:
        player_y = WINDOW_HEIGHT - PLAYER_SIZE
        player_dy = 0
        is_jumping = False
        jumps_left = 2
    else:
        player_y += player_dy
    # Проверка на столкновения с врагами
    player_rect = pygame.Rect(new_pos_x, new_pos_y, PLAYER_SIZE, PLAYER_SIZE)
    if not check_collision_with_objects(player_rect, objects):
        player_x = new_pos_x

    # Проверка столкновений с платформами
    player_rect = pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)
    on_ground = False
    for platform in platforms:
        if player_rect.colliderect(platform) and player_dy >= 0:
            player_y = platform.top - PLAYER_SIZE
            player_dy = 0
            is_jumping = False
            on_ground = True
            jumps_left = 2
            break

    # Ограничение движения персонажа
    player_x = max(WALL_THICKNESS, min(player_x, WINDOW_WIDTH - PLAYER_SIZE - WALL_THICKNESS))

    # Рендеринг объектов
    screen.fill(WHITE)
    # Шкала здоровья
    pygame.draw.rect(screen, RED, (20, 20, player_health * 2, 20))
    pygame.draw.rect(screen, BLACK, (20, 20, MAX_HEALTH * 2, 20), 2)
    # Отрисовка ловушек (шипов)
    for trap in traps:
       trap_center_x = trap.x + TRAP_WIDTH // 2
       trap_center_y = trap.y + TRAP_HEIGHT // 2
       pygame.draw.polygon(screen, ORANGE, [
           (trap_center_x, trap.y), # Вершина шипа
           (trap.x, trap.y + TRAP_HEIGHT),# левый угол
           (trap.x + TRAP_WIDTH, trap.y + TRAP_HEIGHT)# правый угол
       ])
    # Отрисовка хрупких платформ
    for fragile in fragile_platforms:
        fragile_key = tuple(fragile.topleft)
        screen.blit(fragile_surfaces[fragile_key], fragile)
    # Отрисовка стен
    pygame.draw.rect(screen, BLACK, (0, 0, WINDOW_WIDTH, WALL_THICKNESS))
    pygame.draw.rect(screen, BLACK, (0, 0, WALL_THICKNESS, WINDOW_HEIGHT))
    pygame.draw.rect(screen, BLACK, (0, WINDOW_HEIGHT - WALL_THICKNESS, WINDOW_WIDTH, WALL_THICKNESS))
    pygame.draw.rect(screen, BLACK, (WINDOW_WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, WINDOW_HEIGHT))

    # Отрисовка персонажа
    player_color = BLUE if player_blink_timer % 2 == 0 else WHITE
    pygame.draw.rect(screen, player_color, (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE), PLAYER_BORDER_THICKNESS)
    pygame.draw.line(screen, player_color, (player_x, player_y), (player_x + PLAYER_SIZE, player_y + PLAYER_SIZE), 2)
    pygame.draw.line(screen, player_color, (player_x + PLAYER_SIZE, player_y), (player_x, player_y + PLAYER_SIZE), 2)

    # Отрисовка врагов
    for obj in objects:
        pygame.draw.rect(screen, RED, obj)

    # Отрисовка платформ
    for platform in platforms:
        pygame.draw.rect(screen, GREEN, platform)
    # Отрисовка зоны атаки
    if show_attack_zone:
        attack_zone_center_x = player_x + PLAYER_SIZE // 2
        attack_zone_center_y = player_y + PLAYER_SIZE // 2
        pygame.draw.circle(screen, RED, (attack_zone_center_x, attack_zone_center_y), ATTACK_SIZE // 2)
        show_attack_zone = False

    # Обработка хрупких платформ
    for fragile in fragile_platforms[:]:
        fragile_key = tuple(fragile.topleft)
        if player_rect.colliderect(fragile):
            if player_dy >= 0:
                player_y = fragile.top - PLAYER_SIZE
                player_dy = 0
                is_jumping = False
                on_ground = True
                jumps_left = 2
            fragile_timers[fragile_key] += 1
            alpha = 255 - int((fragile_timers[fragile_key] / (FPS * 2)) * 255)
            if fragile_timers[fragile_key] >= FPS * 2:
                fragile_platforms.remove(fragile)
                del fragile_surfaces[fragile_key]
                del fragile_timers[fragile_key]
            else:
                surface = fragile_surfaces[fragile_key]
                surface.set_alpha(alpha)
                screen.blit(surface, fragile)
        else:
            if fragile_key in fragile_timers and fragile_timers[fragile_key] > 0:
                alpha = 255 - int((fragile_timers[fragile_key] / (FPS * 2)) * 255)
                surface = fragile_surfaces[fragile_key]
                surface.set_alpha(alpha)
                screen.blit(surface, fragile)
    # Проверка на урон от ловушек
    for trap in traps:
        if player_rect.colliderect(trap):
            if player_blink_timer == 0:
                player_health -= 10
                player_blink_timer = BLINK_DURATION
            break
    # Если здоровье закончилось, персонаж возрождается
    if player_health <= 0:
        player_health = MAX_HEALTH
        player_x, player_y = get_valid_starting_position([])
        player_rect = pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)

    # Обновление таймера мигания
    if player_blink_timer > 0:
        player_blink_timer -= 1

    # Обновление экрана
    pygame.display.flip()
    clock.tick(FPS)