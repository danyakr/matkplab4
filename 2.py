import pygame
import sys
import random

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

# Размеры персонажа и объектов
PLAYER_SIZE = 50
PLAYER_BORDER_THICKNESS = 2
OBJECT_SIZE = 50
WALL_THICKNESS = 5
ATTACK_SIZE = 100  # Размер зоны атаки

# Скорость движения персонажа
PLAYER_SPEED = 5

# Инициализация окна и часов
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("2D-игра с ближним боем")
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

SPAWN_INTERVAL = 3000  # Интервал в миллисекундах
time_since_last_spawn = 0
show_attack_zone = False  # Флаг показа зоны атаки

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
                player_dx = -PLAYER_SPEED
            elif event.key == pygame.K_RIGHT:
                player_dx = PLAYER_SPEED
            elif event.key == pygame.K_UP:
                player_dy = -PLAYER_SPEED
            elif event.key == pygame.K_DOWN:
                player_dy = PLAYER_SPEED
            elif event.key == pygame.K_SPACE:  # Атака ближнего боя
                attack_zone = pygame.Rect(
                    player_x - (ATTACK_SIZE - PLAYER_SIZE) // 2,
                    player_y - (ATTACK_SIZE - PLAYER_SIZE) // 2,
                    ATTACK_SIZE,
                    ATTACK_SIZE
                )
                objects = [obj for obj in objects if not attack_zone.colliderect(obj)]
                show_attack_zone = True  # Включаем отображение зоны атаки
        elif event.type == pygame.KEYUP:
            if event.key in {pygame.K_LEFT, pygame.K_RIGHT}:
                player_dx = 0
            elif event.key in {pygame.K_UP, pygame.K_DOWN}:
                player_dy = 0

    # Появление нового врага
    if time_since_last_spawn >= SPAWN_INTERVAL:
        spawn_enemy()
        time_since_last_spawn = 0

    # Обновление позиции персонажа
    new_pos_x = player_x + player_dx
    new_pos_y = player_y + player_dy
    player_rect = pygame.Rect(new_pos_x, new_pos_y, PLAYER_SIZE, PLAYER_SIZE)
    if not check_collision_with_objects(player_rect, objects):
        player_x = new_pos_x
        player_y = new_pos_y

    # Ограничение движения персонажа
    player_x = max(WALL_THICKNESS, min(player_x, WINDOW_WIDTH - PLAYER_SIZE - WALL_THICKNESS))
    player_y = max(WALL_THICKNESS, min(player_y, WINDOW_HEIGHT - PLAYER_SIZE - WALL_THICKNESS))

    # Рендеринг объектов
    screen.fill(WHITE)

    # Отрисовка стен
    pygame.draw.rect(screen, BLACK, (0, 0, WINDOW_WIDTH, WALL_THICKNESS))  # Верхняя стена
    pygame.draw.rect(screen, BLACK, (0, 0, WALL_THICKNESS, WINDOW_HEIGHT))  # Левая стена
    pygame.draw.rect(screen, BLACK, (0, WINDOW_HEIGHT - WALL_THICKNESS, WINDOW_WIDTH, WALL_THICKNESS))  # Нижняя стена
    pygame.draw.rect(screen, BLACK, (WINDOW_WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, WINDOW_HEIGHT))  # Правая стена

    # Отрисовка персонажа
    pygame.draw.rect(screen, BLUE, (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE), PLAYER_BORDER_THICKNESS)
    pygame.draw.line(screen, BLUE, (player_x, player_y), (player_x + PLAYER_SIZE, player_y + PLAYER_SIZE), 2)
    pygame.draw.line(screen, BLUE, (player_x + PLAYER_SIZE, player_y), (player_x, player_y + PLAYER_SIZE), 2)

    # Отрисовка врагов
    for obj in objects:
        pygame.draw.rect(screen, RED, obj)

    # Отрисовка зоны атаки
    if show_attack_zone:
        pygame.draw.circle(
            screen,
            RED,
            (player_x + PLAYER_SIZE // 2, player_y + PLAYER_SIZE // 2),  # Центр круга совпадает с центром игрока
            ATTACK_SIZE // 2  # Радиус круга
        )
        show_attack_zone = False

    # Обновление экрана
    pygame.display.flip()
