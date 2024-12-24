# Практическая работа #4 - Практическая работа #4 - Разработка механик и эффектов в 2D-игре с использованием Pygame

## Цель работы
Освоить реализацию простых механик, эффектов и взаимодействий в 2D-играх с использованием Pygame.

## Задание 1. Базовая заготовка игры

### Описание
Простая 2D-игра с управлением квадратным персонажем, ограниченным стенами, и неподвижными объектами.

### Функционал
*   Управление персонажем клавишами-стрелками.
*   Ограничение движения персонажа стенами.
*   Обработка столкновений персонажа с объектами.
*   Графическое отображение: белый фон, синий квадратный персонаж, красные препятствия, чёрные стены.

## Задание 2. Ближний бой

### Описание изменений
Добавлена механика ближнего боя, позволяющая уничтожать врагов в области атаки.

### Внесённые изменения
*   Создана зона атаки в виде красного круга с радиусом `ATTACK_SIZE`.
*   Центр зоны совпадает с центром игрока.
*   Враги, попадающие в зону атаки, удаляются из списка `objects`.
*   Зона атаки временно отображается на экране при нажатии клавиши `SPACE`.
*   Переменная `show_attack_zone` для управления отображением зоны атаки.

### Результат
Игрок может атаковать врагов в пределах круга нажатием `SPACE`. Отображается красный круг атаки. Враги в зоне атаки уничтожаются.

## Задание 3. Гравитация и прыжки

### Описание
Реализована система гравитации и прыжков для персонажа.

### Подходы и приёмы
1.  Введена переменная вертикальной скорости `player_dy`.
2.  Проверка столкновений персонажа с платформами.
3.  Прыжок реализован с использованием начальной скорости вверх.
4.  Симуляция гравитации через фиксированное изменение `player_dy`.

### Результаты
*   Персонаж может прыгать при наличии платформы.
*   При отсутствии опоры персонаж падает.
*   Реализован ограниченный двойной прыжок.

## Задание 4. Ловушки

### 1.  Исчезающие платформы

#### 1.1. Дизайн
*   Визуальное представление: прямоугольники розового цвета.
*   Механика: при касании платформы становятся прозрачными и исчезают через 2 секунды.
*   Размещение: рядом с обычными платформами.

#### 1.2. Код
*   Данные: список `fragile_platforms`, таймер `fragile_timers`, поверхности `fragile_surfaces`.
*   Таймер для исчезновения.
*   Отрисовка с динамической прозрачностью.
*   Столкновение с проверкой `player_dy >= 0`.

### 2.  Шипы

#### 2.1. Дизайн
*   Визуальное представление: равнобедренные треугольники оранжевого цвета.
*   Механика: при столкновении наносят урон.
*   Размещение: на обычных платформах.

#### 2.2. Код
*   Данные: список `traps` в виде `pygame.Rect`.
*   Урон при столкновении.
*   Отрисовка в виде треугольников.

## Задание 6. Сбор предметов

### 1.  Монеты

#### 1.1. Дизайн
*   Визуальное представление: круги золотого цвета.
*   Механика: при столкновении с персонажем монета исчезает, и счет увеличивается на 10.
*   Размещение: случайным образом, избегая препятствий.
*   Обновление: монеты обновляются при смерти персонажа.

#### 1.2. Код
*   Данные: список `coins` с координатами центров `(coin_x, coin_y)`.
*   Генерация монет.
*   Удаление при сборе.
*   Отрисовка как круги.

### 2.  Система счета
*   Переменная `score` для хранения очков.
*   Увеличение счета при сборе монет.
*   Сброс счета при смерти персонажа.
*   Отрисовка счета на экране.

## Задание 7. Преследование врагами

### 1.1. Дизайн
*   **Механика:** Враги преследуют персонажа.
*   **Предотвращение застревания:** Враги отталкиваются от препятствий.
*  **Размещение:** Случайное.

### 1.2. Код
*   Враги хранятся в списке `objects` как `pygame.Rect`.
*   Вычисляется направление к персонажу.
*   Враги перемещаются в направлении игрока с `ENEMY_SPEED`.
*   Враги отталкиваются от препятствий, и от персонажа.
*   Враги не могут выйти за границы игрового поля.
